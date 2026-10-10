import os
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
os.environ.setdefault('SDL_AUDIODRIVER', 'dummy')
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'main'))
import unittest
from unittest.mock import patch, Mock
from types import SimpleNamespace as NS
from collections import defaultdict
import controls
from controls import CameraInput, InputController, InputState, KeyboardInput
import pygame


class ControlsTests(unittest.TestCase):
    def test_keyboard_never_initializes_camera(self):
        with patch.object(controls, 'CameraInput') as camera:
            c = InputController('keyboard')
            self.assertEqual(c.mode, 'keyboard')
            camera.assert_not_called()

    def test_keyboard_diagonal_speed_and_shoot(self):
        keys = defaultdict(bool, {pygame.K_w: True, pygame.K_d: True, pygame.K_SPACE: True})
        with patch.object(pygame.key, 'get_pressed', return_value=keys):
            state = KeyboardInput().poll()
        self.assertAlmostEqual(sum(v*v for v in state.movement), 1)
        self.assertLess(state.movement[1], 0)
        self.assertTrue(state.shoot)

    def test_startup_failure_falls_back_and_retry_recovers(self):
        camera = Mock()
        with patch.object(controls, 'CameraInput', side_effect=[RuntimeError('unavailable'), camera]):
            c = InputController()
            self.assertEqual(c.mode, 'keyboard')
            self.assertIn('UNAVAILABLE', c.hint)
            c.select_camera()
            self.assertEqual(c.mode, 'camera')
            c.select_keyboard()
            camera.close.assert_called_once()

    def test_midgame_failure_returns_keyboard_input_same_frame(self):
        camera = Mock()
        camera.poll.side_effect = RuntimeError('disconnected')
        with patch.object(controls, 'CameraInput', return_value=camera):
            c = InputController()
        expected = InputState(movement=(1, 0), shoot=True)
        with patch.object(c.keyboard, 'poll', return_value=expected):
            self.assertEqual(c.poll(), expected)
        self.assertEqual(c.mode, 'keyboard')
        camera.close.assert_called_once()

    def test_failed_camera_open_releases_capture(self):
        import cv2
        cap = Mock()
        cap.isOpened.return_value = False
        with patch.object(cv2, 'VideoCapture', return_value=cap):
            with self.assertRaises(RuntimeError):
                CameraInput()
        cap.release.assert_called_once()

    def test_model_initialization_failure_releases_capture(self):
        import cv2, mediapipe as mp
        cap = Mock()
        with patch.object(cv2, 'VideoCapture', return_value=cap), patch.object(mp.solutions.hands, 'Hands', side_effect=RuntimeError('model')):
            with self.assertRaises(RuntimeError):
                CameraInput()
        cap.release.assert_called_once()

    def test_gesture_mapping_and_no_hands(self):
        points = [NS(x=0.0, y=0.0) for _ in range(21)]
        points[8] = NS(x=0.3, y=0.7)
        points[4] = NS(x=0.32, y=0.7)
        hand = NS(landmark=points)
        result = NS(multi_hand_landmarks=[hand, hand], multi_handedness=[NS(classification=[NS(label='Right')]), NS(classification=[NS(label='Left')])])
        state = CameraInput.interpret(result)
        self.assertEqual(state.target, (0.3, 0.7))
        self.assertTrue(state.shoot)
        points[4] = NS(x=0.6, y=0.7)
        self.assertFalse(CameraInput.interpret(result).shoot)
        self.assertEqual(CameraInput.interpret(NS(multi_hand_landmarks=None, multi_handedness=None)), InputState())

    def test_cleanup_is_idempotent(self):
        c = CameraInput.__new__(CameraInput)
        cap, hands = Mock(), Mock()
        c.cap, c.hands, c.preview_open = cap, hands, False
        cap.release.side_effect = RuntimeError('backend')
        c.close(); c.close()
        cap.release.assert_called_once()
        hands.close.assert_called_once()


class GameTests(unittest.TestCase):
    def setUp(self):
        from test import Game
        self.old_dir = Path.cwd()
        os.chdir(Path(__file__).resolve().parents[1] / 'main')
        self.game = Game(input_mode='keyboard')
        self.game.save_highscore = Mock()  # Never change the user's score in tests.

    def tearDown(self):
        self.game.controls.close()
        pygame.quit()
        os.chdir(self.old_dir)

    def test_keyboard_movement_cooldown_and_boundaries(self):
        g = self.game
        start = g.bird_pos.copy()
        with patch.object(g.controls, 'poll', return_value=InputState(movement=(1, -1), shoot=True)):
            g.handle_input()
            self.assertGreater(g.bird_pos[0], start[0])
            self.assertLess(g.bird_pos[1], start[1])
            self.assertEqual(len(g.bullets), 1)
            g.handle_input()
            self.assertEqual(len(g.bullets), 1)
            for _ in range(200): g.handle_input()
        self.assertLessEqual(g.bird_pos[0], g.width // 3 - 30)
        self.assertGreaterEqual(g.bird_pos[1], 30)

    def test_camera_failure_does_not_freeze_timers(self):
        g = self.game
        camera = Mock()
        camera.poll.side_effect = RuntimeError('lost camera')
        g.controls.camera = camera
        g.shooting_delay, g.invincible_timer = 10, 20
        with patch.object(g.controls.keyboard, 'poll', return_value=InputState()):
            g.handle_input()
        self.assertEqual((g.shooting_delay, g.invincible_timer, g.frame_count), (9, 19, 1))
        self.assertEqual(g.controls.mode, 'keyboard')

    def test_real_assets_and_gameplay_states_render(self):
        g = self.game
        g.menu_state.draw()
        with patch.object(g.controls, 'poll', return_value=InputState(shoot=True)):
            for _ in range(120):
                g.handle_input(); g.update(); g.draw()
        for health in [100, 50, 10]:
            g.bird_health = health
            g.draw()
        g.apply_power_up('shield'); g.draw()
        g.game_over = True; g.draw()
        g.reset_game()
        self.assertEqual(g.bird_health, 100)
        self.assertFalse(g.game_over)

    def test_r_replays_through_event_loop_and_accepts_input(self):
        g = self.game
        g.in_menu = False
        g.bird_health = 0
        g.update()
        self.assertTrue(g.game_over)
        g.score, g.level = 500, 4
        g.enemy_spawn_timer, g.power_up_spawn_timer = 40, 800
        g.combo_count, g.combo_timer = 5, 120
        g.milestone_power_up_counter = 1000
        g.time_factor = 0.7
        g.add_recovery_animation(g.bird_pos.copy())
        controller = g.controls
        best = g.highscore
        calls = 0

        def events():
            nonlocal calls
            calls += 1
            if calls == 1:
                return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r)]
            if calls == 2:
                self.assertFalse(g.game_over)
                self.assertEqual((g.bird_health, g.score, g.level), (100, 0, 1))
                self.assertEqual((g.enemy_spawn_timer, g.power_up_spawn_timer,
                                  g.combo_count, g.combo_timer,
                                  g.milestone_power_up_counter), (0, 0, 0, 0, 0))
                self.assertEqual(g.active_animations, [])
                self.assertEqual(g.time_factor, 1.0)
                self.assertIs(g.controls, controller)
                self.assertEqual(g.highscore, best)
                return []
            self.assertGreater(g.bird_pos[0], 100)
            self.assertEqual(len(g.bullets), 1)
            return [pygame.event.Event(pygame.QUIT)]

        with patch.object(pygame.event, 'get', side_effect=events), patch.object(g.controls, 'poll', return_value=InputState(movement=(1, 0), shoot=True)):
            g.run()
        self.assertEqual(calls, 3)

    def test_camera_target_uses_original_smoothing(self):
        g = self.game
        x, y = g.bird_pos
        with patch.object(g.controls, 'poll', return_value=InputState(target=(0.5, 0.25))):
            g.handle_input()
        self.assertAlmostEqual(g.bird_pos[0], x + (133 - x) * 0.15)
        self.assertAlmostEqual(g.bird_pos[1], y + (150 - y) * 0.15)

    def test_switch_keys_reach_controller(self):
        g = self.game
        with patch.object(g.controls, 'select_keyboard') as keyboard, patch.object(g.controls, 'select_camera') as camera:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F2))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F3))
            g.handle_input()
            keyboard.assert_called_once()
            camera.assert_called_once()

    def test_exit_releases_input_resources(self):
        g = self.game
        g.in_menu = False
        camera = Mock()
        g.controls.camera = camera
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        g.run()
        camera.close.assert_called_once()
        camera.poll.assert_not_called()


class LauncherTests(unittest.TestCase):
    def test_root_launcher_from_another_directory(self):
        import runpy
        root = Path(__file__).resolve().parents[1]
        previous = Path.cwd()
        previous_path = sys.path.copy()
        try:
            os.chdir('/private/tmp' if sys.platform == 'darwin' else root.parent)
            caller = Path.cwd()
            with patch.object(sys, 'argv', ['run.py', '--input', 'keyboard']), patch.object(pygame.event, 'get', return_value=[pygame.event.Event(pygame.QUIT)]):
                runpy.run_path(str(root / 'run.py'), run_name='__main__')
            self.assertEqual(Path.cwd(), caller)
            self.assertEqual(sys.path, previous_path)
        finally:
            os.chdir(previous)


if __name__ == '__main__':
    unittest.main()

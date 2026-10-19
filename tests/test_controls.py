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
    @staticmethod
    def open_palm():
        points = [NS(x=0.5, y=0.9) for _ in range(21)]
        for indices, x, top in [((5, 6, 7, 8), 0.4, 0.18),
                                ((9, 10, 11, 12), 0.5, 0.12),
                                ((13, 14, 15, 16), 0.6, 0.18),
                                ((17, 18, 19, 20), 0.7, 0.3)]:
            for index, y in zip(indices, (0.6, 0.45, 0.35, top)):
                points[index] = NS(x=x, y=y)
        for index, x, y in [(1, 0.4, 0.8), (2, 0.3, 0.7),
                             (3, 0.2, 0.6), (4, 0.1, 0.5)]:
            points[index] = NS(x=x, y=y)
        return NS(landmark=points)

    def test_reload_requires_all_five_left_fingers(self):
        hand = self.open_palm()
        result = NS(multi_hand_landmarks=[hand],
                    multi_handedness=[NS(classification=[NS(label='Left')])])
        self.assertTrue(CameraInput.interpret(result).reload)
        self.assertFalse(CameraInput.interpret(result).shoot)
        for tip in (4, 8, 12, 16, 20):
            folded = self.open_palm()
            folded.landmark[tip] = NS(x=0.5, y=0.85)
            self.assertFalse(CameraInput.is_open_hand(folded))
        result.multi_handedness[0].classification[0].label = 'Right'
        self.assertFalse(CameraInput.interpret(result).reload)
        # Rotate the synthetic palm: recognition must not depend on fingers pointing up.
        for point in hand.landmark:
            point.x, point.y = point.y * 0.75, point.x * 4 / 3
        self.assertTrue(CameraInput.is_open_hand(hand))

    def test_keyboard_reload(self):
        with patch.object(pygame.key, 'get_pressed', return_value=defaultdict(bool, {pygame.K_e: True})):
            self.assertTrue(KeyboardInput().poll().reload)

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
    def test_unlimited_keeps_firing_without_reload_or_ammo_hud(self):
        g = self.game
        g.set_ammo_mode('unlimited')
        g.ammo = 0  # Even inherited empty state cannot block unlimited shots.
        with patch.object(g.controls, 'poll', return_value=InputState(shoot=True)):
            for _ in range(500):
                g.handle_input()
        self.assertEqual(len(g.bullets), 25)
        g.update_reload(InputState(reload=True))
        self.assertIsNone(g.reload_started_at)
        with patch.object(g, 'draw_ammo_ui') as ammo_ui:
            g.draw()
        ammo_ui.assert_not_called()
        g.reset_game()
        self.assertEqual(g.ammo_mode, 'unlimited')

    def test_ammo_modes_selectable_from_menu_guide_and_keys(self):
        g = self.game
        g.set_ammo_mode('unlimited')
        limited_rect = g.guide.ammo_buttons(280, compact=True)[1][1]
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=limited_rect.center))
        self.assertIsNone(g.menu_state.handle_input())
        self.assertEqual(g.ammo_mode, 'limited')
        g.ammo, g.reload_started_at, g.reload_progress = 3, 100, 0.5
        g.guide.visible = True
        unlimited_rect = g.guide.ammo_buttons(422)[0][1]
        pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=unlimited_rect.center))
        g.handle_input()
        self.assertEqual((g.ammo_mode, g.ammo, g.reload_started_at, g.reload_progress),
                         ('unlimited', 10, None, 0))
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
        g.handle_input()
        self.assertEqual(g.ammo_mode, 'limited')
        g.reset_game()
        self.assertEqual(g.ammo_mode, 'limited')
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
        g.handle_input()
        self.assertEqual(g.ammo_mode, 'unlimited')

    def test_default_ammo_mode_is_unlimited(self):
        self.assertEqual(self.default_ammo_mode, 'unlimited')

    def test_held_fire_stops_at_empty_and_cannot_spend_powerups(self):
        g = self.game
        with patch.object(g.controls, 'poll', return_value=InputState(shoot=True)), patch.object(g, 'play_single_sound') as sound:
            for _ in range(500):
                g.handle_input()
        self.assertEqual((g.ammo, len(g.bullets)), (0, 10))
        self.assertEqual(sound.call_count, 10)
        g.effects['triple_shot']['uses'] = 3
        self.assertFalse(g.fire_bullet())
        self.assertEqual(g.effects['triple_shot']['uses'], 3)

    def test_reload_hold_cancels_and_rearms_shooting(self):
        g = self.game
        g.ammo = 0
        with patch.object(g.controls, 'poll', return_value=InputState(reload=True)), patch.object(pygame.time, 'get_ticks', side_effect=[100, 599]):
            g.handle_input(); g.handle_input()
        self.assertEqual(g.ammo, 0)
        self.assertGreater(g.reload_progress, 0.9)
        with patch.object(g.controls, 'poll', return_value=InputState()):
            g.handle_input()
        self.assertEqual(g.reload_progress, 0)
        with patch.object(g.controls, 'poll', return_value=InputState(reload=True)), patch.object(pygame.time, 'get_ticks', side_effect=[600, 1100]):
            g.handle_input(); g.draw(); g.handle_input()
        self.assertEqual((g.ammo, len(g.bullets)), (10, 0))
        with patch.object(g.controls, 'poll', return_value=InputState(shoot=True)):
            g.handle_input()
        self.assertEqual((g.ammo, len(g.bullets)), (9, 1))

    def test_reload_partial_magazines_but_not_full_and_guide_cancels_hold(self):
        g = self.game
        for rounds in (0, 3, 9):
            with self.subTest(rounds=rounds):
                g.ammo = rounds
                g.reload_started_at = None
                with patch.object(pygame.time, 'get_ticks', side_effect=[100, 600]):
                    g.update_reload(InputState(reload=True))
                    self.assertEqual(g.ammo, rounds)
                    g.update_reload(InputState(reload=True))
                self.assertEqual(g.ammo, 10)
        g.update_reload(InputState(reload=True))
        self.assertEqual(g.ammo, 10)
        self.assertIsNone(g.reload_started_at)
        g.ammo = 0
        g.update_reload(InputState(reload=True))
        g.update_reload(InputState(shoot=True, reload=True))
        self.assertIsNone(g.reload_started_at)
        g.update_reload(InputState(reload=True))
        g.guide.visible = True
        g.handle_input()
        self.assertIsNone(g.reload_started_at)

    def test_powered_volley_spends_one_round_and_replay_refills(self):
        g = self.game
        g.effects['split_shot']['uses'] = 2
        self.assertTrue(g.fire_bullet())
        self.assertEqual((g.ammo, len(g.bullets), g.effects['split_shot']['uses']), (9, 5, 1))
        g.ammo = 0
        g.update_reload(InputState(reload=True))
        g.reset_game()
        self.assertEqual(g.ammo, 10)
        self.assertIsNone(g.reload_started_at)
        self.assertEqual(g.reload_progress, 0)

    def setUp(self):
        from test import Game
        self.old_dir = Path.cwd()
        os.chdir(Path(__file__).resolve().parents[1] / 'main')
        self.game = Game(input_mode='keyboard')
        self.default_ammo_mode = self.game.ammo_mode
        self.game.set_ammo_mode('limited')
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

    def test_guide_pauses_input_and_supports_clickable_modes(self):
        g = self.game
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_h))
        with patch.object(g.controls, 'poll') as poll:
            g.handle_input()
            self.assertTrue(g.guide.visible)
            poll.assert_not_called()
        with patch.object(g.controls, 'select_camera') as camera:
            pygame.event.post(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=g.guide.camera_button.center))
            g.handle_input()
            camera.assert_called_once()
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))
        g.handle_input()
        self.assertFalse(g.guide.visible)
        self.assertTrue(g.running)

    def test_mac_letter_shortcuts(self):
        g = self.game
        with patch.object(g.controls, 'select_keyboard') as keyboard, patch.object(g.controls, 'select_camera') as camera:
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_k))
            pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_c))
            g.handle_input()
            keyboard.assert_called_once()
            camera.assert_called_once()

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

"""Input adapters: produce intentions without changing game state."""
from dataclasses import dataclass
import math
import pygame


@dataclass(frozen=True)
class InputState:
    movement: tuple = (0.0, 0.0)
    target: tuple | None = None
    shoot: bool = False
    reload: bool = False


class KeyboardInput:
    def poll(self):
        keys = pygame.key.get_pressed()
        dx = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        dy = int(keys[pygame.K_s] or keys[pygame.K_DOWN]) - int(keys[pygame.K_w] or keys[pygame.K_UP])
        length = math.hypot(dx, dy)
        movement = (dx / length, dy / length) if length else (0.0, 0.0)
        return InputState(movement=movement, shoot=bool(keys[pygame.K_SPACE]),
                          reload=bool(keys[pygame.K_e]))


class CameraInput:
    def __init__(self, camera_index=0):
        self.cap = None
        self.hands = None
        self.cv2 = None
        self.preview_open = False
        self.frame_count = 0
        try:
            # Keyboard mode does not import or initialize camera dependencies.
            import cv2
            import mediapipe as mp
            self.cv2 = cv2
            self.cap = cv2.VideoCapture(camera_index)
            if not self.cap.isOpened():
                raise RuntimeError(f"Camera {camera_index} is unavailable")
            self.mp_hands = mp.solutions.hands
            self.mp_draw = mp.solutions.drawing_utils
            self.hands = self.mp_hands.Hands(
                max_num_hands=2, min_detection_confidence=0.5,
                min_tracking_confidence=0.5, model_complexity=0)
        except Exception:
            self.close()
            raise

    @staticmethod
    def is_open_hand(landmarks):
        # Joint angles and palm-relative distances also work when the hand rotates.
        points = [(p.x * 4 / 3, p.y) for p in landmarks.landmark]

        def distance(a, b):
            return math.dist(points[a], points[b])

        def straight(a, b, c):
            u = (points[a][0] - points[b][0], points[a][1] - points[b][1])
            v = (points[c][0] - points[b][0], points[c][1] - points[b][1])
            length = math.hypot(*u) * math.hypot(*v)
            return length > 1e-8 and (u[0] * v[0] + u[1] * v[1]) / length < -0.86

        palm = distance(5, 17)
        if palm < 1e-6:
            return False
        fingers_open = all(straight(base, pip, dip) and straight(pip, dip, tip)
                           and distance(0, tip) > distance(0, pip) + palm * 0.2
                           for base, pip, dip, tip in [(5, 6, 7, 8), (9, 10, 11, 12),
                                                      (13, 14, 15, 16), (17, 18, 19, 20)])
        return (fingers_open and straight(1, 2, 3) and straight(2, 3, 4)
                and distance(4, 5) > palm * 0.6 and distance(4, 8) > palm * 0.6)

    @staticmethod
    def interpret(results):
        target, shoot, reload = None, False, False
        for landmarks, handedness in zip(results.multi_hand_landmarks or [],
                                         results.multi_handedness or []):
            tip = landmarks.landmark[8]
            if handedness.classification[0].label == 'Right':
                target = (tip.x, tip.y)
            elif handedness.classification[0].label == 'Left':
                thumb = landmarks.landmark[4]
                shoot = shoot or math.hypot(thumb.x - tip.x, thumb.y - tip.y) < 0.05
                reload = reload or CameraInput.is_open_hand(landmarks)
        return InputState(target=target, shoot=shoot, reload=reload and not shoot)

    def poll(self):
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("Camera stopped delivering frames")
        frame = self.cv2.resize(self.cv2.flip(frame, 1), (320, 240))
        results = self.hands.process(self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB))
        self.frame_count += 1
        if self.frame_count % 2 == 0:
            for landmarks in results.multi_hand_landmarks or []:
                self.mp_draw.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
            self.preview_open = True
            self.cv2.imshow('Hand Tracking', frame)
            self.cv2.waitKey(1)
        return self.interpret(results)

    def close(self):
        # Each resource is independent; a backend cleanup failure must not
        # prevent releasing the remaining resources or keyboard fallback.
        for attr, method in [('cap', 'release'), ('hands', 'close')]:
            resource = getattr(self, attr)
            setattr(self, attr, None)
            if resource is not None:
                try:
                    getattr(resource, method)()
                except Exception:
                    pass
        if self.preview_open:
            self.preview_open = False
            try:
                self.cv2.destroyWindow('Hand Tracking')
            except Exception:
                pass


class InputController:
    def __init__(self, mode='auto', camera_index=0):
        if mode not in ('auto', 'camera', 'keyboard'):
            raise ValueError(f"Unknown input mode: {mode}")
        self.keyboard = KeyboardInput()
        self.camera = None
        self.camera_index = camera_index
        self.notice = ''
        if mode != 'keyboard':
            self.select_camera()

    @property
    def mode(self):
        return 'camera' if self.camera is not None else 'keyboard'

    @property
    def hint(self):
        if self.camera is not None:
            return 'CAMERA | K: keyboard | C: retry | ESC: quit'
        prefix = 'CAMERA UNAVAILABLE | ' if self.notice else ''
        return prefix + 'WASD/Arrows: move | SPACE: fire | E: reload | C: camera'

    def select_keyboard(self):
        self.close()
        self.notice = ''

    def select_camera(self):
        self.close()
        try:
            self.camera = CameraInput(self.camera_index)
            self.notice = ''
        except Exception as exc:
            self.notice = str(exc)
            print(f'{exc}. Using keyboard: WASD/Arrows + Space. Return HOME to retry camera.')

    def poll(self):
        if self.camera is not None:
            try:
                return self.camera.poll()
            except Exception as exc:
                self.close()
                self.notice = str(exc)
                print(f'{exc}. Switched to keyboard: WASD/Arrows + Space.')
        return self.keyboard.poll()

    def close(self):
        if self.camera is not None:
            self.camera.close()
            self.camera = None

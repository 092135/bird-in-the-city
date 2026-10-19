"""In-game controls guide, shared by the menu and paused gameplay."""
import pygame


class ControlsGuide:
    def __init__(self):
        self.visible = False
        self.help_button = pygame.Rect(662, 575, 130, 25)
        self.keyboard_button = pygame.Rect(64, 470, 210, 44)
        self.camera_button = pygame.Rect(294, 470, 210, 44)
        self.close_button = pygame.Rect(524, 470, 210, 44)

    def handle_event(self, event, controls):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_h:
                self.visible = not self.visible
                return True
            if self.visible and event.key == pygame.K_ESCAPE:
                self.visible = False
                return True
            if event.key in (pygame.K_k, pygame.K_F2):
                controls.select_keyboard()
                return True
            if event.key in (pygame.K_c, pygame.K_F3):
                controls.select_camera()
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.visible:
                if self.keyboard_button.collidepoint(event.pos):
                    controls.select_keyboard()
                elif self.camera_button.collidepoint(event.pos):
                    controls.select_camera()
                elif self.close_button.collidepoint(event.pos):
                    self.visible = False
                return True
            if self.help_button.collidepoint(event.pos):
                self.visible = True
                return True
        return self.visible and event.type != pygame.QUIT

    @staticmethod
    def text(screen, text, pos, size=24, color=(255, 244, 230)):
        screen.blit(pygame.font.Font(None, size).render(text, True, color), pos)

    def draw(self, screen, controls):
        pygame.draw.rect(screen, (35, 27, 24), (0, 575, 800, 25))
        self.text(screen, controls.hint, (8, 581), 19)
        pygame.draw.rect(screen, (143, 86, 59), self.help_button)
        self.text(screen, 'GUIDE [H]', (687, 580), 22)
        if not self.visible:
            return
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 190))
        screen.blit(shade, (0, 0))
        pygame.draw.rect(screen, (43, 34, 29), (40, 50, 720, 500))
        pygame.draw.rect(screen, (179, 107, 73), (40, 50, 720, 500), 3)
        self.text(screen, 'HOW TO PLAY', (64, 72), 38)
        self.text(screen, 'Game paused while this guide is open.', (64, 114), 22)
        self.text(screen, 'CAMERA  /  press C or click Use camera', (64, 155), 28, (255, 204, 120))
        lines = [
            'Allow camera access. Keep both hands visible and well lit.',
            'Right index finger: move the bird. Left thumb + index pinch: shoot.',
            '10 rounds. When empty, open LEFT hand for 0.5s to reload.',
            'No camera? The game switches to keyboard controls.',
        ]
        for i, line in enumerate(lines):
            self.text(screen, line, (64, 190 + i * 25), 23)
        self.text(screen, 'KEYBOARD  /  press K or click Use keyboard', (64, 306), 28, (255, 204, 120))
        self.text(screen, 'WASD/Arrows: move. SPACE: shoot. Empty? Hold E for 0.5s.', (64, 342), 23)
        self.text(screen, 'After game over: click the game window, then R to replay.', (64, 372), 23)
        self.text(screen, 'H: guide / resume. ESC: close guide, or quit during play.', (64, 402), 23)
        status = 'CAMERA UNAVAILABLE - keyboard active' if controls.notice else controls.mode.upper() + ' active'
        self.text(screen, status, (64, 438), 23, (166, 220, 160))
        for rect, label in [(self.keyboard_button, 'Use keyboard [K]'),
                            (self.camera_button, 'Use camera [C]'),
                            (self.close_button, 'Back to game [H]')]:
            pygame.draw.rect(screen, (143, 86, 59), rect)
            self.text(screen, label, (rect.x + 13, rect.y + 13), 24)

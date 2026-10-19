"""Contextual instructions and navigation; round settings stay locked."""
import pygame


class ControlsGuide:
    def __init__(self, game):
        self.game = game
        self.visible = False
        self.onboarding = False
        self.home_button = pygame.Rect(544, 575, 110, 25)
        self.help_button = pygame.Rect(662, 575, 130, 25)
        self.close_button = pygame.Rect(414, 470, 290, 46)
        self.panel_home = pygame.Rect(96, 470, 290, 46)

    def handle_event(self, event, controls):
        locked = self.game.round_locked
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.visible and not self.onboarding:
                    self.visible = False
                elif not self.game.in_menu:
                    self.game.return_home()
                else:
                    return False
                return True
            if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.visible:
                self.visible = self.onboarding = False
                return True
            if event.key == pygame.K_h:
                self.visible = not self.visible
                self.onboarding = False
                return True
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_k, pygame.K_c,
                             pygame.K_F2, pygame.K_F3):
                if not locked and not self.visible:
                    if event.key in (pygame.K_k, pygame.K_F2):
                        self.game.select_input('keyboard')
                    elif event.key in (pygame.K_c, pygame.K_F3):
                        self.game.select_input('camera')
                return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.visible:
                if self.panel_home.collidepoint(event.pos):
                    self.game.return_home()
                elif self.close_button.collidepoint(event.pos):
                    self.visible = self.onboarding = False
                return True
            if not self.game.in_menu and self.home_button.collidepoint(event.pos):
                self.game.return_home()
                return True
            if not self.game.in_menu and self.help_button.collidepoint(event.pos):
                self.visible = True
                return True
        return self.visible

    @staticmethod
    def text(screen, text, pos, size=24, color=(255, 244, 230)):
        screen.blit(pygame.font.Font(None, size).render(text, True, color), pos)

    def draw(self, screen, controls):
        pygame.draw.rect(screen, (35, 27, 24), (0, 575, 800, 25))
        if self.game.in_menu:
            hint = 'Choose controls and ammo after PLAY. ESC: back.'
        elif controls.mode == 'camera':
            hint = 'CAMERA | Right hand: move | Left pinch: fire'
        else:
            hint = 'KEYBOARD | WASD/Arrows: move | SPACE: fire'
            if self.game.ammo_mode == 'limited':
                hint += ' | E: reload'
        self.text(screen, hint, (8, 581), 18)
        if not self.game.in_menu:
            for rect, label in [(self.home_button, 'HOME [ESC]'), (self.help_button, 'GUIDE [H]')]:
                pygame.draw.rect(screen, (143, 86, 59), rect)
                self.text(screen, label, (rect.x + 12, 581), 20)
        if not self.visible:
            return
        shade = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 180))
        screen.blit(shade, (0, 0))
        pygame.draw.rect(screen, (43, 34, 29), (64, 90, 672, 450))
        pygame.draw.rect(screen, (179, 107, 73), (64, 90, 672, 450), 3)
        self.text(screen, 'READY TO FLY?' if self.onboarding else 'HOW TO PLAY', (96, 115), 38)
        ammo = 'UNLIMITED AMMO' if self.game.ammo_mode == 'unlimited' else '10-ROUND MAGAZINE'
        self.text(screen, controls.mode.upper() + '  /  ' + ammo, (96, 166), 26, (255, 204, 120))
        if controls.mode == 'camera':
            lines = ['Keep both hands visible and well lit.',
                     'RIGHT index finger: move the bird.',
                     'LEFT thumb + index pinch: shoot.',
                     ('Open your LEFT hand for 0.5s to reload.' if self.game.ammo_mode == 'limited'
                      else 'Hold the pinch to keep firing. No reload needed.')]
        else:
            lines = ['Click the game window to focus the controls.',
                     'WASD or arrow keys: move the bird.',
                     'Hold SPACE: shoot.',
                     ('Hold E for 0.5s to reload anytime.' if self.game.ammo_mode == 'limited'
                      else 'Unlimited ammo. No reload needed.')]
        for i, line in enumerate(lines):
            self.text(screen, line, (96, 217 + i * 36), 27)
        if controls.notice:
            self.text(screen, 'Camera unavailable: keyboard fallback is active.', (96, 370), 23, (255, 204, 120))
        else:
            self.text(screen, 'After game over: R to replay this mode.', (96, 370), 24)
        self.text(screen, 'To change modes, return HOME. No switching mid-round.', (96, 404), 23)
        for rect, label in [(self.panel_home, 'HOME'),
                            (self.close_button, 'START [ENTER]' if self.onboarding else 'RESUME [ENTER]')]:
            pygame.draw.rect(screen, (143, 86, 59), rect)
            font = pygame.font.Font(None, 28)
            text = font.render(label, True, (255, 244, 230))
            screen.blit(text, text.get_rect(center=rect.center))

import pygame
import cv2
import mediapipe as mp
import numpy as np
import random
from pygame.locals import *
import os

class GameConfig:
    # Window settings
    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 60
    
    # Player settings
    BIRD_START_HEALTH = 100
    BIRD_SIZE = 15
    BIRD_START_POS = [100, WINDOW_HEIGHT//2]
    
    # Combat settings
    SHOOTING_DELAY = 20
    RAPID_FIRE_DELAY = 10
    INVINCIBILITY_DURATION = 90
    
    # Power up settings
    SHIELD_DURATION = 0
    RAPID_FIRE_DURATION = 0
    TRIPLE_SHOT_USES = 0
    SPLIT_SHOT_USES = 0
    
    # Enemy settings
    DAMAGE_VALUES = {
        'normal': 10,
        'fast': 15,
        'large': 20
    }
    
    # Asset paths
    ASSETS = {
        'game_over': 'Animation/Effects/GameOver.PNG',
        'shield': 'Animation/Effects/Shield.PNG',
        'bullet': 'Animation/Effects/Bullet.PNG',
        'bird_healthy': 'Animation/Bird/Healthy/Healthy{}.PNG',
        'bird_slight_damage': 'Animation/Bird/Slight_Damage/SlightDamage{}.PNG',
        'bird_heavily_damaged': 'Animation/Bird/Heavily_Damaged/HeavilyDamaged{}.PNG',
        'menu': 'Animation/Effects/GameMenu.PNG',
        'intro': 'Animation/Effects/Introduction.PNG'
    }

    POLLUTION_ASSETS = {
        'normal': [
            'Animation/Effects/Glass.PNG',  # 更改为新的玻璃图片
            'Animation/Effects/Glass.PNG',
            'Animation/Effects/Glass.PNG'
        ],
        'fast': [
            'Animation/Effects/Pollution/Pollution1_1.PNG',
            'Animation/Effects/Pollution/Pollution1_2.PNG',
            'Animation/Effects/Pollution/Pollution1_3.PNG'
        ],
        'large': [
            'Animation/Effects/Boss.PNG',  # 更改为新的Boss图片
            'Animation/Effects/Boss.PNG',
            'Animation/Effects/Boss.PNG'
        ]
    }
    
    RECOVERY_ANIMATION = [
        'Animation/Effects/Recovery/Recovery1.PNG',
        'Animation/Effects/Recovery/Recovery2.PNG',
        'Animation/Effects/Recovery/Recovery3.PNG'
    ]

    IMPACT_ANIMATION = [
        'Animation/Effects/Impact/Impact1.PNG',
        'Animation/Effects/Impact/Impact2.PNG',
        'Animation/Effects/Impact/Impact3.PNG',
        'Animation/Effects/Impact/Impact4.PNG'
    ]

    BACKGROUNDS = {
        'healthy': 'Animation/Effects/Healthy_Background.PNG',
        'slight_damage': 'Animation/Effects/Slightly_Damaged_Background.PNG',
        'heavily_damaged': 'Animation/Effects/Heavily_Damaged_Background.PNG'
    }

    POWER_UP_ICONS = {
        'health': 'Animation/Effects/Recovery_Icon.PNG',
        'rapid_fire': 'Animation/Effects/Rapid_Shot_Icon.PNG',
        'split_shot': 'Animation/Effects/Spread_Shot_Icon.PNG',
        'triple_shot': 'Animation/Effects/Triple_Shot_Icon.PNG',
        'shield': 'Animation/Effects/Shield_Icon.PNG'
    }

    BULLET_TYPES = {
        'split_shot': 'Animation/Effects/Spread_Shot.PNG',
        'rapid_fire': 'Animation/Effects/Rapid_Shot.PNG',
        'triple_shot': 'Animation/Effects/Triple_Shot.PNG'
    }

    SOUND_TYPES = {
        'background_music': 'sfx/background_music.wav',
        'game_over': 'sfx/game_over.wav',
        'button_click': 'sfx/button_click.wav',
        'single_shot': 'sfx/single_shot.wav',
        'multi_shot': 'sfx/multi_shot.wav',
        'collect_tools': 'sfx/collect_tools.wav',
        'level_up': 'sfx/level_up.wav',
        'get_hurt': 'sfx/get_hurt.wav',
        'hit_pollution': 'sfx/hit_pollution.wav',
        'shield_loop': 'sfx/shield_loop.wav',
        'health_recovery': 'sfx/health_recovery.wav'
    }

    # 新添加的Scoring settings
    BASE_SCORES = {
        'normal': 10,
        'fast': 15,
        'large': 20
    }
    COMBO_MULTIPLIER = 0.1  # 10% bonus per combo
    MAX_COMBO_MULTIPLIER = 2.0  # Maximum 2x score multiplier
    
    # 新添加的Level progression
    BASE_LEVEL_SCORE = 200  # Base score needed for first level
    LEVEL_SCORE_MULTIPLIER = 1.2  # Each level requires 20% more score
    
    # 新添加的Enhanced enemy settings
    MAX_SPEED = {
        'normal': 7,
        'fast': 10,
        'large': 4
    }
    MIN_SPAWN_INTERVAL = 30
    SPEED_INCREASE_PER_LEVEL = 0.05  # 5% speed increase per level
    
    # 新添加的Enhanced power up settings
    POWER_UP_BASE_INTERVAL = 900
    POWER_UP_INTERVAL_DECREASE = 10
    MIN_POWER_UP_INTERVAL = 400
    LOW_HEALTH_BONUS_CHANCE = 0.2
    LOW_HEALTH_THRESHOLD = 30  

    # 新添加的Enhanced defense settings
    BASE_INVINCIBILITY_TIME = 90
    INVINCIBILITY_INCREASE_PER_LEVEL = 3
    MAX_INVINCIBILITY_TIME = 150

    HIGHSCORE_FILE = "highscore.txt"

class MenuState:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.running = True
        self.current_state = 'menu'  # 'menu' or 'intro'
        
        # Load menu backgrounds
        self.menu_bg = self.load_image('Animation/Effects/GameMenu.PNG', 
                                     (self.game.width, self.game.height))
        self.intro_bg = self.load_image('Animation/Effects/Introduction.PNG',
                                      (self.game.width, self.game.height))
        
        # 增大按钮尺寸
        button_width = 250  # 从180增加到250
        button_height = 60  # 从40增加到60
        spacing = 40       # 从30增加到40
        start_y = self.game.height // 2 + 50  # 稍微上移以适应更大的按钮
        
        self.buttons = {
            'play': pygame.Rect((self.game.width - button_width) // 2,
                              start_y - button_height - spacing,
                              button_width, button_height),
            'intro': pygame.Rect((self.game.width - button_width) // 2,
                               start_y,
                               button_width, button_height),
            'quit': pygame.Rect((self.game.width - button_width) // 2,
                              start_y + button_height + spacing,
                              button_width, button_height),
            'back': pygame.Rect(50, self.game.height - 100,
                              button_width, button_height)
        }
        
        # 像素风格的配色方案
        self.button_colors = {
            'normal': {
                'fill': (82, 54, 41),      # 深棕色填充
                'light': (143, 86, 59),    # 亮边框
                'dark': (51, 34, 26)       # 暗边框
            },
            'hover': {
                'fill': (143, 86, 59),     # 亮棕色填充
                'light': (179, 107, 73),   # 更亮的边框
                'dark': (82, 54, 41)       # 深边框
            },
            'text': (255, 244, 230)        # 暖白色文字
        }
        
        # 使用相对路径加载字体，增大字号
        try:
            self.font = pygame.font.Font('font/press_start_2p.ttf', 24)  # 从16增加到24
        except:
            print("Pixel font not found, using default font")
            self.font = pygame.font.Font(None, 48)  # 相应增加默认字体大小

    def draw_pixel_button(self, rect, color_scheme, text):
        """Draw a pixel art style button"""
        # 主体填充
        pygame.draw.rect(self.screen, color_scheme['fill'], rect)
        
        # 像素风格的边框，增加边框宽度
        pixel_size = 3  # 从2增加到3
        
        # 上边和左边（亮边框）
        pygame.draw.rect(self.screen, color_scheme['light'],
                        (rect.left, rect.top, rect.width, pixel_size))
        pygame.draw.rect(self.screen, color_scheme['light'],
                        (rect.left, rect.top, pixel_size, rect.height))
        
        # 下边和右边（暗边框）
        pygame.draw.rect(self.screen, color_scheme['dark'],
                        (rect.left, rect.bottom - pixel_size, rect.width, pixel_size))
        pygame.draw.rect(self.screen, color_scheme['dark'],
                        (rect.right - pixel_size, rect.top, pixel_size, rect.height))
        
        # 渲染文字
        text_surface = self.font.render(text, True, self.button_colors['text'])
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)

    def load_image(self, path, size=None):
        return self.game.load_image(path, size)

    def handle_input(self):
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == QUIT:
                return 'quit'
            elif event.type == MOUSEBUTTONDOWN:
                mouse_clicked = True
                
        # Handle menu state
        if self.current_state == 'menu':
            for button_name, button_rect in self.buttons.items():
                if button_name != 'back':  # Don't show back button in main menu
                    if button_rect.collidepoint(mouse_pos):
                        if mouse_clicked:
                            if button_name == 'play':
                                return 'play'
                            elif button_name == 'intro':
                                self.current_state = 'intro'
                            elif button_name == 'quit':
                                return 'quit'
        
        # Handle intro state
        elif self.current_state == 'intro':
            if self.buttons['back'].collidepoint(mouse_pos):
                if mouse_clicked:
                    self.current_state = 'menu'
                    
        return None

    def draw(self):
        # Draw background based on current state
        if self.current_state == 'menu':
            self.screen.blit(self.menu_bg, (0, 0))
        else:  # intro state
            self.screen.blit(self.intro_bg, (0, 0))
            
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw buttons based on current state
        if self.current_state == 'menu':
            button_labels = {'play': 'PLAY', 'intro': 'INTRO', 'quit': 'QUIT'}
            for button_name, button_rect in self.buttons.items():
                if button_name != 'back':
                    is_hovered = button_rect.collidepoint(mouse_pos)
                    color_scheme = self.button_colors['hover' if is_hovered else 'normal']
                    self.draw_pixel_button(button_rect, color_scheme, button_labels[button_name])
        
        # Draw back button in intro state
        elif self.current_state == 'intro':
            back_rect = self.buttons['back']
            is_hovered = back_rect.collidepoint(mouse_pos)
            color_scheme = self.button_colors['hover' if is_hovered else 'normal']
            self.draw_pixel_button(back_rect, color_scheme, 'BACK')
            
        pygame.display.flip()

    def run(self):
        while self.running:
            action = self.handle_input()
            
            if action == 'quit':
                return False
            elif action == 'play':
                return True
                
            self.draw()
            self.clock.tick(60)

class Game:
    def __init__(self):
        pygame.init()
        self.width = GameConfig.WINDOW_WIDTH
        self.height = GameConfig.WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Environmental Awareness")
        self.highscore = self.load_highscore()

        self.running = True
        self.paused = False
        self.game_over = False
        
        # Add spawn timers
        self.enemy_spawn_timer = 0
        self.power_up_spawn_timer = 0
        
        self.combo_count = 0
        self.combo_timer = 0
        self.milestone_power_up_counter = 0

        # Initialize mediapipe
        self.init_camera()
        
        # Bird properties
        self.bird_pos = GameConfig.BIRD_START_POS.copy()
        self.last_valid_pos = GameConfig.BIRD_START_POS.copy()
        self.last_pos = self.bird_pos.copy()
        self.bird_size = GameConfig.BIRD_SIZE
        self.bird_health = GameConfig.BIRD_START_HEALTH
        self.shooting_delay = 0
        self.invincible_timer = 0
        self.flash_effect = False
        self.frame_count = 0
        
        # Damage values
        self.damage_values = GameConfig.DAMAGE_VALUES
        
        # Special effects system
        self.effects = {
            'health': {'color': (0, 255, 0), 'duration': 0, 'uses': 0},
            'rapid_fire': {'color': (255, 165, 0), 'duration': GameConfig.RAPID_FIRE_DURATION, 'uses': 0},
            'triple_shot': {'color': (255, 255, 0), 'duration': 0, 'uses': GameConfig.TRIPLE_SHOT_USES},
            'shield': {'color': (0, 191, 255), 'duration': GameConfig.SHIELD_DURATION, 'uses': 0},
            'split_shot': {'color': (255, 105, 180), 'duration': 0, 'uses': GameConfig.SPLIT_SHOT_USES}
        }
        
        # Game collections
        self.score = 0
        self.level = 1
        self.bullets = []
        self.pollution = []
        self.power_ups = []
        self.clock = pygame.time.Clock()
        self.time_factor = 1.0
        
        # Initialize backgrounds dictionary before loading assets
        self.backgrounds = {}
        
        # Initialize active animations list
        self.active_animations = []
        
        # Initialize assets after all required attributes are set
        self.init_assets()

        self.menu_state = MenuState(self)
        self.in_menu = True

    def init_camera(self):
        try:
            self.mp_hands = mp.solutions.hands
            self.mp_draw = mp.solutions.drawing_utils
            self.hands = self.mp_hands.Hands(
                max_num_hands=2,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5,
                model_complexity=0
            )
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                print("Warning: Cannot open camera, falling back to keyboard controls")
                self.use_camera = False
                return False
            self.use_camera = True
            return True
        except Exception as e:
            print(f"Error initializing camera: {e}")
            self.use_camera = False
            return False

    def load_image(self, path, size=None):
        try:
            full_path = os.path.join(self.base_path, path)
            #print(f"Loading image from: {full_path}")  # 添加这行来打印实际路径
            if not os.path.exists(full_path):
                print(f"Warning: Image not found: {full_path}")
                surface = pygame.Surface((30, 30))
                surface.fill((255, 0, 255))  # Placeholder for missing image
                return surface
            
            image = pygame.image.load(full_path)
            if size:
                try:
                    image = pygame.transform.scale(image, size)
                except ValueError as e:
                    print(f"Error scaling image {path}: {e}")
                    return image
            return image
        except pygame.error as e:
            print(f"Error loading image {path}: {e}")
            surface = pygame.Surface((30, 30))
            surface.fill((255, 0, 255))
            return surface
    
    def init_assets(self):
        self.base_path = os.path.dirname(__file__)

        # 首先加载通用资源
        # Load bullet image
        self.bullet_image = self.load_image(
            GameConfig.ASSETS['bullet'],
            (30, 30)
        )

        # 然后加载特殊子弹图片
        self.bullet_images = {
            'default': self.bullet_image  # 现在可以使用 bullet_image 了
        }
        for bullet_type, path in GameConfig.BULLET_TYPES.items():
            self.bullet_images[bullet_type] = self.load_image(path, (30, 30))

        # 加载道具图标
        self.power_up_icons = {}
        for power_type, path in GameConfig.POWER_UP_ICONS.items():
            self.power_up_icons[power_type] = self.load_image(path, (70, 70))

        # 加载背景
        for state, path in GameConfig.BACKGROUNDS.items():
            try:
                full_path = os.path.join(self.base_path, path)
                image = pygame.image.load(full_path)
                self.backgrounds[state] = pygame.transform.scale(image, (self.width, self.height))
            except (pygame.error, FileNotFoundError) as e:
                print(f"Error loading background {path}: {e}")
                fallback = pygame.Surface((self.width, self.height))
                if state == 'healthy':
                    fallback.fill((135, 206, 235))
                elif state == 'slight_damage':
                    fallback.fill((170, 170, 170))
                else:
                    fallback.fill((139, 69, 19))
                self.backgrounds[state] = fallback
        
        # 加载污染物图片
        self.pollution_images = {
            'normal': [],
            'fast': [],
            'large': []
        }

        pollution_sizes = {
            'normal': (70, 70),
            'fast': (60, 60),
            'large': (72, 120)
        }
        
        for enemy_type, paths in GameConfig.POLLUTION_ASSETS.items():
            for path in paths:
                image = self.load_image(path, pollution_sizes[enemy_type])
                self.pollution_images[enemy_type].append(image)

        # 加载游戏结束图片
        self.game_over_image = self.load_image(
            GameConfig.ASSETS['game_over'],
            (self.width // 2, self.height // 3)
        )

        # 加载护盾图片
        self.shield_image = self.load_image(
            GameConfig.ASSETS['shield'],
            (115, 115)
        )

        # 加载恢复动画帧
        self.recovery_frames = []
        for path in GameConfig.RECOVERY_ANIMATION:
            image = self.load_image(path, (60, 60))
            self.recovery_frames.append(image)
        
        self.impact_frames = []
        for path in GameConfig.IMPACT_ANIMATION:
            image = self.load_image(path, (100, 100))  # 可以调整爆炸效果的大小
            self.impact_frames.append(image)

        # 加载鸟的动画
        self.bird_images = {
            'healthy': [],
            'slight_damage': [],
            'heavily_damaged': []
        }
        
        for i in range(1, 5):
            self.bird_images['healthy'].append(
                self.load_image(GameConfig.ASSETS['bird_healthy'].format(i), (90, 90))
            )
            self.bird_images['slight_damage'].append(
                self.load_image(GameConfig.ASSETS['bird_slight_damage'].format(i), (90, 90))
            )
            self.bird_images['heavily_damaged'].append(
                self.load_image(GameConfig.ASSETS['bird_heavily_damaged'].format(i), (90, 90))
            )
        
        # Loading sound effect
        self.sound_effect = {}
        self.bullet_sound = 'single_shot'
        self.background_music_playing = False
        self.game_over_playing = False
        self.shield_loop_playing = False
        for sound_type, path in GameConfig.SOUND_TYPES.items():
            self.sound_effect[sound_type] = pygame.mixer.Sound(path)
        
        self.current_frame = 0
        self.frame_update_speed = 5

    def load_highscore(self):
        try:
            with open(GameConfig.HIGHSCORE_FILE, 'r') as f:
                return int(f.read().strip())
        except (FileNotFoundError, ValueError):
            return 0
            
    def save_highscore(self):
        try:
            with open(GameConfig.HIGHSCORE_FILE, 'w') as f:
                f.write(str(self.highscore))
        except IOError:
            print("Unable to save highscore")
        
            
    def check_collision(self, pos1, pos2, size2, is_bullet=False):
        """
        通用的碰撞检测
        pos1: 第一个物体的位置
        pos2: 第二个物体的位置
        size2: 第二个物体的碰撞盒大小
        is_bullet: 是否是子弹的碰撞检测
        """
        if is_bullet:
            # 子弹使用更小的碰撞盒
            collision_size1 = 15  # 子弹碰撞盒半径
            # 子弹位置已经是中心点，不需要额外偏移
            center1 = pos1
        else:
            # 鸟的碰撞盒
            collision_size1 = 45  # 图片大小的一半
            # 计算鸟的中心位置
            center1 = [
                pos1[0] + 45,  # 加上图片宽度的一半
                pos1[1] + 45   # 加上图片高度的一半
            ]
        
        # 对于Boss类型敌人使用矩形碰撞盒
        for p in self.pollution:
            if p['type'] == 'large' and pos2 == p['pos']:
                # Boss使用矩形碰撞盒
                boss_left = pos2[0] - 36  # 72/2
                boss_right = pos2[0] + 36
                boss_top = pos2[1] - 60   # 120/2
                boss_bottom = pos2[1] + 60
                
                # 圆形与矩形的碰撞检测
                closest_x = max(boss_left, min(center1[0], boss_right))
                closest_y = max(boss_top, min(center1[1], boss_bottom))
                
                distance = np.sqrt((center1[0] - closest_x)**2 + 
                                (center1[1] - closest_y)**2)
                
                return distance < collision_size1
        
        # 其他敌人使用圆形碰撞盒
        distance = np.sqrt((center1[0] - pos2[0])**2 + 
                        (center1[1] - pos2[1])**2)
        
        return distance < (size2 + collision_size1)
            
    def detect_hand_gesture(self, hand_landmarks):
        thumb_tip = hand_landmarks.landmark[4]
        index_tip = hand_landmarks.landmark[8]
        distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + 
                          (thumb_tip.y - index_tip.y)**2)
        return distance < 0.05

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False
        
        ret, frame = self.cap.read()
        if not ret:
            return
            
        frame = cv2.flip(frame, 1)
        frame = cv2.resize(frame, (320, 240))
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(frame_rgb)
        
        shoot = False
        
        if results.multi_hand_landmarks:
            for hand_landmarks, handedness in zip(results.multi_hand_landmarks, results.multi_handedness):
                # 右手控制移动
                if handedness.classification[0].label == 'Right':
                    index_tip = hand_landmarks.landmark[8]
                    
                    # 限制在左侧1/3区域
                    max_x = self.width // 3
                    game_x = min(max(30, int(index_tip.x * max_x)), max_x - 30)
                    game_y = min(max(30, int(index_tip.y * self.height)), self.height - 30)
                    
                    # 使用较小的平滑系数使移动更平滑
                    self.bird_pos[0] += (game_x - self.bird_pos[0]) * 0.15
                    self.bird_pos[1] += (game_y - self.bird_pos[1]) * 0.15
                    
                # 左手控制射击
                elif handedness.classification[0].label == 'Left':
                    if self.detect_hand_gesture(hand_landmarks) and self.shooting_delay <= 0:
                        shoot = True
            
            if self.frame_count % 2 == 0:
                self.draw_hand_tracking(frame, results.multi_hand_landmarks)
        
        # 确保边界限制
        self.bird_pos[0] = max(30, min(self.width//3 - 30, self.bird_pos[0]))
        self.bird_pos[1] = max(30, min(self.height - 30, self.bird_pos[1]))
        
        if shoot:
            self.fire_bullet()
            self.shooting_delay = 20 if not self.effects['rapid_fire']['duration'] > 0 else 10

            self.play_single_sound(self.bullet_sound, 0, 0.85)
            
            
        if self.shooting_delay > 0:
            self.shooting_delay -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            
        self.frame_count += 1

    def draw_hand_tracking(self, frame, hand_landmarks):
        for landmarks in hand_landmarks:
            self.mp_draw.draw_landmarks(frame, landmarks, self.mp_hands.HAND_CONNECTIONS)
        cv2.imshow('Hand Tracking', frame)
        cv2.waitKey(1)

    def fire_bullet(self):
        angles = set()  # 使用集合避免重复角度
        # 记录当前激活的效果
        active_effect = None
        
        if self.effects['triple_shot']['uses'] > 0:
            angles.update([-15, 0, 15])
            active_effect = 'triple_shot'
        elif self.effects['split_shot']['uses'] > 0:
            angles.update([-30, -15, 0, 15, 30])
            active_effect = 'split_shot'
        else:
            angles.add(0)

        # 为所有角度创建子弹
        new_bullets = []
        for angle in angles:
            bullet = {
                'pos': [self.bird_pos[0] + 45, self.bird_pos[1] + 45],
                'angle': angle,
                'power': 1,
                'effect': active_effect  # 保存子弹类型
            }
            new_bullets.append(bullet)
        
        # 添加所有子弹
        self.bullets.extend(new_bullets)
        
        # 最后再减少使用次数
        if active_effect == 'triple_shot':
            self.effects['triple_shot']['uses'] -= 1
        elif active_effect == 'split_shot':
            self.effects['split_shot']['uses'] -= 1
    
    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        
        # Calculate spawn interval with smoother scaling
        interval = max(GameConfig.MIN_SPAWN_INTERVAL, 
                    50 - int(self.level * 1.5))
        
        if self.enemy_spawn_timer >= interval:
            self.enemy_spawn_timer = 0
            
            # Base number of enemies plus one every 4 levels
            num_enemies = 2 + (self.level - 1) // 4
            num_enemies = min(4, num_enemies)
            
            # 定义碰撞盒大小 - 使用图片大小的一半
            size_map = {
                'normal': 35,  # 70/2
                'fast': 30,    # 60/2
                'large': 36    # 100/2
            }
            
            for _ in range(num_enemies):
                # Weighted enemy type selection based on level
                weights = {
                    'normal': max(50 - self.level * 2, 20),
                    'fast': min(30 + self.level * 2, 50),
                    'large': min(20 + self.level, 30)
                }
                total_weight = sum(weights.values())
                weights = {k: v/total_weight for k, v in weights.items()}
                
                enemy_type = random.choices(
                    list(weights.keys()),
                    weights=list(weights.values())
                )[0]
                
                # Calculate speed with cap
                base_speed = 8 if enemy_type == 'fast' else 5
                speed_bonus = 1 + (GameConfig.SPEED_INCREASE_PER_LEVEL * (self.level - 1))
                actual_speed = min(
                    base_speed * speed_bonus,
                    GameConfig.MAX_SPEED[enemy_type]
                )
                
                self.pollution.append({
                    'pos': [self.width, random.randint(50, self.height-50)],
                    'type': enemy_type,
                    'size': size_map[enemy_type],  # 现在size_map已定义
                    'speed': actual_speed,
                    'health': 3 if enemy_type == 'large' else 1
                })

    def run(self):

        self.play_single_sound('background_music', -1, 0.3) # Playback background music
        self.background_music_playing = True

        try:
            if self.in_menu:
                continue_game = self.menu_state.run()
                if not continue_game:
                    return
                self.in_menu = False

            self.running = True  # 确保running被设置
            while self.running:
                if not self.game_over:
                    self.handle_input()
                    self.update()
                else:
                    for event in pygame.event.get():
                        if event.type == QUIT:
                            self.running = False
                        elif event.type == KEYDOWN:
                            if event.key == K_r:
                                self.play_single_sound('button_click', 0, 1.3)
                                self.reset_game()
                            elif event.key == K_q:
                                self.running = False
            
                self.draw()
                self.clock.tick(60)
        finally:
            if hasattr(self, 'cap'):  # 检查cap是否存在
                self.cap.release()
            cv2.destroyAllWindows()
            pygame.quit()

    def spawn_power_ups(self):
        self.power_up_spawn_timer += 1
        
        interval = max(
            GameConfig.MIN_POWER_UP_INTERVAL,
            GameConfig.POWER_UP_BASE_INTERVAL - self.level * GameConfig.POWER_UP_INTERVAL_DECREASE
        )
        
        # 只在血量非常低时才触发概率加成
        if self.bird_health < GameConfig.LOW_HEALTH_THRESHOLD:
            interval = int(interval * (1 - GameConfig.LOW_HEALTH_BONUS_CHANCE))
        
        if self.power_up_spawn_timer >= interval:
            self.power_up_spawn_timer = 0
            
            # 更保守的权重设置
            weights = {
                'health': 10 if self.bird_health < 30 else 5,  # 降低阈值和权重
                'shield': 6 if self.bird_health < 40 else 3,   # 降低阈值和权重
                'rapid_fire': 20,  # 增加攻击道具权重
                'triple_shot': 20,
                'split_shot': 20
            }
            
            total_weight = sum(weights.values())
            weights = {k: v/total_weight for k, v in weights.items()}
            
            power_type = random.choices(
                list(weights.keys()),
                weights=list(weights.values())
            )[0]
            
            self.power_ups.append({
                'type': power_type,
                'pos': [self.width, random.randint(50, self.height-50)]
            })
        
        # 里程碑道具生成更严格
        if self.milestone_power_up_counter >= 1800:  # 进一步增加间隔
            self.milestone_power_up_counter = 0
            # 只在血量很低时才生成
            if self.bird_health < 25:  # 更严格的血量条件
                self.power_ups.append({
                    'type': random.choice(['shield', 'health']),
                    'pos': [self.width, random.randint(50, self.height-50)]
                })

    def update_bullets(self):
        for bullet in self.bullets[:]:
            speed = 10 * self.time_factor
            rad_angle = np.radians(bullet['angle'])
            bullet['pos'][0] += np.cos(rad_angle) * speed
            bullet['pos'][1] += np.sin(rad_angle) * speed
            
            if (bullet['pos'][0] > self.width or 
                bullet['pos'][1] < 0 or bullet['pos'][1] > self.height):
                self.bullets.remove(bullet)

    def add_recovery_animation(self, pos):
        """在指定位置添加一个恢复动画"""
        self.active_animations.append({
            'type': 'recovery',
            'frames': self.recovery_frames,
            'current_frame': 0,
            'pos': pos.copy(),  # 复制位置以避免引用问题
            'frame_delay': 5,   # 每5帧更新一次
            'frame_counter': 0
        })

    def add_impact_animation(self, pos):
        """在指定位置添加爆炸动画"""
        self.active_animations.append({
            'type': 'impact',
            'frames': self.impact_frames,
            'current_frame': 0,
            'pos': pos.copy(),  # 复制位置以避免引用问题
            'frame_delay': 3,   # 增加延迟，使动画更容易看清
            'frame_counter': 0
        })

    def update_animations(self):
        """更新所有活动的动画"""
        for anim in self.active_animations[:]:  # 使用副本来遍历
            anim['frame_counter'] += 1
            if anim['frame_counter'] >= anim['frame_delay']:
                anim['frame_counter'] = 0
                anim['current_frame'] += 1
                if anim['current_frame'] >= len(anim['frames']):
                    self.active_animations.remove(anim)

    def update(self):
        # 更新特效持续时间
        for effect in self.effects.values():
            if effect['duration'] > 0:
                effect['duration'] -= 1

        # 更新连击系统
        if hasattr(self, 'combo_timer') and self.combo_timer > 0:
            self.combo_timer -= 1
        else:
            self.combo_count = 0
        
        # 更新里程碑计数器
        if hasattr(self, 'milestone_power_up_counter'):
            self.milestone_power_up_counter += 1

        # 生成敌人和道具
        self.spawn_enemies()
        self.spawn_power_ups()
        self.update_bullets()
        self.update_animations()
        
        # 更新污染物
        for p in self.pollution[:]:
            p['pos'][0] -= p['speed'] * self.time_factor
            if p['pos'][0] < -50:
                self.pollution.remove(p)
                continue
                    
            for bullet in self.bullets[:]:
                if self.check_collision(bullet['pos'], p['pos'], p['size'], is_bullet=True):
                    p['health'] -= bullet['power']
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    # 添加爆炸效果
                    self.add_impact_animation(p['pos'])

                    self.play_multiple_sound('hit_pollution', 0, 0.6)

                    if p['health'] <= 0:
                        if p in self.pollution:
                            # 新的计分逻辑
                            self.combo_count = getattr(self, 'combo_count', 0) + 1
                            self.combo_timer = 120  # 2 seconds to maintain combo
                            
                            combo_bonus = min(
                                1 + (self.combo_count * GameConfig.COMBO_MULTIPLIER),
                                GameConfig.MAX_COMBO_MULTIPLIER
                            )
                            base_score = GameConfig.BASE_SCORES[p['type']]
                            self.score += int(base_score * combo_bonus * self.level)
                            
                            self.pollution.remove(p)
                        break
            
            # 碰撞伤害检测
            if (self.invincible_timer <= 0 and
                not self.effects['shield']['duration'] > 0 and
                self.check_collision(self.bird_pos, p['pos'], p['size'])):
                    
                self.bird_health -= self.damage_values[p['type']]

                self.play_single_sound('get_hurt', 0, 0.8)
                
                # 计算基于等级的无敌时间
                base_invincibility = GameConfig.BASE_INVINCIBILITY_TIME
                level_bonus = self.level * GameConfig.INVINCIBILITY_INCREASE_PER_LEVEL
                self.invincible_timer = min(
                    base_invincibility + level_bonus,
                    GameConfig.MAX_INVINCIBILITY_TIME
                )
                
                self.flash_effect = True
                if p in self.pollution:
                    self.pollution.remove(p)

        # 更新道具
        for power in self.power_ups[:]:
            power['pos'][0] -= 3 * self.time_factor
            if power['pos'][0] < 0:
                self.power_ups.remove(power)
            
            if self.check_collision(self.bird_pos, power['pos'], 10):
                self.apply_power_up(power['type'])
                self.power_ups.remove(power)
        
        # 检查升级条件
        required_score = int(GameConfig.BASE_LEVEL_SCORE * 
                            (GameConfig.LEVEL_SCORE_MULTIPLIER ** (self.level - 1)))
        
        if self.score >= required_score:
            self.level += 1
            self.play_single_sound('level_up', 0, 0.6)

            # 更严格的升级奖励条件
            if self.bird_health < 35:  # 降低阈值
                # 不是每次升级都给道具
                if random.random() < 0.5:  # 50%概率
                    self.power_ups.append({
                        'type': random.choice(['shield', 'health']),
                        'pos': [self.width, random.randint(50, self.height-50)]
                    })
            # 保留原有的敌人速度增加逻辑
            if self.level > 1:
                for p in self.pollution:
                    p['speed'] *= 1.05
        
        # 检查游戏结束条件
        if self.bird_health <= 0:
            self.game_over = True

        if self.score > self.highscore:
            self.highscore = self.score
            self.save_highscore()

    def handle_damage(self, damage_type):
        """处理玩家受到伤害的逻辑"""
        if self.invincible_timer <= 0 and not self.effects['shield']['duration'] > 0:
            self.bird_health -= self.damage_values[damage_type]
            
            # 计算基于等级的无敌时间
            base_invincibility = GameConfig.BASE_INVINCIBILITY_TIME
            level_bonus = self.level * GameConfig.INVINCIBILITY_INCREASE_PER_LEVEL
            self.invincible_timer = min(
                base_invincibility + level_bonus,
                GameConfig.MAX_INVINCIBILITY_TIME
            )
            
            self.flash_effect = True
            
            # 添加临时减速效果
            self.time_factor = 0.7
            # 一秒后恢复正常速度
            pygame.time.set_timer(pygame.USEREVENT, 1000)
            
            return True  # 表示伤害已生效
        return False 

    def apply_power_up(self, power_type):
        if power_type == 'health':
            self.bird_health = min(100, self.bird_health + 30)  # 增加血量
            self.add_recovery_animation(self.bird_pos)
            self.play_single_sound('health_recovery', 0, 0.4)
            
        elif power_type == 'rapid_fire':
            self.effects['rapid_fire']['duration'] += 600  # 累加持续时间
            self.play_single_sound('collect_tools', 0, 1)
        elif power_type == 'triple_shot':
            self.effects['triple_shot']['uses'] += 5  # 累加使用次数
            self.play_single_sound('collect_tools', 0, 1)
        elif power_type == 'shield':
            self.effects['shield']['duration'] += 600  # 累加护盾持续时间
            self.sound_effect['background_music'].stop() # Stop background music
            self.background_music_playing = False
            if not self.shield_loop_playing:
                self.play_single_sound('shield_loop', -1, 0.5)
                self.shield_loop_playing = True
        elif power_type == 'split_shot':
            self.effects['split_shot']['uses'] += 3  # 累加分裂子弹使用次数
            self.play_single_sound('collect_tools', 0, 1)
    
    def draw(self):
        self.screen.fill((135, 206, 235))

        if self.bird_health >= 75:
            current_bg = self.backgrounds.get('healthy')
        elif self.bird_health >= 25:
            current_bg = self.backgrounds.get('slight_damage')
        else:
            current_bg = self.backgrounds.get('heavily_damaged')

        # Draw the background
        if current_bg:
            self.screen.blit(current_bg, (0, 0))
        else:
            self.screen.fill((135, 206, 235))

        # 根据健康值选择鸟的状态
        if self.bird_health >= 75:
            state = 'healthy'
        elif self.bird_health >= 25:
            state = 'slight_damage'
        else:
            state = 'heavily_damaged'

        # 绘制动画帧
        if state in self.bird_images:
            bird_animation = self.bird_images[state]
            if bird_animation:  # 确保动画帧不为空
                current_image = bird_animation[self.current_frame // self.frame_update_speed % len(bird_animation)]
                
                # 如果在无敌时间内，设置透明度和闪烁
                if self.invincible_timer > 0:
                    if (self.frame_count // 5) % 2 == 0:  # 每 5 帧切换显示/隐藏
                        current_image.set_alpha(230)  # 半透明
                        self.screen.blit(current_image, self.bird_pos)
                else:
                    current_image.set_alpha(255)  # 恢复正常透明度
                    self.screen.blit(current_image, self.bird_pos)
            else:
                print(f"No animation frames found for state: {state}")
        else:
            print(f"Invalid bird state: {state}")

        self.current_frame = (self.current_frame + 1) % (self.frame_update_speed * len(bird_animation))
        
        self.draw_ui()

        for power in self.power_ups:
            power_pos = (int(power['pos'][0] - 35), int(power['pos'][1] - 35))  # 居中显示图标
            if power['type'] in self.power_up_icons:
                self.screen.blit(self.power_up_icons[power['type']], power_pos)
            else:
                # 如果没有找到图标，使用原来的圆形显示
                color = self.effects[power['type']]['color']
                pygame.draw.circle(self.screen, color, 
                                 (int(power['pos'][0]), int(power['pos'][1])), 35)

        
        for p in self.pollution:
            # 根据敌人类型选择对应的动画帧
            animation_frames = self.pollution_images[p['type']]
            current_frame = (self.frame_count // 10) % len(animation_frames)  # 每10帧切换一次动画
            enemy_image = animation_frames[current_frame]
            
            # 计算图片绘制位置（让图片中心对准敌人位置）
            image_x = int(p['pos'][0] - enemy_image.get_width() // 2)
            image_y = int(p['pos'][1] - enemy_image.get_height() // 2)
            
            self.screen.blit(enemy_image, (image_x, image_y))
        
        for bullet in self.bullets:
            bullet_pos = (int(bullet['pos'][0] - 15), int(bullet['pos'][1] - 15))
            
            # 根据子弹自身的效果类型选择图片
            bullet_image = self.bullet_images['default']
            self.bullet_sound = 'single_shot'
            
            if bullet.get('effect') == 'split_shot':
                bullet_image = self.bullet_images.get('split_shot', self.bullet_images['default'])
                self.bullet_sound = 'multi_shot'
            elif bullet.get('effect') == 'triple_shot':
                bullet_image = self.bullet_images.get('triple_shot', self.bullet_images['default'])
                self.bullet_sound = 'multi_shot'
            elif self.effects['rapid_fire']['duration'] > 0:  # rapid fire 效果仍然基于持续时间
                bullet_image = self.bullet_images.get('rapid_fire', self.bullet_images['default'])
            
            self.screen.blit(bullet_image, bullet_pos)
        

        self.draw_ui()

        # 如果有护盾，绘制护盾
        if self.effects['shield']['duration'] > 0:
            
            shield_pos = (
                int(self.bird_pos[0] - (115 - 90) / 2),  # 水平偏移
                int(self.bird_pos[1] - (115 - 90) / 2)   # 垂直偏移
            )
            self.screen.blit(self.shield_image, shield_pos)
        else:
            self.sound_effect['shield_loop'].stop()
            self.shield_loop_playing = False
            if not self.background_music_playing:
                self.play_single_sound('background_music', -1, 0.3)
                self.background_music_playing = True
        
        for anim in self.active_animations:
            if anim['type'] == 'recovery':
                current_image = anim['frames'][anim['current_frame']]
                self.screen.blit(current_image, anim['pos'])
            elif anim['type'] == 'impact':
                current_image = anim['frames'][anim['current_frame']]
                # 将爆炸效果居中显示在碰撞位置
                impact_pos = (
                    int(anim['pos'][0] - current_image.get_width() // 2),
                    int(anim['pos'][1] - current_image.get_height() // 2)
                )
                self.screen.blit(current_image, impact_pos)
                                 
        if self.game_over:
            self.draw_game_over()
            if self.background_music_playing:
                self.sound_effect['background_music'].stop()
            if self.shield_loop_playing:
                self.sound_effect['shield_loop'].stop()
            if not self.game_over_playing:
                self.play_single_sound('game_over', 0, 0.4)
                self.game_over_playing = True
        
        pygame.display.flip()
        
    def draw_ui(self):
        try:
            font = pygame.font.Font('font/press_start_2p.ttf', 16)  # 降低字号到16
        except:
            print("Pixel font not found, using default font")
            font = pygame.font.Font(None, 28)  # 相应降低默认字号
            
        # 格式化效果名称的辅助函数
        def format_effect_name(name):
            # 将 snake_case 转换为 Title Case 并简化名称
            name_map = {
                'health': 'Health',
                'rapid_fire': 'Rapid Fire',
                'triple_shot': 'Triple Shot',
                'shield': 'Shield',
                'split_shot': 'Split Shot'
            }
            return name_map.get(name, name.replace('_', ' ').title())
        
        # 主要游戏数据显示（左上角）
        ui_data = {
            'HP': f"{max(0, self.bird_health)}%",  # 简化 Health 为 HP
            'Score': f"{self.score}",
            'Best': f"{self.highscore}", 
            'Level': f"{self.level}"
        }
        
        shadow_color = (50, 50, 50)
        text_color = (255, 255, 255)
        
        # 左上角状态显示
        for i, (key, value) in enumerate(ui_data.items()):
            text = f'{key}: {value}'
            # 阴影
            shadow_surface = font.render(text, True, shadow_color)
            self.screen.blit(shadow_surface, (12, 12 + i * 30))  # 减少行距到30
            
            # 主文本
            text_surface = font.render(text, True, text_color)
            self.screen.blit(text_surface, (10, 10 + i * 30))
        
        # 右上角效果显示
        margin = 20   # 向左移动起始位置，留出更多空间
        y = 10
        for effect_name, effect in self.effects.items():
            if effect['duration'] > 0 or effect['uses'] > 0:
                formatted_name = format_effect_name(effect_name)
                if effect['duration'] > 0:
                    text = f"{formatted_name}: {effect['duration'] // 60}s"
                else:
                    text = f"{formatted_name}: {effect['uses']}"
                
                # 获取文本尺寸
                text_width, _ = font.size(text)
                # 从右边缘向左计算位置
                x = self.width - text_width - margin
                
                # 阴影
                shadow_surface = font.render(text, True, shadow_color)
                self.screen.blit(shadow_surface, (x + 2, y + 2))
                
                # 主文本
                text_surface = font.render(text, True, text_color)
                self.screen.blit(text_surface, (x, y))
                y += 25
    
    def draw_game_over(self):
        # 加载游戏结束图片并缩放至全屏
        game_over_screen = self.load_image(
            'Animation/Effects/Game_Over.PNG',
            (self.width, self.height)
        )
        
        self.screen.blit(game_over_screen, (0, 0))
        
        try:
            font = pygame.font.Font('font/press_start_2p.ttf', 24)
        except:
            print("Pixel font not found, using default font")
            font = pygame.font.Font(None, 48)
        
        text_color = (255, 255, 255)  # 改为白色
        shadow_color = (50, 50, 50) 
        
        # 修改标签顺序
        labels = ["BEST", "SCORE", "LEVEL"]
        label_to_attr = {
            "BEST": "highscore",
            "SCORE": "score",
            "LEVEL": "level"
        }
        
        # 计算最长标签的宽度来确定对齐位置
        max_label_width = max(font.size(label)[0] for label in labels)
        
        # 设置中心点，将整体下移
        center_x = self.width // 2
        start_y = self.height * 0.55  # 从0.45改为0.5，整体下移
        spacing = 45
        
        # 在中心点两侧绘制文本
        for i, label in enumerate(labels):
            y = start_y + i * spacing
            
            # 计算标签和值的位置
            label_pos_x = center_x - 20
            value = str(getattr(self, label_to_attr[label]))
            
            # 绘制标签（右对齐）
            label_surface = font.render(f"{label}:", True, text_color)
            label_rect = label_surface.get_rect(right=label_pos_x, centery=y)
            label_shadow = font.render(f"{label}:", True, shadow_color)
            shadow_rect = label_shadow.get_rect(right=label_pos_x + 2, centery=y + 2)
            
            # 绘制值（左对齐）
            value_surface = font.render(value, True, text_color)
            value_rect = value_surface.get_rect(left=label_pos_x + 20, centery=y)
            value_shadow = font.render(value, True, shadow_color)
            shadow_value_rect = value_shadow.get_rect(left=label_pos_x + 22, centery=y + 2)
            
            # 绘制阴影
            self.screen.blit(label_shadow, shadow_rect)
            self.screen.blit(value_shadow, shadow_value_rect)
            # 绘制主文本
            self.screen.blit(label_surface, label_rect)
            self.screen.blit(value_surface, value_rect)
        
        # 操作提示也相应下移
        hint = "RETRY: R   QUIT: Q"
        hint_surface = font.render(hint, True, text_color)
        hint_rect = hint_surface.get_rect(center=(self.width//2, self.height * 0.78))  # 从0.7改为0.75
        hint_shadow = font.render(hint, True, shadow_color)
        hint_shadow_rect = hint_shadow.get_rect(center=(self.width//2 + 2, self.height * 0.78 + 2))
        
        self.screen.blit(hint_shadow, hint_shadow_rect)
        self.screen.blit(hint_surface, hint_rect)
            
    def reset_game(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)

        for alpha in range(128, -1, -16):  # 渐隐效果
            overlay.set_alpha(alpha)
            self.screen.blit(overlay, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

        self.bird_pos = [100, self.height//2]
        self.last_pos = self.bird_pos.copy()
        self.bird_health = 100
        self.shooting_delay = 0
        self.invincible_timer = 0
        self.score = 0
        self.level = 1
        self.bullets.clear()
        self.pollution.clear()
        self.power_ups.clear()
        self.game_over = False
        self.flash_effect = False
        for effect in self.effects.values():
            effect['duration'] = 0
            effect['uses'] = 0
        
        self.background_music_playing = False
        self.shield_loop_playing = False
        self.game_over_playing = False
    
    # Play sound without overlap
    def play_single_sound(self, sound_type, loop=0, volume=1.0):
        if sound_type in self.sound_effect:
            self.sound_effect[sound_type].set_volume(volume)
            self.sound_effect[sound_type].play(loops=loop)
        else:
            print(f"Sound type '{sound_type}' not found.")
    
    # Play sound with overlap
    def play_multiple_sound(self, sound_type, loop=0, volume=1.0):
        if sound_type in GameConfig.SOUND_TYPES:
            sound = pygame.mixer.Sound(GameConfig.SOUND_TYPES[sound_type])
            sound.set_volume(volume)
            sound.play(loops=loop)
        else:
            print(f"Sound type '{sound_type}' not found in configuration.")
        
if __name__ == '__main__':
    game = Game()
    game.run()

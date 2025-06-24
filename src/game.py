import pygame
import sys
from constants import DisplayConstants
from enums import GameState
from game_objects.body_system import BodySystem
from game_objects.disease import Disease, DIABETES
from ui.screen_renderer import ScreenRenderer
from event_handler import EventHandler
from game_updater import GameUpdater

class Game:
    # Основной класс игры, управляющий всеми игровыми системами
    
    def __init__(self):
        self.setup_game_state()
        self.setup_game_systems()
        self.setup_educational_content()
        self.educational_quest = None
        self.quest_progress = 0
        
    def setup_game_state(self):
        # Инициализация базового состояния игры
        self.state = GameState.MENU
        self.body = BodySystem()
        
    def setup_game_systems(self):
        # Инициализация игровых подсистем
        self.event_handler = EventHandler(self)
        self.screen_renderer = ScreenRenderer(self)
        self.updater = GameUpdater(self)
        
    def setup_educational_content(self):
        # Инициализация обучающего контента
        self.body.disease = None
        self.body.disease = Disease(DIABETES)
        self.educational_quest = None
        self.quest_progress = 0

    def handle_event(self, event):
        # Обработка игровых событий
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_position = pygame.mouse.get_pos()
            if self.state == GameState.MENU:
                if not self.event_handler.handle_menu_click(mouse_position):
                    pygame.quit()
                    sys.exit()
            elif self.state == GameState.GAME_OVER:
                if not self.event_handler.handle_game_over_click(mouse_position):
                    pygame.quit()
                    sys.exit()
            else:
                self.event_handler.handle_main_gameplay_click(mouse_position)

    def draw(self, screen):
        # Отрисовка игрового интерфейса
        screen.fill(DisplayConstants.BACKGROUND)
        self.screen_renderer.draw(screen)

    def update(self, dt):
        # Обновление игровой логики
        self.updater.update(dt) 

    def start_educational_quest(self, name):
        # Запуск образовательного квеста по имени
        if name == "Диабет":
            self.educational_quest = {
                "name": "Образовательный квест: Диабет",
                "steps": [
                    "Что такое диабет?",
                    "Причины возникновения диабета",
                    "Симптомы диабета",
                    "Профилактика и лечение диабета"
                ],
                "current_step": 0
            }
            self.quest_progress = 0
        else:
            self.educational_quest = None
            self.quest_progress = 0 
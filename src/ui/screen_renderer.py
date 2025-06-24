import pygame
from constants import DisplayConstants, GameObjectConstants, GameBalanceConstants
from enums import GameState, Nutrient
from ui.user_interface import UserInterface
import math

# Отвечает за отрисовку всех элементов игры
class ScreenRenderer:
    """Отвечает за отрисовку всех элементов игры"""
    
    def __init__(self, game):
        self.game = game
        self.ui = UserInterface()

    def draw(self, screen):
        # Отрисовывает текущий экран игры
        if self.game.state == GameState.MENU:
            self.draw_menu(screen)
        else:
            self.draw_main_gameplay_screen(screen)

    def draw_menu(self, screen):
        # Отрисовка главного меню
        screen.fill(DisplayConstants.BACKGROUND)
        self.ui.draw_text_centered(screen, "Биология Человека", 
                                 pygame.font.SysFont("arial", DisplayConstants.TITLE_FONT_SIZE), 
                                 DisplayConstants.HEIGHT // 4, DisplayConstants.GREEN)

        start_button = pygame.Rect(DisplayConstants.WIDTH // 2 - 100, DisplayConstants.HEIGHT // 2, 200, 50)
        quit_button = pygame.Rect(DisplayConstants.WIDTH // 2 - 100, DisplayConstants.HEIGHT // 2 + 70, 200, 50)
        
        self.ui.draw_button(screen, "Начать игру", start_button, DisplayConstants.BLUE)
        self.ui.draw_button(screen, "Выйти", quit_button, DisplayConstants.RED)

    def draw_main_gameplay_screen(self, screen):
        # Главный геймплейный экран со всеми кнопками и информацией
        screen.fill(DisplayConstants.BACKGROUND)
        self.ui.draw_text_centered(screen, "ОРГАНИЗМ ЧЕЛОВЕКА", pygame.font.SysFont("arial", DisplayConstants.TITLE_FONT_SIZE), 30, DisplayConstants.GREEN)

        # Кнопки управления системами
        button_width, button_height = 220, 50
        start_x = 80
        y = 100
        gap = 20
        # Кровеносная система
        self.ui.draw_button(screen, "Создать лейкоцит", pygame.Rect(start_x, y, button_width, button_height), DisplayConstants.GREEN)
        self.ui.draw_button(screen, "Атаковать вирусы", pygame.Rect(start_x, y + button_height + gap, button_width, button_height), DisplayConstants.RED)
        # Нервная система
        self.ui.draw_button(screen, "Снизить стресс", pygame.Rect(start_x, y + 2 * (button_height + gap), button_width, button_height), DisplayConstants.BLUE)
        # Пищеварительная система
        self.ui.draw_button(screen, "Принять пищу", pygame.Rect(start_x, y + 3 * (button_height + gap), button_width, button_height), DisplayConstants.ORANGE)
        # Заболевания
        dz_btn_y = y + 4 * (button_height + gap)
        if self.game.body.disease:
            self.ui.draw_button(screen, "Лечить", pygame.Rect(start_x, dz_btn_y, button_width, button_height), DisplayConstants.GREEN)
        else:
            self.ui.draw_button(screen, "Диагностика", pygame.Rect(start_x, dz_btn_y, button_width, button_height), DisplayConstants.BLUE)

        # Статус заболевания
        if self.game.body.disease:
            disease = self.game.body.disease
            font_status = pygame.font.SysFont("arial", DisplayConstants.MAIN_FONT_SIZE)
            progress_percent = int(100 * disease.progress / disease.duration) if disease.duration > 0 else 0
            ticks_left = max(0, disease.duration - disease.progress)
            seconds_left = int(ticks_left // 60)  # 60 тиков ≈ 1 секунда при 60 FPS
            status_text = f"Статус болезни: {progress_percent}% | Тяжесть: {disease.severity:.2f} | Осталось: {seconds_left} сек."
            self.ui.draw_text_centered(screen, status_text, font_status, dz_btn_y + button_height + 40, DisplayConstants.YELLOW)

        # Информация о заболевании (образовательный квест)
        if self.game.educational_quest:
            font_title = pygame.font.SysFont("arial", DisplayConstants.HEADER_FONT_SIZE, bold=True)
            font_main = pygame.font.SysFont("arial", DisplayConstants.SMALL_FONT_SIZE)
            disease_name = "Диабет"
            base_y = dz_btn_y + button_height + 10
            self.ui.draw_text_centered(screen, f"⚕ {disease_name} ⚕", font_title, base_y, DisplayConstants.RED)
            description = "Нарушение обмена глюкозы из-за недостатка инсулина."
            self.ui.draw_text_centered(screen, description, font_main, base_y + 30, DisplayConstants.WHITE)
            symptoms = "Симптомы: жажда, частое мочеиспускание, усталость."
            treatment = "Лечение: инсулинотерапия, диета, физические упражнения."
            self.ui.draw_text_centered(screen, symptoms, font_main, base_y + 60, DisplayConstants.YELLOW)
            self.ui.draw_text_centered(screen, treatment, font_main, base_y + 90, DisplayConstants.GREEN)

        # Панель состояния организма
        self.draw_status_panel(screen)

    def draw_status_panel(self, screen):
        # Отрисовка панели состояния организма
        panel_height = 100
        panel_rect = pygame.Rect(0, DisplayConstants.HEIGHT - panel_height, DisplayConstants.WIDTH, panel_height)
        self.ui.draw_panel(screen, panel_rect, DisplayConstants.PANEL_BG)

        indicators = [
            ("Здоровье", self.game.body.health, DisplayConstants.RED),
            ("Энергия", self.game.body.energy, DisplayConstants.YELLOW),
            ("Глюкоза", self.game.body.nutrients[Nutrient.GLUCOSE], DisplayConstants.GREEN),
            ("Стресс", self.game.body.stress_level, DisplayConstants.PURPLE)
        ]

        self.draw_indicators(screen, indicators, panel_rect)

        # Кнопка меню — справа внизу панели
        menu_button = pygame.Rect(DisplayConstants.WIDTH - 120, DisplayConstants.HEIGHT - panel_height + 30, 100, 40)
        self.ui.draw_button(screen, "Меню", menu_button, DisplayConstants.BLUE, DisplayConstants.WHITE)

    def draw_indicators(self, screen, indicators, panel_rect):
        # Отрисовка индикаторов состояния
        bar_width = 120
        spacing = 50
        total_width = len(indicators) * bar_width + (len(indicators) - 1) * spacing
        start_x = (DisplayConstants.WIDTH - total_width) // 2
        for i, (name, value, color) in enumerate(indicators):
            x_pos = start_x + i * (bar_width + spacing)
            y_pos = panel_rect.y + 35
            # Название показателя
            text_surface = pygame.font.SysFont("arial", DisplayConstants.SMALL_FONT_SIZE).render(name, True, DisplayConstants.WHITE)
            text_rect = text_surface.get_rect(x=x_pos, y=y_pos - 28)
            screen.blit(text_surface, text_rect)
            # Прогресс-бар
            self.ui.draw_progress_bar(screen, x_pos, y_pos, bar_width, 28, value, 100, color)
            # Значение показателя
            value_text = f"{int(value)}%"
            value_surface = pygame.font.SysFont("arial", DisplayConstants.SMALL_FONT_SIZE).render(value_text, True, DisplayConstants.WHITE)
            value_rect = value_surface.get_rect(x=x_pos + bar_width + 10, y=y_pos + 4)
            screen.blit(value_surface, value_rect) 
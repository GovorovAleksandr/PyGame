import pygame
from constants import DisplayConstants
from enums import GameState, CellType, Nutrient
from game_objects.disease import Disease

class EventHandler:
    def __init__(self, game):
        self.game = game

    def handle_menu_click(self, mouse_position):
        start_button = pygame.Rect(DisplayConstants.WIDTH // 2 - 100, DisplayConstants.HEIGHT // 2, 200, 50)
        quit_button = pygame.Rect(DisplayConstants.WIDTH // 2 - 100, DisplayConstants.HEIGHT // 2 + 70, 200, 50)
        if start_button.collidepoint(mouse_position):
            self.game.state = GameState.MAIN
            return True
        elif quit_button.collidepoint(mouse_position):
            return False
        return True

    def handle_game_over_click(self, mouse_position):
        popup_width = 400
        popup_height = 300
        popup_x = DisplayConstants.WIDTH // 2 - popup_width // 2
        popup_y = DisplayConstants.HEIGHT // 2 - popup_height // 2
        restart_button = pygame.Rect(DisplayConstants.WIDTH // 2 - 90, popup_y + 160, 180, 50)
        if restart_button.collidepoint(mouse_position):
            self.game.setup_game_state()
            self.game.setup_educational_content()
            return True
        quit_button = pygame.Rect(DisplayConstants.WIDTH // 2 - 90, popup_y + 220, 180, 50)
        if quit_button.collidepoint(mouse_position):
            return False
        return True

    def handle_main_screen_click(self, mouse_position):
        systems = [
            ("Кровеносная система", GameState.CIRCULATORY),
            ("Нервная система", GameState.NERVOUS),
            ("Пищеварительная система", GameState.DIGESTIVE),
            ("Заболевания", GameState.DISEASE)
        ]
        for i, (_, state) in enumerate(systems):
            button = pygame.Rect(DisplayConstants.WIDTH // 2 - 150, 80 + i * 80, 300, 60)
            if button.collidepoint(mouse_position):
                self.game.state = state
                break

    def handle_system_specific_click(self, mouse_position):
        if self.game.state == GameState.CIRCULATORY:
            self._handle_circulatory_click(mouse_position)
        elif self.game.state == GameState.NERVOUS:
            self._handle_nervous_click(mouse_position)
        elif self.game.state == GameState.DIGESTIVE:
            self._handle_digestive_click(mouse_position)
        elif self.game.state == GameState.DISEASE:
            self.handle_disease_click(mouse_position)

    def _handle_circulatory_click(self, mouse_position):
        if self._is_button_clicked(mouse_position, 50):
            self.game.body.add_cell(CellType.WHITE_BLOOD)
        elif self._is_button_clicked(mouse_position, 120):
            self.game.body.fight_pathogens(CellType.WHITE_BLOOD)

    def _handle_nervous_click(self, mouse_position):
        if self._is_button_clicked(mouse_position, 50):
            self.game.body.stress_level = max(0, self.game.body.stress_level - 20)

    def _handle_digestive_click(self, mouse_position):
        # Кнопка "Принять пищу" по центру экрана
        button_width, button_height = 240, 60
        center_x = DisplayConstants.WIDTH // 2 - button_width // 2
        y_start = 220
        food_button = pygame.Rect(center_x, y_start, button_width, button_height)
        if food_button.collidepoint(mouse_position):
            self.game.body.add_nutrient(Nutrient.GLUCOSE, 20)
            self.game.body.add_nutrient(Nutrient.AMINO_ACIDS, 15)
        elif self._is_button_clicked(mouse_position, 120):
            self.game.body.add_nutrient(Nutrient.HORMONES, 10)

    def handle_disease_click(self, mouse_position):
        # Кнопка "Диагностика" или "Лечить" по центру экрана
        button_width, button_height = 240, 60
        center_x = DisplayConstants.WIDTH // 2 - button_width // 2
        y_start = 220
        if self.game.body.disease:
            heal_button = pygame.Rect(center_x, y_start, button_width, button_height)
            if heal_button.collidepoint(mouse_position):
                self.game.body.disease = None
        else:
            diagnose_button = pygame.Rect(center_x, y_start, button_width, button_height)
            if diagnose_button.collidepoint(mouse_position):
                self.game.start_educational_quest("Диабет")

    def _is_button_clicked(self, mouse_position, y_pos):
        return DisplayConstants.WIDTH - 200 <= mouse_position[0] <= DisplayConstants.WIDTH - 20 and y_pos <= mouse_position[1] <= y_pos + 50

    def handle_temperature_controls(self, mouse_position):
        pass

    def handle_return_to_menu(self, mouse_position):
        panel_height = 100
        menu_button = pygame.Rect(DisplayConstants.WIDTH - 100, DisplayConstants.HEIGHT - panel_height + 45, 80, 30)
        if menu_button.collidepoint(mouse_position):
            self.game.state = GameState.MAIN 

    def handle_main_gameplay_click(self, mouse_position):
        # Кнопки слева
        button_width, button_height = 220, 50
        start_x = 80
        y = 100
        gap = 20
        # Создать лейкоцит
        if pygame.Rect(start_x, y, button_width, button_height).collidepoint(mouse_position):
            self.game.body.add_cell(CellType.WHITE_BLOOD)
            return
        # Атаковать вирусы
        if pygame.Rect(start_x, y + button_height + gap, button_width, button_height).collidepoint(mouse_position):
            self.game.body.fight_pathogens(CellType.WHITE_BLOOD)
            return
        # Снизить стресс
        if pygame.Rect(start_x, y + 2 * (button_height + gap), button_width, button_height).collidepoint(mouse_position):
            self.game.body.stress_level = max(0, self.game.body.stress_level - 20)
            return
        # Принять пищу
        if pygame.Rect(start_x, y + 3 * (button_height + gap), button_width, button_height).collidepoint(mouse_position):
            self.game.body.add_nutrient(Nutrient.GLUCOSE, 20)
            self.game.body.add_nutrient(Nutrient.AMINO_ACIDS, 15)
            return
        # Диагностика/Лечить
        dz_btn_y = y + 4 * (button_height + gap)
        if self.game.body.disease:
            if pygame.Rect(start_x, dz_btn_y, button_width, button_height).collidepoint(mouse_position):
                self.game.body.disease = None
                return
        else:
            if pygame.Rect(start_x, dz_btn_y, button_width, button_height).collidepoint(mouse_position):
                self.game.start_educational_quest("Диабет")
                return
        # Кнопка меню (справа внизу панели)
        panel_height = 100
        menu_button = pygame.Rect(DisplayConstants.WIDTH - 120, DisplayConstants.HEIGHT - panel_height + 30, 100, 40)
        if menu_button.collidepoint(mouse_position):
            self.game.state = GameState.MENU
            return 
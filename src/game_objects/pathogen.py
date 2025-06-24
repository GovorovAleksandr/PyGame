import random
import pygame
import math
from constants.display_constants import DisplayConstants
from constants.game_object_constants import GameObjectConstants
from constants.game_balance_constants import GameBalanceConstants
from enums import PathogenType

class PathogenInfo:
    def __init__(self, color: tuple[int, int, int], description: str, draw_style: str):
        self.color = color
        self.description = description
        self.draw_style = draw_style

# Определение типов патогенов
VIRUS_INFO = PathogenInfo(
    color=(200, 50, 200),     # Фиолетовый
    description="Вирус (РНК/ДНК в белковой оболочке)",
    draw_style="spiky"        # С шипами
)

BACTERIA_INFO = PathogenInfo(
    color=(200, 200, 50),     # Желтый
    description="Бактерия (одноклеточный микроорганизм)",
    draw_style="smooth"       # Гладкий
)

PARASITE_INFO = PathogenInfo(
    color=(100, 200, 100),    # Зеленый
    description="Паразит (организм, живущий за счет хозяина)",
    draw_style="complex"      # Сложная форма
)

# Словарь соответствия типов и их информации
PATHOGEN_TYPE_INFO = {
    PathogenType.VIRUS: VIRUS_INFO,
    PathogenType.BACTERIA: BACTERIA_INFO,
    PathogenType.PARASITE: PARASITE_INFO
}

class Pathogen:
    # Представляет патоген (вирус, бактерию или паразита) в организме
    
    def __init__(self, x, y, pathogen_type):
        self.x = x
        self.y = y
        self.type = pathogen_type
        self.strength = random.randint(GameObjectConstants.PATHOGEN_STRENGTH_MIN, GameObjectConstants.PATHOGEN_STRENGTH_MAX)
        self.speed = random.uniform(GameObjectConstants.PATHOGEN_SPEED_MIN, GameObjectConstants.PATHOGEN_SPEED_MAX)
        self.target_x = None
        self.target_y = None
        self.info = PATHOGEN_TYPE_INFO[self.type]
        self.size = GameObjectConstants.PATHOGEN_SIZE

    def update(self, body_system):
        # Обновляет состояние патогена
        self.move_to_target()
        self.keep_in_bounds()
        self.damage_body(body_system)

    def move_to_target(self):
        if self.target_x is not None and self.target_y is not None:
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = (dx ** 2 + dy ** 2) ** 0.5
            
            if distance > self.speed:
                self.x += (dx / distance) * self.speed
                self.y += (dy / distance) * self.speed
            else:
                self.x = self.target_x
                self.y = self.target_y
                self.target_x = None
                self.target_y = None

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

    def keep_in_bounds(self):
        # Удержание патогена в границах экрана
        self.x = max(20, min(DisplayConstants.WIDTH - 230, self.x))
        self.y = max(20, min(DisplayConstants.HEIGHT - 120, self.y))

    def damage_body(self, body_system):
        # Нанесение урона организму
        body_system.health = max(0, min(100, 
            body_system.health - GameBalanceConstants.PATHOGEN_IMPACT_FACTOR * self.strength))

    def draw(self, screen):
        # Отрисовка патогена
        color = self.info.color
        center = (int(self.x), int(self.y))
        
        # Основная форма патогена
        pygame.draw.circle(screen, color, center, self.size)
        
        # Дополнительные элементы в зависимости от типа
        if self.info.draw_style == "spiky":
            self.draw_spikes(screen, color, center)
    
    def draw_spikes(self, screen, color, center):
        # Отрисовка шипов для вирусов
        for i in range(6):
            angle = i * math.pi / 3
            spike_end = (
                center[0] + math.cos(angle) * (self.size + 5),
                center[1] + math.sin(angle) * (self.size + 5)
            )
            pygame.draw.line(screen, color, center, spike_end, 2) 
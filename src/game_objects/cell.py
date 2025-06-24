import random
import pygame
from constants import GameObjectConstants, DisplayConstants
from enums import CellType, Nutrient

class CellInfo:
    def __init__(self, color: tuple[int, int, int], function: str):
        self.color = color
        self.function = function

# Определение типов клеток
RED_BLOOD_INFO = CellInfo(
    color=(220, 60, 60),      # Красный
    function="Перенос кислорода"
)

WHITE_BLOOD_INFO = CellInfo(
    color=(240, 240, 240),    # Белый
    function="Борьба с инфекцией"
)

NEURON_INFO = CellInfo(
    color=(65, 105, 225),     # Синий
    function="Передача нервных импульсов"
)

MUSCLE_INFO = CellInfo(
    color=(218, 165, 32),     # Золотой
    function="Сокращение и движение"
)

LIVER_INFO = CellInfo(
    color=(147, 112, 219),    # Фиолетовый
    function="Обработка питательных веществ"
)

# Словарь соответствия типов и их информации
CELL_TYPE_INFO = {
    CellType.RED_BLOOD: RED_BLOOD_INFO,
    CellType.WHITE_BLOOD: WHITE_BLOOD_INFO,
    CellType.NEURON: NEURON_INFO,
    CellType.MUSCLE: MUSCLE_INFO,
    CellType.LIVER: LIVER_INFO
}

class Cell:
    # Представляет клетку организма с определенным типом и функциями
    
    def __init__(self, x, y, cell_type):
        # Позиция клетки
        self.x = x
        self.y = y
        self.target_x = None
        self.target_y = None
        
        # Характеристики клетки
        self.type = cell_type
        self.info = CELL_TYPE_INFO[cell_type]
        self.size = GameObjectConstants.CELL_SIZE
        self.energy = 100
        self.speed = random.uniform(GameObjectConstants.CELL_SPEED_MIN, GameObjectConstants.CELL_SPEED_MAX)

    def update(self, body_system):
        # Обновляет состояние клетки
        self.move_to_target()
        self.consume_energy()
        self.perform_function(body_system)
        self.keep_in_bounds()

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

    def consume_energy(self):
        # Расходует энергию клетки
        self.energy = max(0, self.energy - 0.01)

    def perform_function(self, body_system):
        # Выполняет функцию клетки в зависимости от её типа
        if self.type == CellType.LIVER:
            body_system.nutrients[Nutrient.AMINO_ACIDS] = min(100, int(body_system.nutrients[Nutrient.AMINO_ACIDS] + 0.03))

    def draw(self, screen):
        # Отрисовывает клетку на экране
        color = self.info.color
        
        # Рисуем внешний круг
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        
        # Рисуем внутренний круг
        inner_color = (color[0] // 2, color[1] // 2, color[2] // 2)
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), self.size // 2)

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

    def keep_in_bounds(self):
        # Удержание клетки в границах экрана
        self.x = max(20, min(DisplayConstants.WIDTH - 230, self.x))
        self.y = max(20, min(DisplayConstants.HEIGHT - 120, self.y)) 
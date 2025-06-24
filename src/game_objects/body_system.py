import random
from typing import Optional
from constants.display_constants import DisplayConstants
from constants.game_object_constants import GameObjectConstants
from constants.game_balance_constants import GameBalanceConstants
from enums import Nutrient, CellType, PathogenType
from game_objects.cell import Cell
from game_objects.disease import Disease
from game_objects.pathogen import Pathogen
from game_objects.stimulus import Stimulus

class BodySystem:
    # Биологическая система организма, управляет состоянием
    
    def __init__(self):
        self.setup_vital_signs()
        self.setup_nutrients()
        self.setup_organisms()
        self.generate_initial_cells()
        self._tick_timer = 0.0

    def setup_vital_signs(self):
        # Установка жизненных показателей
        self.health = 100
        self.energy = 100
        self.stress_level = 0

    def setup_nutrients(self):
        # Установка уровней питательных веществ
        self.nutrients = {nutrient: 100 for nutrient in Nutrient}

    def setup_organisms(self):
        # Инициализация живых организмов
        self.cells = []           # Клетки организма
        self.pathogens = []       # Вредные микроорганизмы
        self.disease: Optional[Disease] = None  # Текущая болезнь
        self.stimuli = []         # Внешние раздражители

    def generate_initial_cells(self):
        # Создание начальных клеток
        for _ in range(GameObjectConstants.INITIAL_CELLS):
            cell_position = self.get_random_position()
            cell_type = random.choice(list(CellType))
            self.cells.append(Cell(cell_position[0], cell_position[1], cell_type))

    def get_random_position(self):
        # Получение случайной позиции в пределах игрового поля
        x = random.randint(50, DisplayConstants.WIDTH - 250)
        y = random.randint(50, DisplayConstants.HEIGHT - 150)
        return x, y

    def update(self, dt):
        # Обновление состояния организма
        self._tick_timer += dt
        if self._tick_timer >= 1.0:
            self._tick_timer -= 1.0
            # Постепенное случайное увеличение стресса
            if random.random() < 0.2:
                base_stress = 0.5
                if self.disease:
                    extra = self.disease.severity * 2
                    self.stress_level = min(100, self.stress_level + base_stress + extra)
                else:
                    self.stress_level = min(100, self.stress_level + base_stress)
            self.update_cells()
            self.update_nutrients()
            self.update_pathogens()
            self.update_stimuli()
            self.update_health()

    def update_cells(self):
        # Обновление состояния клеток
        for cell in self.cells:
            cell.update(self)

    def update_nutrients(self):
        # Обновление уровня питательных веществ
        # Расходуем только глюкозу
        self.nutrients[Nutrient.GLUCOSE] = max(0, min(100, int(self.nutrients[Nutrient.GLUCOSE] - GameBalanceConstants.NUTRIENT_CONSUMPTION_GLUCOSE / 10)))
        # Гормоны производятся при стрессе
        if self.stress_level > 30:
            self.nutrients[Nutrient.HORMONES] = min(100, int(self.nutrients[Nutrient.HORMONES] + GameBalanceConstants.HORMONE_PRODUCTION_AMOUNT))
        # Энергия
        if self.has_enough_nutrients():
            self.energy = min(100, self.energy + GameBalanceConstants.ENERGY_INCREASE_AMOUNT)
        else:
            self.energy = max(0, self.energy - GameBalanceConstants.ENERGY_DECREASE_AMOUNT)

    def has_enough_nutrients(self):
        # Проверка достаточности питательных веществ
        return all(self.nutrients[nutrient] > GameBalanceConstants.ENERGY_BALANCE_THRESHOLD for nutrient in self.nutrients)

    def update_pathogens(self):
        # Обновление состояния патогенов
        # Обновление существующих патогенов
        for pathogen in self.pathogens[:]:
            pathogen.update(self)
            if pathogen.strength <= 0:
                self.pathogens.remove(pathogen)

        # Появление новых патогенов
        if (random.random() < GameBalanceConstants.PATHOGEN_APPEARANCE_PROBABILITY and 
            len(self.pathogens) < GameObjectConstants.MAX_PATHOGENS):
            position = self.get_random_position()
            pathogen_type = random.choice(list(PathogenType))
            self.pathogens.append(Pathogen(position[0], position[1], pathogen_type))

    def update_stimuli(self):
        # Обновление внешних раздражителей
        # Удаление истекших стимулов
        for stimulus in self.stimuli[:]:
            stimulus.duration -= 1
            if stimulus.duration <= 0:
                self.stimuli.remove(stimulus)

        # Появление новых стимулов
        if (random.random() < GameBalanceConstants.STIMULUS_APPEARANCE_PROBABILITY and 
            len(self.stimuli) < GameObjectConstants.MAX_STIMULI):
            position = self.get_random_position()
            from game_objects.stimulus import ALL_STIMULUS_TYPES
            stimulus_type = random.choice(ALL_STIMULUS_TYPES)
            self.stimuli.append(Stimulus(position[0], position[1], stimulus_type))

    def update_health(self):
        # Обновление уровня здоровья
        if self.disease:
            if not self.disease.update(self):
                self.disease = None

    def add_cell(self, cell_type):
        # Добавляет клетку указанного типа в случайную позицию
        pos = self.get_random_position()
        self.cells.append(Cell(pos[0], pos[1], cell_type))

    def fight_pathogens(self, cell_type):
        # Борьба с патогенами определённым типом клеток
        if cell_type == CellType.WHITE_BLOOD:
            # Все лейкоциты атакуют всех патогенов
            for pathogen in self.pathogens[:]:
                pathogen.strength -= GameObjectConstants.PATHOGEN_STRENGTH_DECREASE * 3  # Усиленная атака
                if pathogen.strength <= 0:
                    self.pathogens.remove(pathogen)
        else:
            for pathogen in self.pathogens:
                for cell in self.cells:
                    if cell.type == cell_type:
                        distance = ((cell.x - pathogen.x) ** 2 + (cell.y - pathogen.y) ** 2) ** 0.5
                        if distance < GameObjectConstants.CELL_FIGHT_DISTANCE:
                            pathogen.strength -= GameObjectConstants.PATHOGEN_STRENGTH_DECREASE

    def add_nutrient(self, nutrient, amount):
        if hasattr(self, 'nutrients') and nutrient in self.nutrients:
            self.nutrients[nutrient] = min(100, max(0, self.nutrients[nutrient] + amount)) 
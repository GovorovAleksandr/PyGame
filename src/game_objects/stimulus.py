import random
from constants import GameObjectConstants, GameBalanceConstants
from enums import Nutrient

class StimulusEffect:
    def __init__(self, glucose: float = 0.0, stress: float = 0.0, hormones: float = 0.0, energy: float = 0.0):
        self.glucose = glucose
        self.stress = stress
        self.hormones = hormones
        self.energy = energy

class StimulusType:
    def __init__(self, name: str, effects: StimulusEffect, description: tuple[str, str]):
        self.name = name
        self.effects = effects
        self.description = description

# Определение типов стимулов
COLD = StimulusType(
    name="Холод",
    effects=StimulusEffect(glucose=-0.1, stress=0.1),
    description=("Увеличивает метаболизм", "Снижает иммунитет")
)

STRESS = StimulusType(
    name="Стресс",
    effects=StimulusEffect(stress=0.2, hormones=0.15, glucose=0.1),
    description=("Высвобождает адреналин", "Подавляет пищеварение")
)

EXERCISE = StimulusType(
    name="Физическая нагрузка",
    effects=StimulusEffect(glucose=-0.15, energy=-0.15),
    description=("Сжигает глюкозу", "Утомляет")
)

# Список всех типов стимулов
ALL_STIMULUS_TYPES = [COLD, STRESS, EXERCISE]

class Stimulus:
    # Представляет внешний раздражитель, влияющий на организм
    
    def __init__(self, x, y, stimulus_type):
        self.x = x
        self.y = y
        self.stimulus_type = stimulus_type
        self.duration = random.randint(GameObjectConstants.STIMULUS_DURATION_MIN, GameObjectConstants.STIMULUS_DURATION_MAX)
        self.intensity = random.uniform(GameObjectConstants.STIMULUS_INTENSITY_MIN, GameObjectConstants.STIMULUS_INTENSITY_MAX)

    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            return True
        return False

    def apply_effect(self, body_system):
        if not hasattr(self, 'stimulus_type'):
            return
        effects = self.stimulus_type.effects
        if effects.glucose != 0:
            body_system.nutrients[Nutrient.GLUCOSE] = max(0, min(100, int(body_system.nutrients[Nutrient.GLUCOSE] + effects.glucose * self.intensity)))
        if effects.stress != 0:
            body_system.stress_level = max(0, min(100, body_system.stress_level + effects.stress * self.intensity))
        if effects.hormones != 0:
            body_system.nutrients[Nutrient.HORMONES] = max(0, min(100, int(body_system.nutrients[Nutrient.HORMONES] + effects.hormones * self.intensity)))
        if effects.energy != 0:
            body_system.energy = max(0, min(100, body_system.energy + effects.energy * self.intensity)) 
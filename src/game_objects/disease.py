import random
from constants import GameObjectConstants, GameBalanceConstants
from enums import Nutrient, PathogenType
from game_objects.pathogen import Pathogen

class DiseaseEffect:
    def __init__(self, glucose: float = 0.0, energy: float = 0.0, stress: float = 0.0, immune: float = 0.0):
        self.glucose = glucose
        self.energy = energy
        self.stress = stress
        self.immune = immune

class DiseaseType:
    def __init__(self, name: str, description: str, treatment: str, effects: DiseaseEffect):
        self.name = name
        self.description = description
        self.treatment = treatment
        self.effects = effects

# Определение типов заболеваний
DIABETES = DiseaseType(
    name="Диабет",
    description="Нарушение обмена глюкозы из-за недостатка инсулина",
    treatment="Инсулинотерапия, диета, физические упражнения",
    effects=DiseaseEffect(glucose=0.2, energy=-0.1)
)

HYPERTENSION = DiseaseType(
    name="Гипертония",
    description="Повышенное кровяное давление в артериях",
    treatment="Гипотензивные препараты, снижение соли, снижение веса",
    effects=DiseaseEffect(stress=0.15)
)

ANEMIA = DiseaseType(
    name="Анемия",
    description="Дефицит красных кровяных клеток или гемоглобина",
    treatment="Препараты железа, витамин B12, фолиевая кислота",
    effects=DiseaseEffect()
)

ALLERGY = DiseaseType(
    name="Аллергия",
    description="Чрезмерная реакция иммунной системы на безвредные вещества",
    treatment="Антигистаминные препараты, избегание аллергенов",
    effects=DiseaseEffect(immune=-0.1)
)

# Список всех типов заболеваний
ALL_DISEASE_TYPES = [DIABETES, HYPERTENSION, ANEMIA, ALLERGY]

class Disease:
    # Представляет заболевание с определенными симптомами и влиянием на организм
    
    def __init__(self, disease_type):
        self.disease_type = disease_type
        self.name = disease_type.name
        self.severity = random.uniform(GameObjectConstants.DISEASE_SEVERITY_MIN, GameObjectConstants.DISEASE_SEVERITY_MAX)
        self.duration = random.randint(GameObjectConstants.DISEASE_DURATION_MIN, GameObjectConstants.DISEASE_DURATION_MAX)
        self.descriptions = {
            "Диабет": "Нарушение обмена веществ, при котором организм не может правильно использовать глюкозу.",
            "Грипп": "Острое вирусное заболевание, поражающее дыхательные пути.",
            "Гастрит": "Воспаление слизистой оболочки желудка.",
            "Аллергия": "Повышенная чувствительность иммунной системы к определенным веществам."
        }
        self.progress = 0

    def update(self, body_system):
        # Обновляет влияние болезни на организм
        self.progress += 1
        if self.progress >= self.duration:
            return False

        self.apply_effects(body_system)
        return True

    def apply_effects(self, body_system):
        # Применяет эффекты болезни к организму
        effects = self.disease_type.effects
        
        if effects.glucose != 0:
            body_system.nutrients[Nutrient.GLUCOSE] = min(100, 
                int(body_system.nutrients[Nutrient.GLUCOSE] + effects.glucose * self.severity))
        
        if effects.energy != 0:
            body_system.energy = max(0, min(100, 
                body_system.energy + effects.energy * self.severity))
        
        if effects.stress != 0:
            body_system.stress_level = min(100, 
                body_system.stress_level + effects.stress * self.severity)
        
        if effects.immune != 0 and random.random() < 0.01:
            pos = body_system.get_random_position()
            pathogen_type = random.choice(list(PathogenType))
            body_system.pathogens.append(Pathogen(pos[0], pos[1], pathogen_type)) 
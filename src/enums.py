from enum import Enum

class GameState(Enum):
    MENU = -1
    MAIN = 0
    CIRCULATORY = 1
    NERVOUS = 2
    DIGESTIVE = 3
    DISEASE = 4
    GAME_OVER = 5


class Nutrient(Enum):
    GLUCOSE = 0
    AMINO_ACIDS = 1
    HORMONES = 2


class PathogenType(Enum):
    VIRUS = 0
    BACTERIA = 1
    PARASITE = 2


class CellType(Enum):
    RED_BLOOD = 0
    WHITE_BLOOD = 1
    NEURON = 2
    MUSCLE = 3
    LIVER = 4 
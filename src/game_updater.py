import random
from constants import GameBalanceConstants
from enums import GameState
from game_objects.disease import Disease

class GameUpdater:
    def __init__(self, game):
        self.game = game

    def update(self, dt):
        # Обновление игровой логики
        if self.game.state != GameState.MENU:
            self.update_body_system(dt)
            self.check_game_over()

    def update_body_system(self, dt):
        # Обновление состояния организма
        self.game.body.update(dt)

        if self.game.body.disease:
            if not self.game.body.disease.update(self.game.body):
                self.game.body.disease = None

        for stimulus in self.game.body.stimuli:
            stimulus.apply_effect(self.game.body)

        if self.game.educational_quest and self.game.quest_progress < 100:
            self.game.quest_progress += 0.01

    def check_game_over(self):
        # Проверка условий окончания игры
        if self.game.body.health <= GameBalanceConstants.GAME_OVER_HEALTH_THRESHOLD:
            self.game.state = GameState.GAME_OVER
            self.show_game_over_popup("Здоровье")
        elif self.game.body.energy <= GameBalanceConstants.GAME_OVER_ENERGY_THRESHOLD:
            self.game.state = GameState.GAME_OVER
            self.show_game_over_popup("Энергия")

    def show_game_over_popup(self, reason):
        # Отображение сообщения о конце игры
        print(f"Игра окончена! Причина: {reason} опустилось до критического уровня.") 
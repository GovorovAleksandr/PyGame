import pygame
import sys
from game import Game

def main():
    # Главная функция игры, управляет игровым циклом и инициализацией
    pygame.init()
    
    window = create_game_window()
    game = Game()
    game_clock = pygame.time.Clock()
    
    run_game_loop(window, game, game_clock)
    
    close_game()

def create_game_window():
    # Создает и настраивает игровое окно
    window_size = (1000, 700)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption("Биология Человека")
    return window

def run_game_loop(window, game, clock):
    # Основной игровой цикл
    is_running = True
    prev_time = pygame.time.get_ticks() / 1000.0
    while is_running:
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - prev_time
        prev_time = current_time
        is_running = process_game_frame(window, game, dt)
        clock.tick(60)

def process_game_frame(window, game, dt=None):
    # Обрабатывает один кадр игры
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        game.handle_event(event)
    if dt is None:
        dt = 1/60
    game.update(dt)
    game.draw(window)
    pygame.display.flip()
    return True

def close_game():
    # Закрывает игру и освобождает ресурсы
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main() 
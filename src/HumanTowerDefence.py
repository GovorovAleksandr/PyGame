import pygame
import sys
import random
import math
from pygame.locals import *
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 120, 255)
RED = (255, 50, 50)
GREEN = (50, 200, 50)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
PURPLE = (180, 50, 230)
ORANGE = (255, 165, 0)
LIGHT_BLUE = (100, 200, 255)

# Состояния игры
MENU = 0
TUTORIAL = 1
PLAYING = 2
SHOP = 3
GAME_OVER = 4
VICTORY = 5

# Создание экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Human TowerDefence")
clock = pygame.time.Clock()

# Шрифты
title_font = pygame.font.SysFont("Arial", 64, bold=True)
large_font = pygame.font.SysFont("Arial", 48, bold=True)
medium_font = pygame.font.SysFont("Arial", 36)
small_font = pygame.font.SysFont("Arial", 22)
tiny_font = pygame.font.SysFont("Arial", 18)
extra_tiny_font = pygame.font.SysFont("Arial", 12)

def resource_path(relative_path):
    """ Получить абсолютный путь к ресурсу, работает для dev и для PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Button:
    def __init__(self, x, y, width, height, text, color=GREEN, hover_color=(100, 255, 100)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        # Для shop_button и music_button используем extra_tiny_font
        if self.text in ["Магазин", "Включить музыку", "Выключить музыку", "Включить звуки", "Выключить звуки"]:
            text_surf = extra_tiny_font.render(self.text, True, BLACK)
        else:
            text_surf = medium_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class Unit(pygame.sprite.Sprite):
    def __init__(self, x, y, unit_type, anims=None):
        super().__init__()
        self.unit_type = unit_type
        self.radius = 25
        self.health = 100
        self.max_health = 100
        self.speed = 1.5
        self.attack_power = 10
        self.attack_range = 100
        self.attack_cooldown = 0
        self.cooldown_time = 30
        self.target = None
        self.shielded = False
        self.state = 'run'  # run, punch, death
        self.anim_frame = 0
        self.anim_timer = 0
        self.anims = anims if anims else {}
        self.dead_anim_played = False
        self.anim_data = {
            'run': {'sheet': self.anims.get('run'), 'frames': 18, 'w': 128, 'h': 128},
            'punch': {'sheet': self.anims.get('punch'), 'frames': 29, 'w': 128, 'h': 128},
            'death': {'sheet': self.anims.get('death'), 'frames': 103, 'w': 128, 'h': 128},
        } if self.anims else None

        # Определение характеристик по типу юнита
        if unit_type == "Нейтрофил":
            self.color = LIGHT_BLUE
            self.speed = 2.0 * 0.7
            self.health = int(100 * 0.5)
            self.max_health = int(100 * 0.5)
            self.attack_power = 15
            self.cooldown_time = 20
            self.cost = 10
            # Анимация
            if self.anim_data is not None:
                self.image = self.get_anim_frame('run', 0)
            # Маска для pixel-perfect хитбокса
            self.mask = pygame.mask.from_surface(self.image)
        elif unit_type == "Макрофаг":
            self.color = GRAY
            self.radius = 35
            self.health = int(150 * 0.5)
            self.max_health = int(150 * 0.5)
            self.speed = 1.0 * 0.7
            self.attack_power = 20
            self.cooldown_time = 40
            self.cost = 30
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
            text = "M"
            text_surf = small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(self.radius, self.radius))
            self.image.blit(text_surf, text_rect)
        elif unit_type == "В-лимфоцит":
            self.color = GREEN
            self.attack_range = 150
            self.health = int(100 * 0.5)
            self.max_health = int(100 * 0.5)
            self.attack_power = 12
            self.cooldown_time = 25
            self.speed = 1.5 * 0.7
            self.cost = 25
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
            text = "B"
            text_surf = small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(self.radius, self.radius))
            self.image.blit(text_surf, text_rect)
        elif unit_type == "Т-киллер":
            self.color = ORANGE
            self.health = int(100 * 0.5)
            self.max_health = int(100 * 0.5)
            self.attack_power = 35
            self.cooldown_time = 50
            self.speed = 1.5 * 0.7
            self.cost = 40
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
            text = "T"
            text_surf = small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(self.radius, self.radius))
            self.image.blit(text_surf, text_rect)
        elif unit_type == "NK-клетка":
            self.color = PURPLE
            self.health = int(100 * 0.5)
            self.max_health = int(100 * 0.5)
            self.attack_power = 40
            self.cooldown_time = 45
            self.speed = 1.5 * 0.7
            self.cost = 50
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
            text = "NK"
            text_surf = small_font.render(text, True, BLACK)
            text_rect = text_surf.get_rect(center=(self.radius, self.radius))
            self.image.blit(text_surf, text_rect)

        if unit_type != "Нейтрофил":
            self.rect = self.image.get_rect(center=(x, y))
        else:
            self.rect = self.image.get_rect(center=(x, y))
        self.target_x = 50

    def get_anim_frame(self, state, frame):
        if self.anim_data is None:
            return self.image
        data = self.anim_data[state]
        sheet = data['sheet']
        w, h = data['w'], data['h']
        frames_per_row = 10
        x = (frame % frames_per_row) * w
        y = (frame // frames_per_row) * h
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(sheet, (0, 0), (x, y, w, h))
        return surf

    def update(self, enemies, enemy_base=None):
        if self.unit_type == "Нейтрофил":
            # Смерть
            if self.health <= 0:
                if not self.dead_anim_played:
                    self.state = 'death'
                    self.anim_frame += 1
                    if self.anim_frame >= self.anim_data['death']['frames']:
                        self.dead_anim_played = True
                        self.kill()
                    else:
                        self.image = self.get_anim_frame('death', min(self.anim_frame, self.anim_data['death']['frames']-1))
                        self.mask = pygame.mask.from_surface(self.image)  # обновляем маску
                return
            # Атака
            if self.target and self.distance_to(self.target) <= self.attack_range:
                if self.attack_cooldown <= 0:
                    self.state = 'punch'
                    self.anim_frame = 0
                    self.attack()
                    self.attack_cooldown = self.cooldown_time
                else:
                    self.attack_cooldown -= 1
                # Анимация удара
                if self.state == 'punch':
                    self.anim_timer += 1
                    if self.anim_timer % 2 == 0:
                        self.anim_frame += 1
                    if self.anim_frame >= self.anim_data['punch']['frames']:
                        self.state = 'run'
                        self.anim_frame = 0
                    self.image = self.get_anim_frame('punch' if self.state=='punch' else 'run', self.anim_frame)
                    self.mask = pygame.mask.from_surface(self.image)  # обновляем маску
                else:
                    if self.anim_data is not None:
                        self.anim_timer += 1
                        if self.anim_timer % 3 == 0:
                            self.anim_frame = (self.anim_frame + 1) % self.anim_data['run']['frames']
                        self.image = self.get_anim_frame('run', self.anim_frame)
                        self.mask = pygame.mask.from_surface(self.image)  # обновляем маску
                # Движение к базе врага
                if self.rect.centerx < SCREEN_WIDTH - 100:
                    self.rect.x += int(self.speed)
                # Атака базы врага, если нет врагов рядом
                if enemy_base and self.rect.colliderect(enemy_base.rect):
                    if self.attack_cooldown <= 0:
                        self.state = 'punch'
                        self.anim_frame = 0
                        enemy_base.take_damage(self.attack_power)
                        self.attack_cooldown = self.cooldown_time
                    else:
                        self.attack_cooldown -= 1
            else:
                # Движение
                self.state = 'run'
                self.anim_timer += 1
                if self.anim_data is not None:
                    if self.anim_timer % 3 == 0:
                        self.anim_frame = (self.anim_frame + 1) % self.anim_data['run']['frames']
                    self.image = self.get_anim_frame('run', self.anim_frame)
                self.mask = pygame.mask.from_surface(self.image)  # обновляем маску
                # Движение к базе врага
                if self.rect.centerx < SCREEN_WIDTH - 100:
                    self.rect.x += int(self.speed)
                # Атака базы врага, если нет врагов рядом
                if enemy_base and self.rect.colliderect(enemy_base.rect):
                    if self.attack_cooldown <= 0:
                        self.state = 'punch'
                        self.anim_frame = 0
                        enemy_base.take_damage(self.attack_power)
                        self.attack_cooldown = self.cooldown_time
                    else:
                        self.attack_cooldown -= 1
            # Поиск цели
            if not self.target or not self.target.alive() or self.distance_to(self.target) > self.attack_range:
                self.find_target(enemies)
        else:
            # Поиск цели
            if not self.target or not self.target.alive() or self.distance_to(self.target) > self.attack_range:
                self.find_target(enemies)
            # Атака цели
            if self.target and self.distance_to(self.target) <= self.attack_range:
                if self.attack_cooldown <= 0:
                    self.attack()
                    self.attack_cooldown = self.cooldown_time
                else:
                    self.attack_cooldown -= 1
            elif any(self.rect.colliderect(enemy.rect) for enemy in enemies):
                pass
            elif enemy_base and self.rect.colliderect(enemy_base.rect):
                if self.attack_cooldown <= 0:
                    self.state = 'run'
                    enemy_base.take_damage(self.attack_power)
                    self.attack_cooldown = self.cooldown_time
                else:
                    self.attack_cooldown -= 1
            elif enemy_base and self.rect.right > enemy_base.rect.left and self.rect.colliderect(enemy_base.rect):
                pass
            elif self.rect.centerx < SCREEN_WIDTH - 100:
                self.state = 'run'
                self.anim_timer += 1
                if self.anim_data is not None:
                    if self.anim_timer % 3 == 0:
                        self.anim_frame = (self.anim_frame + 1) % self.anim_data['run']['frames']
                    self.image = self.get_anim_frame('run', self.anim_frame)
                self.rect.x += int(self.speed)

    def find_target(self, enemies):
        closest = None
        min_dist = float('inf')

        for enemy in enemies:
            dist = self.distance_to(enemy)
            if dist < min_dist and dist <= self.attack_range:
                min_dist = dist
                closest = enemy

        self.target = closest

    def distance_to(self, target):
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        return math.sqrt(dx * dx + dy * dy)

    def attack(self):
        if self.target:
            self.target.take_damage(self.attack_power)

    def take_damage(self, damage):
        if not self.shielded:
            self.health -= damage
            return self.health <= 0
        return False

    def draw_health_bar(self, surface):
        bar_width = 50
        bar_height = 5
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 10

        # Фон полосы здоровья
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # Здоровье
        health_width = (self.health / self.max_health) * bar_width
        health_color = GREEN  # Всегда зелёный для своих юнитов
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))

        # Щит
        if self.shielded:
            shield_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 5,
                                      self.rect.width + 10, self.rect.height + 10)
            pygame.draw.rect(surface, BLUE, shield_rect, 2)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type, anims=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.health = 100
        self.max_health = 100
        self.speed = 1.0
        self.attack_power = 5
        self.attack_cooldown = 0
        self.cooldown_time = 60
        self.state = 'run'  # run, attack
        self.anim_frame = 0
        self.anim_timer = 0
        self.anims = anims if anims else {}
        self.anim_data = {
            'run': {'sheet': self.anims.get('run'), 'frames': 24, 'w': 128, 'h': 128},
            'attack': {'sheet': self.anims.get('attack'), 'frames': 95, 'w': 128, 'h': 128},
        } if self.anims else None
        self.dead_anim_played = False
        self.image = None  # <-- гарантируем, что атрибут есть

        # Определение характеристик по типу врага
        if enemy_type == "Бактерия":
            self.color = RED
            self.size = 20
            self.health = int(80 * 1.5)
            self.max_health = int(80 * 1.5)
            self.speed = 1.2
            self.attack_power = int(4 * 1.25 * 2)
            self.reward = 200
            # Анимация barbarian
            if self.anims:
                self.state = 'run'
                self.anim_frame = 0
                self.anim_timer = 0
                frame_img = self.get_anim_frame('run', 0)
                if frame_img is None:
                    frame_img = pygame.Surface((128, 128), pygame.SRCALPHA)
                fixed_surf = pygame.Surface((128, 128), pygame.SRCALPHA)
                # Отзеркаливаем по горизонтали для бега
                frame_img = pygame.transform.flip(frame_img, True, False)
                # Уменьшаем в 1.5 раза (до ~85x85)
                frame_img = pygame.transform.smoothscale(frame_img, (85, 85))
                fx = (128 - frame_img.get_width()) // 2
                fy = (128 - frame_img.get_height()) // 2
                fixed_surf.blit(frame_img, (fx, fy))
                self.image = fixed_surf
                self.rect = self.image.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 + random.randint(-100, 100)))
            else:
                self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
                pygame.draw.rect(self.image, self.color,
                                 (0, 0, self.size * 2, self.size * 2), border_radius=5)
                self.rect = self.image.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 + random.randint(-100, 100)))
        elif enemy_type == "Вирус гриппа":
            self.color = RED
            self.size = 25
            self.health = int(70 * 1.5)
            self.max_health = int(70 * 1.5)
            self.speed = 1.5
            self.attack_power = int(3 * 1.25 * 2)
            self.reward = 300
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            points = [
                (self.size, 0),
                (self.size * 2, self.size),
                (self.size * 1.5, self.size * 2),
                (self.size * 0.5, self.size * 2),
                (0, self.size)
            ]
            pygame.draw.polygon(self.image, self.color, points)
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 + random.randint(-100, 100)))
        elif enemy_type == "ВИЧ":
            self.color = RED
            self.size = 30
            self.health = int(120 * 1.5)
            self.max_health = int(120 * 1.5)
            self.speed = 0.8
            self.attack_power = int(7 * 1.25 * 2)
            self.reward = 400
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, self.color, [
                (self.size, 0),
                (self.size * 2, self.size * 0.5),
                (self.size * 1.5, self.size * 2),
                (self.size * 0.5, self.size * 2),
                (0, self.size * 0.5)
            ])
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 + random.randint(-100, 100)))
        elif enemy_type == "Раковая клетка":
            self.color = (50, 50, 50)
            self.size = 40
            self.health = int(200 * 1.5)
            self.max_health = int(200 * 1.5)
            self.speed = 0.6
            self.attack_power = int(10 * 1.25 * 2)
            self.reward = 600
            self.image = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (self.size, self.size), self.size)
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 + random.randint(-100, 100)))
        # Если вдруг не создали image (неизвестный тип врага)
        if self.image is None:
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 0, 255), (20, 20), 20)
        # Гарантируем, что у любого врага есть self.rect
        if not hasattr(self, 'rect'):
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT // 2 + random.randint(-100, 100)))
        self.target_x = 50

    def get_anim_frame(self, state, frame):
        if self.anim_data is None:
            return self.image
        data = self.anim_data[state]
        sheet = data['sheet']
        w, h = data['w'], data['h']
        frames_per_row = sheet.get_width() // w
        x = (frame % frames_per_row) * w
        y = (frame // frames_per_row) * h
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        surf.blit(sheet, (0, 0), (x, y, w, h))
        return surf

    def update(self, player_base, units=None):
        if self.enemy_type == "Бактерия" and self.anim_data:
            blocked = False
            if units:
                for unit in units:
                    if self.rect.colliderect(unit.rect):
                        blocked = True
                        # Атака юнита
                        if self.attack_cooldown <= 0:
                            self.state = 'attack'
                            self.anim_frame = 0
                            unit.take_damage(self.attack_power)
                            self.attack_cooldown = self.cooldown_time
                        else:
                            self.attack_cooldown -= 1
            if not blocked and not self.rect.colliderect(player_base.rect) and self.rect.centerx > self.target_x:
                self.state = 'run'
                self.anim_timer += 1
                if self.anim_timer % 3 == 0:
                    self.anim_frame = (self.anim_frame + 1) % self.anim_data['run']['frames']
                frame_img = self.get_anim_frame('run', self.anim_frame)
                # Отзеркаливаем по горизонтали для бега
                frame_img = pygame.transform.flip(frame_img, True, False)
                # Уменьшаем в 1.5 раза (до ~85x85)
                frame_img = pygame.transform.smoothscale(frame_img, (85, 85))
                if frame_img is None:
                    frame_img = pygame.Surface((128, 128), pygame.SRCALPHA)
                fixed_surf = pygame.Surface((128, 128), pygame.SRCALPHA)
                fx = (128 - frame_img.get_width()) // 2
                fy = (128 - frame_img.get_height()) // 2
                fixed_surf.blit(frame_img, (fx, fy))
                self.image = fixed_surf
                self.rect.x = int(self.rect.x - self.speed)
            elif self.rect.colliderect(player_base.rect):
                if self.attack_cooldown <= 0:
                    self.state = 'attack'
                    self.anim_frame = 0
                    player_base.take_damage(self.attack_power)
                    self.attack_cooldown = self.cooldown_time
                else:
                    self.attack_cooldown -= 1
            # Анимация атаки
            if self.state == 'attack':
                self.anim_timer += 1
                if self.anim_timer % 2 == 0:
                    self.anim_frame += 1
                if self.anim_frame >= self.anim_data['attack']['frames']:
                    self.state = 'run'
                    self.anim_frame = 0
                frame_img = self.get_anim_frame('attack' if self.state == 'attack' else 'run', self.anim_frame)
                if frame_img is None:
                    frame_img = pygame.Surface((128, 128), pygame.SRCALPHA)
                fixed_surf = pygame.Surface((128, 128), pygame.SRCALPHA)
                # Отзеркаливаем по горизонтали для бега
                frame_img = pygame.transform.flip(frame_img, True, False)
                fx = (128 - frame_img.get_width()) // 2
                fy = (128 - frame_img.get_height()) // 2
                fixed_surf.blit(frame_img, (fx, fy))
                self.image = fixed_surf
        else:
            # старое поведение для других врагов
            blocked = False
            if units:
                for unit in units:
                    if self.rect.colliderect(unit.rect):
                        blocked = True
                        if self.attack_cooldown <= 0:
                            unit.take_damage(self.attack_power)
                            self.attack_cooldown = self.cooldown_time
                        else:
                            self.attack_cooldown -= 1
            if not blocked and not self.rect.colliderect(player_base.rect) and self.rect.centerx > self.target_x:
                self.rect.x = int(self.rect.x - self.speed)
            if self.rect.colliderect(player_base.rect):
                if self.attack_cooldown <= 0:
                    player_base.take_damage(self.attack_power)
                    self.attack_cooldown = self.cooldown_time
                else:
                    self.attack_cooldown -= 1

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0

    def draw_health_bar(self, surface):
        bar_width = 40
        bar_height = 4
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.top - 8

        # Фон полосы здоровья
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # Здоровье
        health_width = (self.health / self.max_health) * bar_width
        health_color = RED  # Всегда красный для врагов
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))


class Base:
    def __init__(self, x, y, color, is_player=True):
        self.rect = pygame.Rect(x, y, 100, 224)
        if is_player:
            self.health = 250
            self.max_health = 250
        else:
            self.health = 1000
            self.max_health = 1000
        self.color = color
        self.is_player = is_player
        self.shielded = False
        self.shield_time = 0

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        # Рисуем щит если активен
        if self.shielded:
            shield_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 5,
                                      self.rect.width + 10, self.rect.height + 10)
            pygame.draw.rect(surface, BLUE, shield_rect, 3, border_radius=15)

        # Текст на базе
        text = "Организм" if self.is_player else "Вирусы"
        text_surf = small_font.render(text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def take_damage(self, damage):
        if not self.shielded:
            self.health -= damage
            return self.health <= 0
        return False

    def draw_health_bar(self, surface):
        bar_width = 120
        bar_height = 10
        bar_x = self.rect.centerx - bar_width // 2
        bar_y = self.rect.bottom + 10

        # Фон полосы здоровья
        pygame.draw.rect(surface, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))

        # Здоровье
        health_width = (self.health / self.max_health) * bar_width
        health_color = GREEN if self.health > self.max_health * 0.3 else RED
        pygame.draw.rect(surface, health_color, (bar_x, bar_y, health_width, bar_height))

        # Текст здоровья
        health_text = f"{self.health}/{self.max_health}"
        text_surf = small_font.render(health_text, True, BLACK)
        text_rect = text_surf.get_rect(center=(self.rect.centerx, bar_y + bar_height + 15))
        surface.blit(text_surf, text_rect)


class ShopItem:
    def __init__(self, x, y, width, height, name, description, cost, effect):
        self.rect = pygame.Rect(x, y, width, height)
        self.name = name
        self.description = description
        self.cost = cost
        self.effect = effect
        self.is_hovered = False

    def draw(self, surface):
        color = LIGHT_BLUE if self.is_hovered else WHITE
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=5)

        # Название товара
        name_surf = tiny_font.render(self.name, True, BLACK)
        name_rect = name_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 8))
        surface.blit(name_surf, name_rect)

        # Описание
        desc_surf = tiny_font.render(self.description, True, BLACK)
        desc_rect = desc_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 35))
        surface.blit(desc_surf, desc_rect)

        # Стоимость
        cost_surf = tiny_font.render(f"Цена: {self.cost} руб.", True, BLACK)
        cost_rect = cost_surf.get_rect(midtop=(self.rect.centerx, self.rect.top + 62))
        surface.blit(cost_surf, cost_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


class Game:
    def __init__(self):
        self.state = MENU
        self.clock = pygame.time.Clock()
        base_y = SCREEN_HEIGHT // 2 - 112  # Центрирование по высоте (224 - высота базы)
        self.player_base = Base(50, base_y, BLUE)
        self.enemy_base = Base(SCREEN_WIDTH - 150, base_y, RED, False)

        # Группы спрайтов
        self.units = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()

        # Ресурсы
        self.immunity = 100
        self.money = 2000
        self.max_immunity = 100

        # Кнопки
        self.buttons = [
            Button(SCREEN_WIDTH // 2 - 100, 340, 200, 60, "Начать игру"),
            Button(SCREEN_WIDTH // 2 - 100, 420, 200, 60, "Обучение"),
            Button(SCREEN_WIDTH // 2 - 100, 500, 200, 60, "Выход")
        ]

        self.tutorial_back_button = Button(SCREEN_WIDTH // 2 - 100, 600, 200, 60, "Назад")

        self.game_over_buttons = [
            Button(SCREEN_WIDTH // 2 - 120, 450, 200, 60, "В меню"),
            Button(SCREEN_WIDTH // 2 + 120, 450, 200, 60, "Выход")
        ]

        self.victory_buttons = [
            Button(SCREEN_WIDTH // 2 - 110, 450, 200, 60, "В меню"),
            Button(SCREEN_WIDTH // 2 + 110, 450, 200, 60, "Выход")
        ]

        self.shop_button = Button(SCREEN_WIDTH - 120, 10, 100, 40, "Магазин")
        self.shop_back_button = Button(SCREEN_WIDTH // 2 - 100, 600, 200, 60, "Продолжить")

        # Товары в магазине
        shop_width = 250
        shop_height = 150
        shop_gap = 30
        total_width = 3 * shop_width + 2 * shop_gap
        start_x = (SCREEN_WIDTH - total_width) // 2
        self.shop_items = [
            ShopItem(start_x + i * (shop_width + shop_gap), 150, shop_width, shop_height,
                     name, desc, cost, effect)
            for i, (name, desc, cost, effect) in enumerate([
                ("Лекарство", "Увеличивает иммунитет +10", 500, "immunity"),
                ("Вакцина Ур.1", "Щит на 15 секунд", 1000, "shield1"),
                ("Вакцина Ур.2", "Щит на 30 секунд", 2000, "shield2")
            ])
        ]
        # Четвертый товар — под ним, по центру
        self.shop_items.append(
            ShopItem(SCREEN_WIDTH // 2 - shop_width // 2, 330, shop_width, shop_height,
                     "Вакцина Ур.3", "Щит на 60 секунд", 3000, "shield3")
        )

        # Таймеры
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 180  # 3 секунды при 60 FPS
        self.countdown_timer = 600  # 10 секунд отсчета
        self.shield_timer = 0

        # Выбранный юнит для размещения
        self.selected_unit = None
        self.unit_types = [
            "Нейтрофил", "Макрофаг", "В-лимфоцит", "Т-киллер", "NK-клетка"
        ]

        # Очки
        self.score = 0
        self.wave = 1

        self.music_on = True
        self.music_button = Button(SCREEN_WIDTH - 240, 80, 110, 40, "Выключить музыку")
        self.sounds_on = True
        self.sounds_button = Button(SCREEN_WIDTH - 360, 80, 110, 40, "Выключить звуки")
        self.music_volume = 0.05
        self.sounds_volume = 0.05
        pygame.mixer.music.load(resource_path("resources/audio/main_theme.mp3"))
        pygame.mixer.music.set_volume(self.music_volume)
        if self.music_on:
            pygame.mixer.music.play(-1)

        self.last_state = None

        # Загрузка фонового изображения
        self.background_img = pygame.image.load(resource_path("resources/sprites/background.png")).convert()
        self.background_img = pygame.transform.scale(self.background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

        self.music_slider_rect = pygame.Rect(SCREEN_WIDTH - 240, 145, 110, 10)
        self.sounds_slider_rect = pygame.Rect(SCREEN_WIDTH - 360, 145, 110, 10)
        self.music_slider_drag = False
        self.sounds_slider_drag = False

        # Загрузка анимаций для нейтрофила
        self.neutrophil_anims = {
            'run': pygame.image.load(resource_path(os.path.join('resources/sprites/male_run.png'))).convert_alpha(),
            'punch': pygame.image.load(resource_path(os.path.join('resources/sprites/male_punch.png'))).convert_alpha(),
            'death': pygame.image.load(resource_path(os.path.join('resources/sprites/male_death.png'))).convert_alpha(),
        }

        # Загрузка анимаций для barbarian (для врага)
        self.barbarian_anims = {
            'run': pygame.image.load(resource_path(os.path.join('resources/sprites/barbarian_run.png'))).convert_alpha(),
            'attack': pygame.image.load(resource_path(os.path.join('resources/sprites/barbarian_attack.png'))).convert_alpha(),
        }

        # Загрузка фонового изображения для меню
        self.menu_background_img = pygame.image.load(resource_path("resources/sprites/menu_background.jpg")).convert()
        self.menu_background_img = pygame.transform.scale(self.menu_background_img, (SCREEN_WIDTH, SCREEN_HEIGHT))

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            # Функция для клика
            def play_click():
                if self.sounds_on:
                    click_sound = pygame.mixer.Sound(resource_path("resources/audio/click.mp3"))
                    click_sound.set_volume(self.sounds_volume)
                    click_sound.play()

            # Обработка меню
            if self.state == MENU:
                for i, button in enumerate(self.buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, event):
                        play_click()
                        if i == 0:  # Начать игру
                            self.reset_game()
                            self.state = PLAYING
                        elif i == 1:  # Обучение
                            self.state = TUTORIAL
                        elif i == 2:  # Выход
                            pygame.quit()
                            sys.exit()

            # Обработка обучения
            elif self.state == TUTORIAL:
                self.tutorial_back_button.check_hover(mouse_pos)
                if self.tutorial_back_button.is_clicked(mouse_pos, event):
                    play_click()
                    self.state = MENU

            # Обработка магазина
            elif self.state == SHOP:
                self.shop_back_button.check_hover(mouse_pos)
                if self.shop_back_button.is_clicked(mouse_pos, event):
                    play_click()
                    self.state = PLAYING

                for item in self.shop_items:
                    item.check_hover(mouse_pos)
                    if item.is_clicked(mouse_pos, event) and self.money >= item.cost:
                        play_click()
                        if self.sounds_on:
                            buying_sound = pygame.mixer.Sound(resource_path("resources/audio/buying.mp3"))
                            buying_sound.set_volume(self.sounds_volume)
                            buying_sound.play()
                        if item.effect == "immunity":
                            self.max_immunity += 10
                            self.money -= item.cost
                        elif item.effect.startswith("shield"):
                            level = int(item.effect[-1])
                            duration = 900 if level == 1 else 1800 if level == 2 else 3600
                            self.shield_timer += duration
                            self.money -= item.cost

            # Обработка игрового процесса
            elif self.state == PLAYING:
                self.shop_button.check_hover(mouse_pos)
                if self.shop_button.is_clicked(mouse_pos, event):
                    play_click()
                    self.state = SHOP

                # --- Кнопка выхода в меню ---
                if hasattr(self, 'exit_to_menu_rect') and self.exit_to_menu_rect.collidepoint(mouse_pos):
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        play_click()
                        self.state = MENU

                # Выбор юнита для покупки (по хитбоксам)
                if hasattr(self, 'unit_button_rects'):
                    for i, rect in enumerate(self.unit_button_rects):
                        if rect.collidepoint(mouse_pos) and event.type == MOUSEBUTTONDOWN:
                            unit_type = self.unit_types[i]
                            unit_cost = 10 if unit_type == "Нейтрофил" else \
                                30 if unit_type == "Макрофаг" else \
                                    25 if unit_type == "В-лимфоцит" else \
                                        40 if unit_type == "Т-киллер" else 50
                            if self.immunity >= unit_cost:
                                self.selected_unit = unit_type

                # Размещение юнита
                if self.selected_unit and event.type == MOUSEBUTTONDOWN and event.button == 1:
                    if 100 < mouse_pos[0] < SCREEN_WIDTH - 200 and 100 < mouse_pos[1] < SCREEN_HEIGHT - 100:
                        unit_cost = 10 if self.selected_unit == "Нейтрофил" else \
                            30 if self.selected_unit == "Макрофаг" else \
                                25 if self.selected_unit == "В-лимфоцит" else \
                                    40 if self.selected_unit == "Т-киллер" else 50
                        if self.immunity >= unit_cost:
                            if self.sounds_on:
                                attack_sound = pygame.mixer.Sound(resource_path("resources/audio/attack.mp3"))
                                attack_sound.set_volume(self.sounds_volume)
                                attack_sound.play()
                            if self.selected_unit == "Нейтрофил":
                                self.units.add(Unit(mouse_pos[0], mouse_pos[1], self.selected_unit, self.neutrophil_anims))
                            else:
                                self.units.add(Unit(mouse_pos[0], mouse_pos[1], self.selected_unit))
                            self.immunity -= unit_cost
                            self.selected_unit = None

                # Отмена выбора
                if event.type == MOUSEBUTTONDOWN and event.button == 3:
                    self.selected_unit = None

            # Обработка конца игры
            elif self.state == GAME_OVER or self.state == VICTORY:
                buttons = self.game_over_buttons if self.state == GAME_OVER else self.victory_buttons
                for i, button in enumerate(buttons):
                    button.check_hover(mouse_pos)
                    if button.is_clicked(mouse_pos, event):
                        play_click()
                        if i == 0:  # В меню
                            self.state = MENU
                        elif i == 1:  # Выход
                            pygame.quit()
                            sys.exit()

            # Кнопка управления музыкой (работает во всех состояниях)
            self.music_button.check_hover(mouse_pos)
            if self.music_button.is_clicked(mouse_pos, event):
                play_click()
                if self.music_on:
                    pygame.mixer.music.stop()
                    self.music_on = False
                    self.music_button.text = "Включить музыку"
                else:
                    pygame.mixer.music.play(-1)
                    self.music_on = True
                    self.music_button.text = "Выключить музыку"

            # Кнопка управления звуками
            self.sounds_button.check_hover(mouse_pos)
            if self.sounds_button.is_clicked(mouse_pos, event):
                play_click()
                if self.sounds_on:
                    self.sounds_on = False
                    self.sounds_button.text = "Включить звуки"
                else:
                    self.sounds_on = True
                    self.sounds_button.text = "Выключить звуки"

            # --- Ползунок громкости музыки ---
            if event.type == MOUSEBUTTONDOWN and self.music_slider_rect.collidepoint(mouse_pos):
                self.music_slider_drag = True
            if event.type == MOUSEBUTTONUP:
                self.music_slider_drag = False
            if self.music_slider_drag and event.type == MOUSEMOTION:
                rel_x = min(max(mouse_pos[0] - self.music_slider_rect.x, 0), self.music_slider_rect.width)
                self.music_volume = rel_x / self.music_slider_rect.width
                pygame.mixer.music.set_volume(self.music_volume)
            # --- Ползунок громкости звуков ---
            if event.type == MOUSEBUTTONDOWN and self.sounds_slider_rect.collidepoint(mouse_pos):
                self.sounds_slider_drag = True
            if event.type == MOUSEBUTTONUP:
                self.sounds_slider_drag = False
            if self.sounds_slider_drag and event.type == MOUSEMOTION:
                rel_x = min(max(mouse_pos[0] - self.sounds_slider_rect.x, 0), self.sounds_slider_rect.width)
                self.sounds_volume = rel_x / self.sounds_slider_rect.width

    def reset_game(self):
        self.units.empty()
        self.enemies.empty()
        self.player_base.health = 250
        self.player_base.max_health = 250
        self.enemy_base.health = 1000
        self.enemy_base.max_health = 1000
        self.immunity = 100
        self.money = 2000
        self.max_immunity = 100
        self.enemy_spawn_timer = 0
        self.countdown_timer = 600  # 10 секунд отсчета
        self.shield_timer = 0
        self.selected_unit = None
        self.score = 0
        self.wave = 1

    def spawn_enemy(self):
        enemy_types = ["Бактерия", "Вирус гриппа", "ВИЧ", "Раковая клетка"]
        weights = [0.4, 0.3, 0.2, 0.1]  # Вероятности появления
        wave_factor = min(1.0, self.wave * 0.1)
        weights[0] = max(0.1, weights[0] - wave_factor * 0.3)
        weights[3] = min(0.4, weights[3] + wave_factor * 0.3)
        enemy_type = random.choices(enemy_types, weights=weights, k=1)[0]
        if enemy_type == "Бактерия":
            self.enemies.add(Enemy(enemy_type, self.barbarian_anims))
        else:
            self.enemies.add(Enemy(enemy_type))

    def update(self):
        if self.state == PLAYING:
            # Обновление щита
            if self.shield_timer > 0:
                self.shield_timer -= 1
                self.player_base.shielded = True
                for unit in self.units:
                    unit.shielded = True
            else:
                self.player_base.shielded = False
                for unit in self.units:
                    unit.shielded = False

            # Отсчет перед началом
            if self.countdown_timer > 0:
                self.countdown_timer -= 1
                return

            # Спавн врагов
            self.enemy_spawn_timer += 1
            if self.enemy_spawn_timer >= self.enemy_spawn_interval:
                self.spawn_enemy()
                self.enemy_spawn_timer = 0

                # Увеличиваем сложность каждые 10 врагов
                if len(self.enemies) % 10 == 0:
                    self.wave += 1
                    self.enemy_spawn_interval = max(60, self.enemy_spawn_interval - 10)

            # Обновление юнитов
            for unit in self.units:
                unit.update(self.enemies, self.enemy_base)
                if unit.health <= 0:
                    if self.sounds_on:
                        puff_sound = pygame.mixer.Sound(resource_path("resources/audio/puff.mp3"))
                        puff_sound.set_volume(self.sounds_volume)
                        puff_sound.play()
                    unit.kill()

            # Обновление врагов
            for enemy in self.enemies:
                enemy.update(self.player_base, self.units)
                if enemy.health <= 0:
                    if self.sounds_on:
                        puff_sound = pygame.mixer.Sound(resource_path("resources/audio/puff.mp3"))
                        puff_sound.set_volume(self.sounds_volume)
                        puff_sound.play()
                    self.immunity = min(self.max_immunity, self.immunity + 3)
                    self.money += enemy.reward
                    self.score += enemy.reward // 10
                    enemy.kill()

            # Проверка условий победы/поражения
            if self.player_base.health <= 0:
                self.state = GAME_OVER
            elif self.enemy_base.health <= 0:
                self.state = VICTORY

        # Воспроизведение победы/поражения только при переходе
        if self.state != self.last_state:
            if self.state == VICTORY:
                if self.sounds_on:
                    victory_sound = pygame.mixer.Sound(resource_path("resources/audio/victory.mp3"))
                    victory_sound.set_volume(self.sounds_volume)
                    victory_sound.play()
            elif self.state == GAME_OVER:
                if self.sounds_on:
                    defeat_sound = pygame.mixer.Sound(resource_path("resources/audio/defeat.mp3"))
                    defeat_sound.set_volume(self.sounds_volume)
                    defeat_sound.play()
            self.last_state = self.state

    def draw(self):
        if self.state == PLAYING:
            # Отрисовка фонового изображения
            screen.blit(self.background_img, (0, 0))
        elif self.state == MENU or self.state == TUTORIAL:
            # Фон меню и обучения
            screen.blit(self.menu_background_img, (0, 0))
        else:
            screen.fill((240, 240, 240))

        if self.state == MENU:
            # Заголовок
            title = title_font.render("Human TowerDefence", True, BLUE)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 190))

            # Подзаголовок
            subtitle = medium_font.render("Защити организм от вирусов!", True, BLACK)
            screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 270))

            # Кнопки
            for button in self.buttons:
                button.draw(screen)

        elif self.state == TUTORIAL:
            # Заголовок
            title = title_font.render("Обучение", True, BLUE)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2 - 80, 50))

            # Описание
            lines = [
                "Цель: защитить организм (синяя база)",
                "и разрушить базу вирусов (красная)",
                "",
                "Ресурсы:",
                "- Иммунитет: для юнитов",
                "- Финансы: за убийство врагов",
                "",
                "Управление:",
                "- ЛКМ: выбрать/поставить юнита",
                "- ПКМ: отменить выбор",
                "- Магазин: улучшения и вакцины",
                "",
                "Советы:",
                "Комбинируйте юнитов для защиты.",
                "Вакцины — для критических моментов!"
            ]

            y_pos = 150
            for line in lines:
                text = tiny_font.render(line, True, BLACK)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2 - 80, y_pos))
                y_pos += 25

            self.tutorial_back_button.draw(screen)

        elif self.state == PLAYING:
            # Отрисовка баз
            self.player_base.draw(screen)
            self.enemy_base.draw(screen)
            self.player_base.draw_health_bar(screen)
            self.enemy_base.draw_health_bar(screen)

            # Отрисовка юнитов и врагов
            self.units.draw(screen)
            self.enemies.draw(screen)

            # Полосы здоровья
            for unit in self.units:
                unit.draw_health_bar(screen)
            for enemy in self.enemies:
                enemy.draw_health_bar(screen)

            # Интерфейс
            pygame.draw.rect(screen, (200, 200, 200), (0, 0, SCREEN_WIDTH, 60))
            pygame.draw.line(screen, BLACK, (0, 60), (SCREEN_WIDTH, 60), 2)

            # Ресурсы
            immunity_text = tiny_font.render(f"Иммунитет: {self.immunity}/{self.max_immunity}", True, BLACK)
            money_text = tiny_font.render(f"Финансы: {self.money} руб.", True, BLACK)
            wave_text = tiny_font.render(f"Волна: {self.wave}", True, BLACK)
            score_text = tiny_font.render(f"Очки: {self.score}", True, BLACK)

            screen.blit(immunity_text, (20, 20))
            screen.blit(money_text, (200, 20))
            screen.blit(wave_text, (400, 20))
            screen.blit(score_text, (550, 20))

            # Панель выбора юнитов
            pygame.draw.rect(screen, (180, 180, 180), (0, SCREEN_HEIGHT - 90, SCREEN_WIDTH, 90))
            unit_y = SCREEN_HEIGHT - 70
            unit_width = 110
            unit_height = 50
            unit_gap = 32
            total_units = len(self.unit_types)
            total_width = total_units * unit_width + (total_units - 1) * unit_gap
            start_x = (SCREEN_WIDTH - total_width) // 2

            # Кнопка выхода в меню (справа)
            exit_rect = pygame.Rect(SCREEN_WIDTH - unit_width - 30, unit_y, unit_width, unit_height)
            pygame.draw.rect(screen, (255, 220, 220), exit_rect, border_radius=8)
            pygame.draw.rect(screen, BLACK, exit_rect, 2, border_radius=8)
            exit_text = extra_tiny_font.render("В меню", True, BLACK)
            screen.blit(exit_text, (exit_rect.centerx - exit_text.get_width() // 2, exit_rect.centery - exit_text.get_height() // 2))
            self.exit_to_menu_rect = exit_rect

            # --- Список хитбоксов кнопок юнитов ---
            self.unit_button_rects = []
            for i, unit_type in enumerate(self.unit_types):
                unit_cost = 10 if unit_type == "Нейтрофил" else \
                    30 if unit_type == "Макрофаг" else \
                        25 if unit_type == "В-лимфоцит" else \
                            40 if unit_type == "Т-киллер" else 50

                color = LIGHT_BLUE if self.selected_unit == unit_type else WHITE
                rect = pygame.Rect(start_x + i * (unit_width + unit_gap), unit_y, unit_width, unit_height)
                self.unit_button_rects.append(rect)
                pygame.draw.rect(screen, color, rect, border_radius=8)
                pygame.draw.rect(screen, BLACK, rect, 2, border_radius=8)

                text = extra_tiny_font.render(f"{unit_type} ({unit_cost})", True, BLACK)
                screen.blit(text, (rect.centerx - text.get_width() // 2, rect.centery - text.get_height() // 2))

            # Отсчет перед началом
            if self.countdown_timer > 0:
                count = self.countdown_timer // 60 + 1
                count_text = large_font.render(str(count), True, RED)
                screen.blit(count_text, (SCREEN_WIDTH // 2 - count_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 - count_text.get_height() // 2))

            # --- ТАЙМЕР ЩИТА поверх всех элементов ---
            if self.shield_timer > 0:
                shield_sec = self.shield_timer // 60
                shield_text = tiny_font.render(f"Щит: {shield_sec} сек", True, GREEN)
                shield_text_y = SCREEN_HEIGHT - 30  # чуть выше самого края
                screen.blit(shield_text, (20, shield_text_y))

            self.shop_button.draw(screen)

        elif self.state == SHOP:
            # Фон
            pygame.draw.rect(screen, (200, 220, 255), (100, 80, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 160),
                             border_radius=20)
            pygame.draw.rect(screen, BLACK, (100, 80, SCREEN_WIDTH - 200, SCREEN_HEIGHT - 160), 3, border_radius=20)

            # Заголовок
            title = large_font.render("Магазин", True, BLUE)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

            # Ресурсы
            money_text = medium_font.render(f"Финансы: {self.money} руб.", True, BLACK)
            screen.blit(money_text, (SCREEN_WIDTH // 2 - money_text.get_width() // 2, 25))

            # Товары
            for item in self.shop_items:
                item.draw(screen)

            self.shop_back_button.draw(screen)

        elif self.state == GAME_OVER:
            # Фон
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))

            # Сообщение
            title = large_font.render("Сожалеем, вы проиграли!", True, RED)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

            # Очки
            score_text = medium_font.render(f"Ваши очки: {self.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

            # Кнопки (выравнивание по центру)
            button_width = 200
            button_height = 60
            button_gap = 40
            total_width = button_width * 2 + button_gap
            start_x = SCREEN_WIDTH // 2 - total_width // 2
            y = 450
            self.game_over_buttons[0].rect.topleft = (start_x, y)
            self.game_over_buttons[1].rect.topleft = (start_x + button_width + button_gap, y)
            for button in self.game_over_buttons:
                button.draw(screen)

        elif self.state == VICTORY:
            # Фон
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 50, 0, 150))
            screen.blit(overlay, (0, 0))

            # Сообщение
            title = large_font.render("Поздравляем, вы победили!", True, GREEN)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))

            # Очки
            score_text = medium_font.render(f"Ваши очки: {self.score}", True, WHITE)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))

            # Кнопки
            button_width = 200
            button_height = 60
            button_gap = 40
            total_width = button_width * 2 + button_gap
            start_x = SCREEN_WIDTH // 2 - total_width // 2
            y = 450
            self.victory_buttons[0].rect.topleft = (start_x, y)
            self.victory_buttons[1].rect.topleft = (start_x + button_width + button_gap, y)
            for button in self.victory_buttons:
                button.draw(screen)

        # Кнопки управления музыкой и звуками
        if self.state != SHOP:
            self.music_button.draw(screen)
            self.sounds_button.draw(screen)
            
            # --- Ползунок громкости музыки ---
            pygame.draw.rect(screen, (180,180,180), self.music_slider_rect, border_radius=5)
            handle_x = int(self.music_slider_rect.x + self.music_volume * self.music_slider_rect.width)
            pygame.draw.circle(screen, BLUE, (handle_x, self.music_slider_rect.y + 5), 8)
            label = extra_tiny_font.render("Музыка", True, BLACK)
            screen.blit(label, (self.music_slider_rect.x, self.music_slider_rect.y - 23))
            # --- Ползунок громкости звуков ---
            pygame.draw.rect(screen, (180,180,180), self.sounds_slider_rect, border_radius=5)
            handle_x = int(self.sounds_slider_rect.x + self.sounds_volume * self.sounds_slider_rect.width)
            pygame.draw.circle(screen, GREEN, (handle_x, self.sounds_slider_rect.y + 5), 8)
            label = extra_tiny_font.render("Звуки", True, BLACK)
            screen.blit(label, (self.sounds_slider_rect.x, self.sounds_slider_rect.y - 23))

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)


# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run()
import pygame
from constants import DisplayConstants

class UserInterface:
    @staticmethod
    def draw_button(screen, text, rect, color, text_color=None):
        if text_color is None:
            text_color = DisplayConstants.WHITE
        pygame.draw.rect(screen, color, rect)
        text_surface = pygame.font.SysFont("arial", DisplayConstants.MAIN_FONT_SIZE).render(text, True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        screen.blit(text_surface, text_rect)

    @staticmethod
    def draw_progress_bar(screen, x, y, width, height, value, max_value, color, bg_color=(50, 50, 50)):
        pygame.draw.rect(screen, bg_color, (x, y, width, height))
        progress_width = (width * value) / max_value
        pygame.draw.rect(screen, color, (x, y, progress_width, height))

    @staticmethod
    def draw_text_centered(screen, text, font, y, color=None):
        if color is None:
            color = DisplayConstants.WHITE
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(DisplayConstants.WIDTH // 2, y))
        screen.blit(text_surface, text_rect)

    @staticmethod
    def draw_panel(screen, rect, color, border_color=None, border_width=0):
        pygame.draw.rect(screen, color, rect)
        if border_color:
            pygame.draw.rect(screen, border_color, rect, border_width) 
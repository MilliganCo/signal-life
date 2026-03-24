import pygame
import math
from settings import (
    CELL_SIZE, COLOR_CALM, COLOR_HOT, COLOR_SUPER, COLOR_COLD,
    REFRACTORY_DURATION, TYPE_HOT, TYPE_SUPER, TYPE_COLD
)

def recovery_color(val, base_color, refractory_duration=REFRACTORY_DURATION):
    """
    Вычисляет цвет для клеток в фазе восстановления на основе базового цвета.
    Смешиваем базовый цвет с белым с небольшим осциллирующим смещением,
    чтобы визуализировать фазу восстановления.
    """
    fraction = (val - 2) / float(refractory_duration - 1) if refractory_duration > 1 else 0
    offset = int(5 * math.sin(val))  # небольшое колебание
    r = min(255, max(0, int(base_color[0] + fraction * (255 - base_color[0]) + offset)))
    g = min(255, max(0, int(base_color[1] + fraction * (255 - base_color[1]) + offset)))
    b = min(255, max(0, int(base_color[2] + fraction * (255 - base_color[2]) + offset)))
    return (r, g, b)

def get_color(cell_type, state_val):
    """
    Возвращает цвет клетки (R,G,B) в зависимости от её типа (cell_type) и состояния (state_val):
      - state_val == 0 => COLOR_CALM (пустая клетка)
      - state_val == 1 => возбужденная: базовый цвет + небольшое смещение
      - state_val >= 2 => фаза восстановления: плавный переход к белому
    """
    if state_val == 0:
        return COLOR_CALM
    elif state_val == 1:
        if cell_type == TYPE_HOT:
            base = COLOR_HOT
            return (min(255, base[0] + 10), base[1], base[2])
        elif cell_type == TYPE_SUPER:
            base = COLOR_SUPER
            # Усиливаем зелёную
            return (base[0], min(255, base[1] + 15), base[2])
        elif cell_type == TYPE_COLD:
            base = COLOR_COLD
            # Усиливаем синюю
            return (base[0], base[1], min(255, base[2] + 10))
        else:
            return COLOR_HOT
    else:
        # фаза восстановления
        if cell_type == TYPE_HOT:
            base = COLOR_HOT
        elif cell_type == TYPE_SUPER:
            base = COLOR_SUPER
        elif cell_type == TYPE_COLD:
            base = COLOR_COLD
        else:
            base = COLOR_HOT
        return recovery_color(state_val, base)

def get_ptype_name(pt):
    if pt == TYPE_HOT:
        return "HOT"
    elif pt == TYPE_SUPER:
        return "SUPER"
    elif pt == TYPE_COLD:
        return "COLD"
    else:
        return "EMPTY"

def draw_grid(screen, state, threshold, ptype, current_ptype):
    rows, cols = state.shape
    for y in range(rows):
        for x in range(cols):
            val = state[y, x]
            cell_type = ptype[y, x]
            color = get_color(cell_type, val)
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

    font = pygame.font.SysFont("Arial", 16)
    text_surface = font.render(f"Threshold: {threshold:.2f}", True, (255, 255, 255))
    screen.blit(text_surface, (5, 5))

    ptype_text = get_ptype_name(current_ptype)
    text_surface2 = font.render(f"Particle: {ptype_text}", True, (255, 255, 255))
    screen.blit(text_surface2, (5, 25))

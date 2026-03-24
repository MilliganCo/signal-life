# display_manager.py
import pygame
from settings import CELL_SIZE, GRID_SIZE, COLOR_CALM, COLOR_EXCITED, REFRACTORY_DURATION

def recovery_color(val, refractory_duration=REFRACTORY_DURATION):
    """
    Вычисляет цвет для клеток в фазе восстановления (состояния от 2 до 2+REFRACTORY_DURATION-1),
    создавая простой градиент.
    """
    fraction = (val - 2) / float(refractory_duration - 1) if refractory_duration > 1 else 0
    r = int(180 + fraction * 50)   # от 180 до 230
    g = 0
    b = int(180 - fraction * 80)   # от 180 до 100
    return (r, g, b)

def draw_grid(screen, state, threshold):
    """
    Рисует решётку клеток. Клетки раскрашиваются в зависимости от состояния:
      0 — COLOR_CALM (спокойная),
      1 — COLOR_EXCITED (возбужденная),
      остальные — градиент восстановления.
    Также выводит текущий порог (THRESHOLD) в левом верхнем углу.
    """
    rows, cols = state.shape
    for y in range(rows):
        for x in range(cols):
            val = state[y, x]
            if val == 0:
                color = COLOR_CALM
            elif val == 1:
                color = COLOR_EXCITED
            else:
                color = recovery_color(val)
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
    # Отрисовка текста с текущим порогом
    font = pygame.font.SysFont("Arial", 16)
    text_surface = font.render(f"Threshold: {threshold:.2f}", True, (255, 255, 255))
    screen.blit(text_surface, (5, 5))

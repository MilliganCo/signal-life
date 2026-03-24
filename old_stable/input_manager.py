# input_manager.py
import pygame
from settings import CELL_SIZE, GRID_SIZE

def handle_mouse(state):
    """
    При зажатой левой кнопке мыши клетка под курсором становится возбужденной (1).
    """
    if pygame.mouse.get_pressed()[0]:
        mx, my = pygame.mouse.get_pos()
        gx = mx // CELL_SIZE
        gy = my // CELL_SIZE
        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE:
            state[gy, gx] = 1

def handle_keys(event, globals_dict):
    """
    Обрабатывает нажатия:
      - Клавиша W увеличивает THRESHOLD.
      - Клавиша S уменьшает THRESHOLD (но не ниже 0.1).
      - Клавиша F переключает режим паузы.
    globals_dict — словарь с переменными 'THRESHOLD' и 'paused', которые изменяются здесь.
    """
    if event.key == pygame.K_w:
        globals_dict['THRESHOLD'] += 0.1
        print(f"Threshold increased: {globals_dict['THRESHOLD']:.2f}")
    elif event.key == pygame.K_s:
        globals_dict['THRESHOLD'] = max(0.1, globals_dict['THRESHOLD'] - 0.1)
        print(f"Threshold decreased: {globals_dict['THRESHOLD']:.2f}")
    elif event.key == pygame.K_f:
        globals_dict['paused'] = not globals_dict['paused']
        print("Paused" if globals_dict['paused'] else "Resumed")

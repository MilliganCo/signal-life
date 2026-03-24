# main.py

import pygame
import numpy as np
from settings import GRID_SIZE, CELL_SIZE, FPS, THRESHOLD as INIT_THRESHOLD
from automata import update_state_with_charge, external_signals
from input_manager import handle_mouse
from display_manager import draw_grid

pygame.init()
screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
pygame.display.set_caption("Signal Life with Charge Accumulation")
clock = pygame.time.Clock()

state = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
charge = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
threshold = INIT_THRESHOLD
paused = False

running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_f:
                paused = not paused
                print("Paused" if paused else "Resumed")

    # Плавное изменение порога при зажатии клавиш W и S
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        threshold += 0.02
    if keys[pygame.K_s]:
        threshold = max(0.1, threshold - 0.02)

    # Рисование мышью
    handle_mouse(state)

    if not paused:
        external_signals(state)
        state, charge = update_state_with_charge(state, charge, threshold)

    screen.fill((50, 50, 50))
    draw_grid(screen, state, threshold)
    pygame.display.flip()

pygame.quit()

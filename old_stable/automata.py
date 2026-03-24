# automata.py

import numpy as np
import random
from settings import GRID_SIZE, REFRACTORY_DURATION, KERNEL, LEAKAGE, GROWTH_PROB, EXTERNAL_SIGNAL_PROB


def in_bounds(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE


def get_signal(state, x, y):
    """
    Возвращает взвешенную сумму сигналов от соседей клетки (x,y) с использованием KERNEL.
    Учитываются только клетки в состоянии возбуждения (state == 1).
    """
    rows = len(KERNEL)
    half = rows // 2
    s = 0.0
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            nx = x + dx
            ny = y + dy
            if in_bounds(nx, ny):
                if state[ny, nx] == 1:
                    s += KERNEL[dy + half][dx + half]
    return s


def count_excited_neighbors(state, x, y):
    """
    Считает число возбужденных соседей (состояние 1) для клетки (x,y).
    """
    cnt = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and state[ny, nx] == 1:
                cnt += 1
    return cnt


def update_state_with_charge(state, charge, current_threshold):
    """
    Обновление, комбинирующее правила "Signal Life" с элементами Game of Life.

    Для клетки в состоянии 0 (спокойная):
      - Накапливается заряд: новый заряд = старый заряд + взвешенная сумма сигналов от соседей - утечка.
      - Если заряд >= current_threshold, клетка становится возбужденной (1) и заряд сбрасывается.
      - Либо, если число возбужденных соседей ровно 3 (правило GOL), клетка тоже возбуждается.

    Для клетки в состоянии 1 (возбужденная):
      - Сразу переходит в фазу восстановления (состояние 2) и заряд сбрасывается.

    Для клетки в состоянии восстановления (значения от 2 до 2+REFRACTORY_DURATION-1):
      - С каждым шагом значение увеличивается, а при достижении верхнего предела клетка сбрасывается в состояние 0.

    Дополнительно можно оставить правило роста (при GROWTH_PROB), но оно можно корректировать.
    """
    new_state = state.copy()
    new_charge = charge.copy()
    rows, cols = state.shape

    for y in range(rows):
        for x in range(cols):
            if state[y, x] == 0:
                # Спокойная клетка: накопление заряда
                s = get_signal(state, x, y)
                # Можно добавить вклад от количества соседей, если нужно:
                # n_exc = count_excited_neighbors(state, x, y)
                # new_charge[y, x] += (s + 0.1*n_exc) - LEAKAGE * new_charge[y, x]
                new_charge[y, x] += s - LEAKAGE * new_charge[y, x]
                # Если заряд превышает порог, возбуждаем клетку
                if new_charge[y, x] >= current_threshold:
                    new_state[y, x] = 1
                    new_charge[y, x] = 0
                # Также правило GOL: если ровно 3 возбуждённых соседей, активируем клетку
                elif count_excited_neighbors(state, x, y) == 3:
                    new_state[y, x] = 1
                    new_charge[y, x] = 0
            elif state[y, x] == 1:
                # Возбужденная клетка переходит в восстановление
                new_state[y, x] = 2
                new_charge[y, x] = 0
            else:
                # Клетка в восстановлении: продвигаем фазу восстановления
                if state[y, x] < 2 + (REFRACTORY_DURATION - 1):
                    new_state[y, x] += 1
                else:
                    new_state[y, x] = 0
                    new_charge[y, x] = 0

    # Правило роста (опционально): от каждой клетки в состоянии 1 с вероятностью GROWTH_PROB возбуждаем соседей
    for y in range(rows):
        for x in range(cols):
            if state[y, x] == 1:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and new_state[ny, nx] == 0:
                            if random.random() < GROWTH_PROB:
                                new_state[ny, nx] = 1
                                new_charge[ny, nx] = 0
    return new_state, new_charge


def external_signals(state):
    """
    Случайным образом возбуждает одну клетку с вероятностью EXTERNAL_SIGNAL_PROB.
    """
    if random.random() < EXTERNAL_SIGNAL_PROB:
        rx = random.randint(0, GRID_SIZE - 1)
        ry = random.randint(0, GRID_SIZE - 1)
        state[ry, rx] = 1

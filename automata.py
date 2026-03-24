import numpy as np
import random
import math
from settings import (
    GRID_SIZE, REFRACTORY_DURATION, KERNEL, LEAKAGE, GROWTH_PROB, EXTERNAL_SIGNAL_PROB,
    ATTRACTION, REPULSION_THRESHOLD, REPULSION_FORCE,
    TYPE_HOT, TYPE_SUPER, TYPE_COLD, INITIAL_SIZE,
    COLD_STOP_PROB, COLD_ABSORB_HOT
)

####################
# Новые настройки для супер- и холодных частиц
####################
SUPER_MOVE_PROB = 0.2       # вероятность случайного перемещения суперчастицы
SUPER_MOVE_RADIUS = 2       # радиус случайного перемещения суперчастицы
# SUPER_DECAY_FACTOR убран, чтобы суперчастицы не теряли массу дополнительно

def in_bounds(x, y):
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

def get_signal(state, x, y):
    """
    Возвращает взвешенную сумму сигналов от соседей (state==1) с использованием ядра KERNEL.
    """
    rows = len(KERNEL)
    half = rows // 2
    s = 0.0
    for dy in range(-half, half + 1):
        for dx in range(-half, half + 1):
            nx = x + dx
            ny = y + dy
            if in_bounds(nx, ny) and state[ny, nx] == 1:
                s += KERNEL[dy + half][dx + half]
    return s

def count_excited_neighbors(state, x, y):
    cnt = 0
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and state[ny, nx] == 1:
                cnt += 1
    return cnt

def pick_neighbor_type(state, ptype, x, y):
    """
    Ищет соседнюю возбужденную клетку (state==1) с ненулевым типом и возвращает её тип.
    Если не найдено, возвращает 0.
    """
    for dy in [-1, 0, 1]:
        for dx in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and state[ny, nx] == 1 and ptype[ny, nx] != 0:
                return ptype[ny, nx]
    return 0

def teleport_super_particle(new_state, new_ptype, new_size, x, y):
    """
    Суперчастица (TYPE_SUPER) телепортируется в ближайшую пустую клетку в радиусе 2,
    создавая "дочернюю" суперчастицу с размером 0.5, а исходная теряет 30% массы.
    """
    radius = 2
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            nx = x + dx
            ny = y + dy
            if in_bounds(nx, ny) and new_state[ny, nx] == 0:
                new_state[ny, nx] = 1
                new_ptype[ny, nx] = new_ptype[y, x]
                new_size[ny, nx] = new_size[y, x] * 0.5
                new_size[y, x] *= 0.7
                return  # завершаем после телепортации
    # Если пустой клетки нет, ничего не делаем

def random_move_super_particle(new_state, new_ptype, new_size, x, y):
    """
    Случайное перемещение суперчастицы с вероятностью SUPER_MOVE_PROB.
    Радиус перемещения SUPER_MOVE_RADIUS. Если перемещение произошло, возвращает True.
    """
    if random.random() < SUPER_MOVE_PROB:
        candidates = []
        for dy in range(-SUPER_MOVE_RADIUS, SUPER_MOVE_RADIUS + 1):
            for dx in range(-SUPER_MOVE_RADIUS, SUPER_MOVE_RADIUS + 1):
                nx = x + dx
                ny = y + dy
                if in_bounds(nx, ny) and new_state[ny, nx] == 0:
                    candidates.append((nx, ny))
        if candidates:
            tx, ty = random.choice(candidates)
            new_state[ty, tx] = 1
            new_ptype[ty, tx] = new_ptype[y, x]
            new_size[ty, tx] = new_size[y, x]
            new_state[y, x] = 0
            new_ptype[y, x] = 0
            new_size[y, x] = 0
            return True
    return False

def update_state_with_charge(state, charge, ptype, size, current_threshold):
    new_state = state.copy()
    new_charge = charge.copy()
    new_ptype = ptype.copy()
    new_size = size.copy()
    rows, cols = state.shape

    # 1. Обновление пустых клеток: накопление заряда
    for y in range(rows):
        for x in range(cols):
            if state[y, x] == 0:
                s = get_signal(state, x, y)
                new_charge[y, x] += s - LEAKAGE * new_charge[y, x]
                if new_charge[y, x] >= current_threshold or count_excited_neighbors(state, x, y) == 3:
                    new_state[y, x] = 1
                    new_charge[y, x] = 0
                    t = pick_neighbor_type(state, ptype, x, y)
                    # Исправлено: если t == 0, оставляем прежний тип клетки
                    new_ptype[y, x] = t if t != 0 else new_ptype[y, x]
                    if new_size[y, x] == 0:
                        new_size[y, x] = INITIAL_SIZE

    # 2. Обновление возбужденных клеток (переход в восстановление)
    for y in range(rows):
        for x in range(cols):
            if state[y, x] == 1:
                ct = ptype[y, x]
                if ct == TYPE_COLD:
                    if random.random() < COLD_STOP_PROB:
                        new_state[y, x] = 1  # остаётся возбужденной (замирание)
                    else:
                        if random.random() < 0.05:
                            new_state[y, x] = 1
                            new_size[y, x] *= 1.02
                        else:
                            new_state[y, x] = 2
                            new_charge[y, x] = 0
                elif ct == TYPE_SUPER:
                    # Обработка суперчастиц отложена на шаг 5
                    pass
                elif ct == TYPE_HOT:
                    new_state[y, x] = 2
                    new_charge[y, x] = 0

    # 3. Восстановление (фаза восстановления)
    for y in range(rows):
        for x in range(cols):
            if state[y, x] >= 2:
                if state[y, x] < 2 + (REFRACTORY_DURATION - 1):
                    new_state[y, x] += 1
                else:
                    new_state[y, x] = 0
                    new_charge[y, x] = 0
                    new_ptype[y, x] = 0
                    new_size[y, x] = 0

    # 4. Правило роста (заражение соседей)
    for y in range(rows):
        for x in range(cols):
            if state[y, x] == 1:
                ct = ptype[y, x]
                if ct == TYPE_COLD:
                    # Холодные заражают только кардинальными направлениями
                    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
                else:
                    directions = [(dx, dy) for dy in [-1, 0, 1] for dx in [-1, 0, 1] if not (dx == 0 and dy == 0)]
                for dx, dy in directions:
                    nx, ny = x + dx, y + dy
                    if in_bounds(nx, ny) and new_state[ny, nx] == 0:
                        if random.random() < GROWTH_PROB:
                            new_state[ny, nx] = 1
                            new_ptype[ny, nx] = ct
                            new_size[ny, nx] = INITIAL_SIZE

    # 5. Взаимодействие (поглощение, телепортация, перемещение)
    # 5.1. Горячие поглощают суперчастицы (по всем 8 направлениям)
    for y in range(rows):
        for x in range(cols):
            if new_state[y, x] == 1 and new_ptype[y, x] == TYPE_HOT:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and new_state[ny, nx] == 1 and new_ptype[ny, nx] == TYPE_SUPER:
                            new_size[y, x] += new_size[ny, nx] * 30.0  # коэффициент поглощения горячими
                            new_state[ny, nx] = 0
                            new_ptype[ny, nx] = 0
                            new_size[ny, nx] = 0

    # 5.2. Обработка суперчастиц
    for y in range(rows):
        for x in range(cols):
            if new_state[y, x] == 1 and new_ptype[y, x] == TYPE_SUPER:
                # Если рядом есть холодные, суперчастица остаётся возбужденной для поглощения холодных
                adjacent_cold = False
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and new_state[ny, nx] == 1 and new_ptype[ny, nx] == TYPE_COLD:
                            adjacent_cold = True
                if adjacent_cold:
                    new_state[y, x] = 1
                else:
                    moved = random_move_super_particle(new_state, new_ptype, new_size, x, y)
                    if not moved:
                        if random.random() < 0.5:
                            new_state[y, x] = 1
                        else:
                            new_state[y, x] = 2
                            new_charge[y, x] = 0

    # 5.3. Остальные взаимодействия
    for y in range(rows):
        for x in range(cols):
            if new_state[y, x] == 1:
                ct = new_ptype[y, x]
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and new_state[ny, nx] == 1:
                            nt = new_ptype[ny, nx]
                            # Холодные поглощают горячие (по кардинальным направлениям)
                            if ct == TYPE_COLD and nt == TYPE_HOT and (abs(dx) + abs(dy) == 1):
                                new_size[y, x] += new_size[ny, nx] * COLD_ABSORB_HOT
                                new_state[ny, nx] = 0
                                new_ptype[ny, nx] = 0
                                new_size[ny, nx] = 0
                            # Остальные пары по словарю ATTRACTION
                            elif (ct, nt) in ATTRACTION or (nt, ct) in ATTRACTION:
                                if new_size[y, x] >= new_size[ny, nx]:
                                    new_size[y, x] += new_size[ny, nx]
                                    new_state[ny, nx] = 0
                                    new_ptype[ny, nx] = 0
                                    new_size[ny, nx] = 0
                                else:
                                    new_size[ny, nx] += new_size[y, x]
                                    new_state[y, x] = 0
                                    new_ptype[y, x] = 0
                                    new_size[y, x] = 0

    # 6. Отталкивание: перемещение клеток одного типа при превышении REPULSION_THRESHOLD
    for y in range(rows):
        for x in range(cols):
            if new_state[y, x] == 1:
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and new_state[ny, nx] == 1 and new_ptype[ny, nx] == new_ptype[y, x]:
                            if new_size[y, x] > REPULSION_THRESHOLD and new_size[ny, nx] > REPULSION_THRESHOLD:
                                moved = False
                                for ddy in [-1, 0, 1]:
                                    for ddx in [-1, 0, 1]:
                                        tx, ty = x + ddx, y + ddy
                                        if in_bounds(tx, ty) and new_state[ty, tx] == 0:
                                            new_state[ty, tx] = 1
                                            new_ptype[ty, tx] = new_ptype[y, x]
                                            new_size[ty, tx] = new_size[y, x] * 0.8
                                            new_state[y, x] = 0
                                            new_ptype[y, x] = 0
                                            new_size[y, x] = 0
                                            moved = True
                                            break
                                    if moved:
                                        break
    return new_state, new_charge, new_ptype, new_size

def external_signals(state, ptype, size):
    """
    Случайным образом возбуждает одну клетку с вероятностью EXTERNAL_SIGNAL_PROB.
    Устанавливает тип горячей (TYPE_HOT) и начальный размер INITIAL_SIZE.
    """
    from settings import EXTERNAL_SIGNAL_PROB, TYPE_HOT, INITIAL_SIZE
    if random.random() < EXTERNAL_SIGNAL_PROB:
        rx = random.randint(0, GRID_SIZE - 1)
        ry = random.randint(0, GRID_SIZE - 1)
        state[ry, rx] = 1
        ptype[ry, rx] = TYPE_HOT
        size[ry, rx] = INITIAL_SIZE

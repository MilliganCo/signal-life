import pygame
import numpy as np
import random

# ========== Параметры модели ==========
GRID_SIZE = 50         # Число клеток по горизонтали и вертикали
CELL_SIZE = 12         # Размер клетки в пикселях
FPS = 10               # Кадров в секунду

# Порог активации, будет изменяться клавишами
THRESHOLD = 2.5

# Длительность полного восстановления (кол-во шагов)
REFRACTORY_DURATION = 5

# Вероятность внешнего сигнала (случайного возбуждения)
EXTERNAL_SIGNAL_PROB = 0.02

# Ядро (3x3) для свёртки сигналов, можно менять коэффициенты
# Например, более сложная схема, чем просто 1.0
KERNEL = np.array([
    [0.2, 0.5, 0.2],
    [0.5, 0.0, 0.5],
    [0.2, 0.5, 0.2]
])

# Цвета (R,G,B) для разных состояний
COLOR_CALM       = (0, 0, 0)         # спокойная клетка (0)
COLOR_EXCITED    = (255, 255, 0)     # возбуждённая (1)
COLOR_RECOVERY_2 = (180, 0, 180)     # примерный цвет восстановления
# Можно делать плавную градацию восстановления

# ========== Инициализация Pygame ==========
pygame.init()
screen = pygame.display.set_mode((GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE))
pygame.display.set_caption("Signal Life: Advanced CA")

clock = pygame.time.Clock()

# ========== Массив состояний ==========
# 0 — спокойная, 1 — возбуждённая, 2..2+T-1 — стадии восстановления
state = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)

# ========== Функции ==========

def in_bounds(x, y):
    """Проверка, лежат ли координаты в границах решётки."""
    return (0 <= x < GRID_SIZE) and (0 <= y < GRID_SIZE)

def get_signal(state, x, y):
    """
    Вычисляет «сигнал» от соседей для клетки (x,y), используя KERNEL.
    Будем считать, что клетка даёт вклад в сигнал,
    только если она в состоянии возбуждения (1).
    """
    rows, cols = KERNEL.shape
    half = rows // 2
    s = 0.0
    for dy in range(-half, half+1):
        for dx in range(-half, half+1):
            nx = x + dx
            ny = y + dy
            if in_bounds(nx, ny):
                # Если клетка возбуждена, добавляем вес из ядра
                if state[ny, nx] == 1:
                    k = KERNEL[dy+half, dx+half]
                    s += k
    return s

def update_state(state):
    """
    Обновляет состояние клеток по правилам:
      1) 0 -> 1, если сигнал >= THRESHOLD
      2) 1 -> 2 (начало восстановления)
      3) 2..(2+T-1) -> +1 (глубже в восстановлении)
         и если достигли 2 + (T-1), то на следующем шаге вернуться в 0
    """
    new_state = state.copy()
    rows, cols = state.shape

    for y in range(rows):
        for x in range(cols):
            val = state[y, x]
            if val == 0:
                # Спокойная клетка, проверяем суммарный сигнал
                signal = get_signal(state, x, y)
                if signal >= THRESHOLD:
                    new_state[y, x] = 1  # возбуждаем
            elif val == 1:
                # Была возбуждена, переходит в начало восстановления
                new_state[y, x] = 2
            else:
                # Восстановление
                if val < 2 + (REFRACTORY_DURATION - 1):
                    # просто +1 стадия
                    new_state[y, x] = val + 1
                else:
                    # заканчиваем восстановление
                    new_state[y, x] = 0
    return new_state

def external_signals(state):
    """
    С некоторой вероятностью возбуждаем случайную клетку.
    """
    rows, cols = state.shape
    if random.random() < EXTERNAL_SIGNAL_PROB:
        rx = random.randint(0, cols-1)
        ry = random.randint(0, rows-1)
        state[ry, rx] = 1  # возбуждаем клетку

def draw_grid(screen, state):
    """
    Рисуем клетки на экране.
    Состояния:
      0 - чёрный
      1 - жёлтый
      2..2+T-1 - фиолетовые (или градиент)
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
                # Восстановление. Можно градиентом
                # Чем выше val, тем бледнее, например
                # Для упрощения: возьмём фиолетовый,
                # но можно усложнить.
                fraction = (val - 2) / float(REFRACTORY_DURATION-1)
                # fraction от 0 до 1
                r = int(180 + fraction * 50)  # 180..230
                g = 0
                b = int(180 - fraction * 80)  # 180..100
                color = (r, g, b)

            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

def handle_mouse(state):
    """
    ЛКМ - возбуждаем клетку
    """
    mouse_pressed = pygame.mouse.get_pressed()
    if mouse_pressed[0]:  # левая кнопка
        mx, my = pygame.mouse.get_pos()
        gx = mx // CELL_SIZE
        gy = my // CELL_SIZE
        if in_bounds(gx, gy):
            state[gy, gx] = 1

def handle_keys(event):
    """
    Изменяем THRESHOLD по нажатию клавиш: вверх/вниз
    """
    global THRESHOLD
    if event.key == pygame.K_UP:
        THRESHOLD += 0.1
        print(f"THRESHOLD = {THRESHOLD:.2f}")
    elif event.key == pygame.K_DOWN:
        THRESHOLD = max(0.1, THRESHOLD - 0.1)  # не даём уйти в отрицательные
        print(f"THRESHOLD = {THRESHOLD:.2f}")

# ========== Основной цикл ==========
running = True
while running:
    clock.tick(FPS)

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            handle_keys(event)

    # Мышь: «рисуем» возбуждённые клетки
    handle_mouse(state)

    # Внешние сигналы
    external_signals(state)

    # Обновляем состояние
    state = update_state(state)

    # Отрисовка
    screen.fill((0, 0, 0))
    draw_grid(screen, state)
    pygame.display.flip()

pygame.quit()

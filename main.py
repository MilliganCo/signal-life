import pygame
import numpy as np
from settings import GRID_SIZE, CELL_SIZE, FPS, THRESHOLD as INIT_THRESHOLD, TYPE_HOT, TYPE_SUPER, TYPE_COLD
from automata import update_state_with_charge, external_signals
from input_manager import handle_mouse, handle_keys
from display_manager import draw_grid
from gui_manager import GUIManager

pygame.init()

# Определяем размеры: игровое поле + панель GUI (ширина панели 220 пикселей)
SIM_WIDTH = GRID_SIZE * CELL_SIZE
PANEL_WIDTH = 220
WINDOW_WIDTH = SIM_WIDTH + PANEL_WIDTH
WINDOW_HEIGHT = GRID_SIZE * CELL_SIZE

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Advanced Signal Life with Metrics")
clock = pygame.time.Clock()

# Создаем менеджер GUI для всей области окна
gui_manager = GUIManager(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

# Глобальный словарь для управления параметрами симуляции
globals_dict = {
    'THRESHOLD': INIT_THRESHOLD,
    'paused': False,
    'current_ptype': TYPE_HOT  # По умолчанию рисуем горячие частицы
}

# Инициализация матриц симуляции
state = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
charge = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)
ptype = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)  # 0 – пустая, 1 – горячие, 2 – сверхпроводимые, 3 – холодные
size = np.zeros((GRID_SIZE, GRID_SIZE), dtype=float)  # Размер/масса частицы

running = True
while running:
    time_delta = clock.tick(FPS) / 1000.0

    # Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Передаем событие GUI менеджеру
        gui_manager.process_event(event)
        if event.type == pygame.KEYDOWN:
            handle_keys(event, globals_dict)

    # Обновляем GUI
    gui_manager.update(time_delta)
    gui_manager.update_labels()

    # Получаем параметры симуляции из GUI (например, порог возбуждения)
    gui_params = gui_manager.get_parameters()
    threshold = gui_params['THRESHOLD']

    # Обновляем локальные переменные из globals_dict
    paused = globals_dict['paused']
    current_ptype = globals_dict['current_ptype']

    # Рисование мышью: установка клетки с выбранным типом
    handle_mouse(state, ptype, size, current_ptype)

    if not paused:
        external_signals(state, ptype, size)
        state, charge, ptype, size = update_state_with_charge(state, charge, ptype, size, threshold)

    # Вычисление метрик симуляции
    hot_count = np.count_nonzero(ptype == TYPE_HOT)
    super_count = np.count_nonzero(ptype == TYPE_SUPER)
    cold_count = np.count_nonzero(ptype == TYPE_COLD)
    nonzero_charge = charge[state != 0]
    avg_charge = nonzero_charge.mean() if nonzero_charge.size > 0 else 0
    nonzero_size = size[size > 0]
    avg_size = nonzero_size.mean() if nonzero_size.size > 0 else 0

    gui_manager.update_metrics(hot_count, super_count, cold_count, avg_charge, avg_size)

    # Рисуем игровое поле (левая часть окна)
    simulation_surface = pygame.Surface((SIM_WIDTH, WINDOW_HEIGHT))
    simulation_surface.fill((50, 50, 50))
    # Функция draw_grid ожидает surface, state, threshold, ptype и current_ptype (если нужно для отрисовки)
    draw_grid(simulation_surface, state, threshold, ptype, current_ptype)
    screen.blit(simulation_surface, (0, 0))

    # Отрисовка элементов GUI (панель справа)
    gui_manager.draw_ui(screen)

    pygame.display.flip()

pygame.quit()

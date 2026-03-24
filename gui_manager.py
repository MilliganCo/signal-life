import pygame
import pygame_gui

class GUIManager:
    def __init__(self, screen_rect):
        # Создаем менеджер интерфейса для всего окна
        self.manager = pygame_gui.UIManager(screen_rect.size)
        # Панель расположим справа от игрового поля (ширина 220 пикселей)
        panel_rect = pygame.Rect(screen_rect.width - 220, 0, 220, screen_rect.height)
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=panel_rect,
            manager=self.manager
        )

        # Ползунок порога возбуждения (Threshold)
        self.threshold_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 10), (200, 30)),
            text="Threshold: 2.20",
            manager=self.manager,
            container=self.panel
        )
        self.threshold_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 45), (200, 30)),
            start_value=2.2,
            value_range=(0.1, 20),
            manager=self.manager,
            container=self.panel
        )

        # Ползунок утечки (Leakage)
        self.leakage_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 85), (200, 30)),
            text="Leakage: 0.05",
            manager=self.manager,
            container=self.panel
        )
        self.leakage_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 120), (200, 30)),
            start_value=0.05,
            value_range=(0.0, 1.0),
            manager=self.manager,
            container=self.panel
        )

        # Ползунок вероятности роста (Growth Prob)
        self.growth_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 160), (200, 30)),
            text="Growth Prob: 0.05",
            manager=self.manager,
            container=self.panel
        )
        self.growth_slider = pygame_gui.elements.UIHorizontalSlider(
            relative_rect=pygame.Rect((10, 195), (200, 30)),
            start_value=0.05,
            value_range=(0.0, 0.2),
            manager=self.manager,
            container=self.panel
        )

        # Метрики симуляции (количество клеток каждого типа, средний заряд, средний размер)
        self.metrics_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect((10, 240), (200, 100)),
            text="Metrics:\nHot: 0\nSuper: 0\nCold: 0\nAvg Charge: 0\nAvg Size: 0",
            manager=self.manager,
            container=self.panel
        )

    def process_event(self, event):
        self.manager.process_events(event)

    def update(self, time_delta):
        self.manager.update(time_delta)

    def draw_ui(self, screen):
        self.manager.draw_ui(screen)

    def update_metrics(self, hot, superp, cold, avg_charge, avg_size):
        metrics_text = (
            f"Metrics:\nHot: {hot}\nSuper: {superp}\nCold: {cold}\n"
            f"Avg Charge: {avg_charge:.2f}\nAvg Size: {avg_size:.2f}"
        )
        self.metrics_label.set_text(metrics_text)

    def update_labels(self):
        # Обновляем надписи ползунков согласно текущим значениям
        thr_val = self.threshold_slider.get_current_value()
        self.threshold_label.set_text(f"Threshold: {thr_val:.2f}")

        lev_val = self.leakage_slider.get_current_value()
        self.leakage_label.set_text(f"Leakage: {lev_val:.2f}")

        growth_val = self.growth_slider.get_current_value()
        self.growth_label.set_text(f"Growth Prob: {growth_val:.2f}")

    def get_parameters(self):
        return {
            'THRESHOLD': self.threshold_slider.get_current_value(),
            'LEAKAGE': self.leakage_slider.get_current_value(),
            'GROWTH_PROB': self.growth_slider.get_current_value()
        }

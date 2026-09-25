# data_manager.py
import os
import pandas as pd
import numpy as np
from typing import Tuple, List, Optional
from models import PlotItem, HelperLine, StyleConfig


class DataManager:
    """Класс для управления данными графиков, вспомогательными линиями и их обработкой."""
    
    def __init__(self) -> None:
        self.plots: List[PlotItem] = []
        self.config: StyleConfig = StyleConfig()
        
        # Границы данных для осей
        self.all_data_bounds: List[float] = [float('inf'), float('-inf')]
        self.global_y_max: float = 0.0

    def load_data_from_file(self, filepath: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Загружает данные времени и интенсивности из CSV/TXT файла.
        
        :param filepath: Путь к файлу.
        :return: Кортеж (массив_времени, массив_интенсивности) или (None, None) при ошибке.
        """
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            start_row = 0
            
            # Ищем начало данных (строка начинается с цифры)
            for i, line in enumerate(lines):
                if line.strip() and line[0].isdigit():
                    start_row = i
                    break
            
            df = pd.read_csv(filepath, sep=';', decimal=',', skiprows=start_row, header=None)
            time_data = pd.to_numeric(df.iloc[:, 0], errors='coerce').values
            intensity_data = pd.to_numeric(df.iloc[:, 1], errors='coerce').values
            
            # Отфильтровываем NaN значения
            mask = ~np.isnan(intensity_data)
            return time_data[mask], intensity_data[mask]
            
        except Exception as e:
            print(f"Ошибка при загрузке данных из {filepath}: {e}")
            return None, None

    def add_plot(self, filepath: str, color: str, line_width: float) -> Optional[PlotItem]:
        """Создает и добавляет новый график в реестр."""
        t_raw, y = self.load_data_from_file(filepath)
        if t_raw is None or y is None:
            return None
            
        label = os.path.basename(filepath).split('.')[0]
        
        plot_item = PlotItem(
            t_raw=t_raw,
            y_orig=y,
            color=color,
            label=label,
            line_width=line_width,
            filepath=filepath
        )
        
        self.plots.append(plot_item)
        self.global_y_max = max(self.global_y_max, y.max())
        self.recalculate_time_data()
        
        return plot_item

    def remove_plot(self, index: int) -> None:
        """Удаляет график по индексу и пересчитывает границы."""
        if 0 <= index < len(self.plots):
            self.plots.pop(index)
            self.recalculate_bounds()

    def move_plot(self, index: int, direction: int) -> None:
        """Перемещает график в списке (влияет на z-order при отрисовке)."""
        new_index = index + direction
        if 0 <= index < len(self.plots) and 0 <= new_index < len(self.plots):
            self.plots[index], self.plots[new_index] = self.plots[new_index], self.plots[index]

    def add_helper_line(self, plot_idx: int, line_type: str, pos: float, start: float, end: float) -> Optional[HelperLine]:
        """Добавляет вспомогательную линию к конкретному графику."""
        if 0 <= plot_idx < len(self.plots):
            helper = HelperLine(
                line_type=line_type,
                pos=pos,
                start=start,
                end=end,
                label_pos=end
            )
            self.plots[plot_idx].helpers.append(helper)
            return helper
        return None

    def remove_helper_line(self, plot_idx: int, helper_idx: int) -> None:
        """Удаляет вспомогательную линию по индексам."""
        if 0 <= plot_idx < len(self.plots):
            if 0 <= helper_idx < len(self.plots[plot_idx].helpers):
                self.plots[plot_idx].helpers.pop(helper_idx)

    def recalculate_time_data(self) -> None:
        """
        Пересчитывает массив времени `t` для всех графиков с учетом 
        глобального смещения, индивидуального смещения и перевода в минуты.
        """
        factor = 60.0 if self.config.convert_sec_to_min else 1.0
        
        for item in self.plots:
            item.t = (item.t_raw / factor) + item.x_offset
            
        self.recalculate_bounds()

    def recalculate_bounds(self) -> None:
        """Пересчитывает глобальные границы по оси X (времени)."""
        if not self.plots:
            self.all_data_bounds = [float('inf'), float('-inf')]
            self.global_y_max = 0.0
            return
            
        new_min = float('inf')
        new_max = float('-inf')
        
        for item in self.plots:
            if len(item.t) > 0:
                new_min = min(new_min, item.t.min())
                new_max = max(new_max, item.t.max())
                
        self.all_data_bounds = [new_min, new_max]

    def clear_all(self) -> None:
        """Очищает все данные."""
        self.plots.clear()
        self.all_data_bounds = [float('inf'), float('-inf')]
        self.global_y_max = 0.0
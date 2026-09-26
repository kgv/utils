# models.py
import uuid
from dataclasses import dataclass, field
from typing import List
import numpy as np


@dataclass
class StyleConfig:
    """Хранит все настройки оформления графика и приложения."""
    # Общие шрифты
    gen_font: str = 'Arial'
    gen_weight: str = 'normal'
    gen_style: str = 'normal'
    
    # Шрифты заголовка
    title_font: str = 'Inherit'
    title_weight: str = 'Inherit'
    title_style: str = 'Inherit'
    title_size: float = 14.0
    
    # Шрифты подписей осей
    label_font: str = 'Inherit'
    label_weight: str = 'Inherit'
    label_style: str = 'Inherit'
    label_size: float = 12.0
    
    # Шрифты делений (тиков)
    tick_font: str = 'Inherit'
    tick_weight: str = 'Inherit'
    tick_style: str = 'Inherit'
    tick_size: float = 10.0
    
    # Шрифты легенды
    legend_font: str = 'Inherit'
    legend_weight: str = 'Inherit'
    legend_style: str = 'Inherit'
    legend_size: float = 10.0
    
    # Линии и сетка
    grid_alpha: float = 0.3
    grid_width: float = 0.8
    spine_width: float = 1.0
    
    # Деления (тики)
    major_tick_width: float = 1.2
    major_tick_length: float = 5.0
    minor_tick_width: float = 0.8
    minor_tick_length: float = 3.0
    x_major_step: float = 0.0
    y_major_step: float = 0.0
    x_minor_step: float = 0.0
    y_minor_step: float = 0.0
    
    # Тексты
    title_text: str = 'EIC Chromatograms'
    x_label: str = 'Время (мин)'
    y_label_abs: str = 'Интенсивность (Counts)'
    y_label_norm: str = 'Относительная интенсивность (%)'
    
    # Состояние отображения
    show_legend: bool = True
    legend_position: str = 'best'
    
    # Размеры графика
    fig_width: float = 10.0
    fig_height: float = 6.0
    
    # Глобальные настройки данных (сохраняются вместе со стилем)
    convert_sec_to_min: bool = False
    reverse_x: bool = False

    # Настройки масштаба
    y_mode: str = "Абсолютный"
    x_min: float = 0.0
    x_max: float = 1.0
    y_min: float = 0.0
    y_max: float = 100.0


@dataclass
class PlotItem:
    """Модель данных одного графика (хроматограммы)."""
    t_raw: np.ndarray
    y_orig: np.ndarray
    color: str
    label: str
    filepath: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    t: np.ndarray = field(init=False)
    linestyle: str = '-'
    line_width: float = 1.5
    show_in_legend: bool = True
    x_offset: float = 0.0
    y_offset: float = 0.0
    visible: bool = True
    helpers: List['HelperLine'] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Инициализация массива времени после создания объекта."""
        self.t = self.t_raw.copy()


@dataclass
class HelperLine:
    """Модель данных вспомогательной линии (вертикальной или горизонтальной)."""
    line_type: str  # 'V' или 'H'
    pos: float
    start: float
    end: float
    label_pos: float
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    color: str = '#000000'
    width: float = 0.5
    text: str = ''
    label_offset: float = 0.0
    label_rotation: int = 0
    layer: str = 'Задний'
    font_size: int = 9
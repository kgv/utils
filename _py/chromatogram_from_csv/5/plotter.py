# plotter.py
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoLocator, NullLocator
from matplotlib.lines import Line2D
import numpy as np
from typing import Dict, List, Tuple

from models import StyleConfig, PlotItem, HelperLine
from data_manager import DataManager


class ChromatogramPlotter:
    """Класс для управления отрисовкой графиков Matplotlib. Не зависит от Tkinter."""

    def __init__(self) -> None:
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.subplots_adjust(bottom=0.2, left=0.12, top=0.9, right=0.95)
        
        # Словарь для связи ID модели PlotItem с объектом Line2D в Matplotlib
        self.plot_lines: Dict[str, Line2D] = {}
        # Список для хранения объектов вспомогательных линий и текстов
        self.helper_artists: List[plt.Artist] = []

    def get_figure(self) -> plt.Figure:
        """Возвращает объект Figure для встраивания в Tkinter."""
        return self.fig

    def _resolve_font(self, config: StyleConfig, prefix: str, prop: str) -> str:
        """Разрешает наследование шрифтов (если стоит 'Inherit', берет общий шрифт)."""
        val = getattr(config, f"{prefix}_{prop}")
        if val == "Inherit":
            return getattr(config, f"gen_{prop}")
        return val

    def refresh(self, data_manager: DataManager, x_min: float, x_max: float, 
                y_mode: str, auto_y: bool, y_min: float, y_max: float) -> Tuple[float, float]:
        """
        Основной метод обновления графика.
        Возвращает новые границы Y (y_min, y_max), если был включен авто-масштаб.
        """
        config = data_manager.config
        
        # 1. Синхронизация линий (создание новых, удаление старых)
        current_ids = {item.id for item in data_manager.plots}
        for plot_id in list(self.plot_lines.keys()):
            if plot_id not in current_ids:
                self.plot_lines[plot_id].remove()
                del self.plot_lines[plot_id]

        # 2. Обновление данных и стилей графиков
        for i, item in enumerate(data_manager.plots):
            if item.id not in self.plot_lines:
                line, = self.ax.plot([], [])
                self.plot_lines[item.id] = line
            
            line = self.plot_lines[item.id]
            
            # Применение данных по X
            line.set_xdata(item.t)
            
            # Применение данных по Y (с учетом нормализации)
            if y_mode == "Нормированный":
                mask = (item.t >= x_min) & (item.t <= x_max)
                v_y = item.y_orig[mask]
                max_y = v_y.max() if v_y.size and v_y.max() > 0 else 1.0
                base_y = (item.y_orig / max_y) * 100 if v_y.size else item.y_orig * 0
                line.set_ydata(base_y + item.y_offset)
            else:
                line.set_ydata(item.y_orig + item.y_offset)
            
            # Применение стилей линии
            line.set_color(item.color)
            line.set_linestyle(item.linestyle)
            line.set_linewidth(item.line_width)
            line.set_visible(item.visible)
            line.set_zorder(i + 10)  # Базовый z-order для графиков
            
            # Легенда
            show_leg = item.show_in_legend and item.visible
            line.set_label(item.label if show_leg else "_nolegend_")

        # 3. Настройка оси X
        safe_x_max = x_max if x_max > x_min else x_min + 0.01
        if config.reverse_x:
            self.ax.set_xlim(safe_x_max, x_min)
        else:
            self.ax.set_xlim(x_min, safe_x_max)

        # 4. Настройка оси Y (Автомасштаб)
        new_y_min, new_y_max = y_min, y_max
        if auto_y:
            calc_y_min, calc_y_max = float('inf'), float('-inf')
            
            if data_manager.plots:
                for item in data_manager.plots:
                    if item.visible and len(item.y_orig) > 0:
                        y_data = self.plot_lines[item.id].get_ydata()
                        calc_y_min = min(calc_y_min, y_data.min())
                        calc_y_max = max(calc_y_max, y_data.max())
                
                if calc_y_max != float('-inf'):
                    yr = calc_y_max - calc_y_min if calc_y_max > calc_y_min else (calc_y_max if calc_y_max > 0 else 1)
                    new_y_min = calc_y_min - yr * 0.02
                    new_y_max = calc_y_max - yr * 0.05
                else:
                    new_y_min, new_y_max = (0, 105) if y_mode == "Нормированный" else (0, 1)
            else:
                # Если графиков нет, ориентируемся на вспомогательные линии
                all_y_coords = []
                for h in data_manager.helpers:
                    if h.line_type == 'H':
                        all_y_coords.append(h.pos)
                    else:
                        all_y_coords.extend([h.start, h.end])
                
                if all_y_coords:
                    min_y, max_y = min(all_y_coords), max(all_y_coords)
                    padding = (max_y - min_y) * 0.1 if (max_y - min_y) > 0 else 1.0
                    new_y_min, new_y_max = min_y - padding, max_y + padding
                else:
                    new_y_min, new_y_max = (0, 105) if y_mode == "Нормированный" else (0, 1)
            
            self.ax.set_ylim(new_y_min, new_y_max)
        else:
            self.ax.set_ylim(y_min, y_max)

        # 5. Отрисовка вспомогательных линий
        self._draw_helper_lines(data_manager.helpers)

        # 6. Применение глобальных стилей (шрифты, сетка, тики)
        self._apply_style(config, y_mode)
        
        return new_y_min, new_y_max

    def _draw_helper_lines(self, helpers: List[HelperLine]) -> None:
        """Отрисовывает вспомогательные линии и текст."""
        for artist in self.helper_artists:
            artist.remove()
        self.helper_artists.clear()

        for h in helpers:
            z = 1 if h.layer == 'Задний' else 50
            txt = h.text if h.text.strip() else str(h.pos)
            
            if h.line_type == 'V':
                line, = self.ax.plot([h.pos, h.pos], [h.start, h.end], color=h.color, lw=h.width, zorder=z)
                tx = h.pos + h.label_offset
                ty = h.label_pos
            else:
                line, = self.ax.plot([h.start, h.end], [h.pos, h.pos], color=h.color, lw=h.width, zorder=z)
                ty = h.pos + h.label_offset
                tx = h.label_pos
                
            text_artist = self.ax.text(
                tx, ty, txt, color=h.color, fontsize=h.font_size,
                va='center', ha='center', fontweight='bold', zorder=z+1,
                rotation=h.label_rotation, rotation_mode='anchor'
            )
            self.helper_artists.extend([line, text_artist])

    def _apply_style(self, config: StyleConfig, y_mode: str) -> None:
        """Применяет настройки оформления к осям, сетке и легенде."""
        # Заголовки
        self.ax.set_title(
            config.title_text,
            fontfamily=self._resolve_font(config, 'title', 'font'),
            fontweight=self._resolve_font(config, 'title', 'weight'),
            fontstyle=self._resolve_font(config, 'title', 'style'),
            fontsize=config.title_size
        )
        
        y_label_text = config.y_label_norm if y_mode == "Нормированный" else config.y_label_abs
        
        for axis, label in [(self.ax.xaxis, config.x_label), (self.ax.yaxis, y_label_text)]:
            axis.set_label_text(
                label,
                fontfamily=self._resolve_font(config, 'label', 'font'),
                fontweight=self._resolve_font(config, 'label', 'weight'),
                fontstyle=self._resolve_font(config, 'label', 'style'),
                fontsize=config.label_size
            )

        # Тики (деления)
        for ax_obj in [self.ax.xaxis, self.ax.yaxis]:
            for tick in ax_obj.get_ticklabels():
                tick.set_fontfamily(self._resolve_font(config, 'tick', 'font'))
                tick.set_fontweight(self._resolve_font(config, 'tick', 'weight'))
                tick.set_fontstyle(self._resolve_font(config, 'tick', 'style'))
                tick.set_fontsize(config.tick_size)

        self.ax.tick_params(which='major', width=config.major_tick_width, length=config.major_tick_length)
        self.ax.tick_params(which='minor', width=config.minor_tick_width, length=config.minor_tick_length)
        
        self.ax.xaxis.set_major_locator(MultipleLocator(config.x_major_step) if config.x_major_step > 0 else AutoLocator())
        self.ax.xaxis.set_minor_locator(MultipleLocator(config.x_minor_step) if config.x_minor_step > 0 else NullLocator())
        self.ax.yaxis.set_major_locator(MultipleLocator(config.y_major_step) if config.y_major_step > 0 else AutoLocator())
        self.ax.yaxis.set_minor_locator(MultipleLocator(config.y_minor_step) if config.y_minor_step > 0 else NullLocator())

        # Рамка и сетка
        for spine in self.ax.spines.values():
            spine.set_linewidth(config.spine_width)
            
        self.ax.grid(False)
        self.ax.grid(visible=True, which='major', alpha=config.grid_alpha, lw=config.grid_width)

        # Легенда
        if self.ax.get_legend():
            self.ax.get_legend().remove()
            
        if config.show_legend and self.plot_lines:
            leg = self.ax.legend(fontsize=config.legend_size)
            if leg:
                plt.setp(
                    leg.get_texts(),
                    fontfamily=self._resolve_font(config, 'legend', 'font'),
                    fontweight=self._resolve_font(config, 'legend', 'weight'),
                    fontstyle=self._resolve_font(config, 'legend', 'style')
                )

    def resize_figure(self, width: float, height: float) -> None:
        """Изменяет физический размер графика (в дюймах)."""
        self.fig.set_size_inches(width, height)

    def save_figure(self, filepath: str) -> None:
        """Сохраняет график в файл."""
        ext = filepath.split('.')[-1].lower()
        if ext == 'png':
            self.fig.savefig(filepath, format='png', bbox_inches='tight', dpi=300)
        else:
            self.fig.savefig(filepath, format='svg', bbox_inches='tight')

    def clear(self) -> None:
        """Полностью очищает график."""
        for line in self.plot_lines.values():
            line.remove()
        self.plot_lines.clear()
        
        for artist in self.helper_artists:
            artist.remove()
        self.helper_artists.clear()
        
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
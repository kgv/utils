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
        
        self.plot_lines: Dict[str, Line2D] = {}
        self.helper_artists: List[plt.Artist] = []

        # --- Объекты для наведения (hover) ---
        self.hover_point, = self.ax.plot([], [], 'ro', markersize=6, zorder=100, visible=False)
        self.hover_text = self.ax.annotate(
            "", xy=(0, 0), xytext=(10, 10), textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
            zorder=101, visible=False
        )

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
                y_mode: str, y_min: float, y_max: float) -> None:
        """
        Основной метод обновления графика.
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

        # 4. Настройка оси Y
        self.ax.set_ylim(y_min, y_max)

        # 5. Отрисовка вспомогательных линий
        self._draw_helper_lines(data_manager.plots)

        # 6. Применение глобальных стилей (шрифты, сетка, тики)
        self._apply_style(config, y_mode)

    def _draw_helper_lines(self, plots: List[PlotItem]) -> None:
        """Отрисовывает вспомогательные линии и текст."""
        for artist in self.helper_artists:
            artist.remove()
        self.helper_artists.clear()

        for p in plots:
            if not p.visible: continue  # Скрываем линии, если скрыт сам график
            for h in p.helpers:
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
                    va='bottom', ha='center', fontweight='bold', zorder=z+1,
                    rotation=h.label_rotation,
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
        
        # --- Скрываем hover ---
        self.hover_point.set_visible(False)
        self.hover_text.set_visible(False)
        
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)
    
    def update_hover(self, event_x: float, event_y: float, event_xdata: float, event_ydata: float):
        """Ищет ближайшую точку к курсору и обновляет маркер."""
        closest_dist = float('inf')
        closest_data = None

        # Ищем ближайшую точку среди всех видимых графиков
        for line in self.plot_lines.values():
            if not line.get_visible(): continue
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            if len(x_data) == 0: continue

            # Находим ближайший X в данных
            idx = np.argmin(np.abs(x_data - event_xdata))
            px, py = x_data[idx], y_data[idx]

            # Переводим координаты данных в пиксели экрана для точного расчета расстояния
            disp_pt = self.ax.transData.transform((px, py))
            dist = np.hypot(disp_pt[0] - event_x, disp_pt[1] - event_y)

            # Порог срабатывания - 30 пикселей
            if dist < closest_dist and dist < 30:
                closest_dist = dist
                closest_data = (px, py)

        if closest_data:
            self.hover_point.set_data([closest_data[0]], [closest_data[1]])
            self.hover_text.set_text(f"X: {closest_data[0]:.3f}\nY: {closest_data[1]:.2f}")
            self.hover_text.xy = (closest_data[0], closest_data[1])
            self.hover_point.set_visible(True)
            self.hover_text.set_visible(True)
            return closest_data
        else:
            self.hover_point.set_visible(False)
            self.hover_text.set_visible(False)
            return None
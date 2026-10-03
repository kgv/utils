# plotter.py
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, AutoLocator, NullLocator
from matplotlib.lines import Line2D
import numpy as np
from typing import Dict, List, Tuple

from models import StyleConfig, PlotItem, PlotMarker
from data_manager import DataManager


class ChromatogramPlotter:
    """Класс для управления отрисовкой графиков Matplotlib. Не зависит от Tkinter."""

    def __init__(self) -> None:
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.fig.subplots_adjust(bottom=0.2, left=0.12, top=0.9, right=0.95)

        self.plot_lines: Dict[str, Line2D] = {}
        self.helper_artists: List[plt.Artist] = []

        # --- Объекты для наведения (hover) ---
        (self.hover_point,) = self.ax.plot(
            [], [], "ro", markersize=6, zorder=100, visible=False
        )
        self.hover_text = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.9),
            zorder=101,
            visible=False,
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

    def refresh(self, data_manager: DataManager) -> None:
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

        global_x_min, global_x_max = float("inf"), float("-inf")
        global_y_min, global_y_max = float("inf"), float("-inf")
        any_normalized = False
        has_visible = False

        # 2. Обновление данных и стилей графиков
        for i, item in enumerate(data_manager.plots):
            if item.id not in self.plot_lines:
                (line,) = self.ax.plot([], [])
                self.plot_lines[item.id] = line

            line = self.plot_lines[item.id]

            if not item.visible:
                line.set_visible(False)
                continue

            has_visible = True
            line.set_visible(True)

            # Маскируем данные по индивидуальным границам X
            mask = (item.t >= item.x_min) & (item.t <= item.x_max)
            t_masked = item.t[mask]
            y_masked = item.y_orig[mask]

            # Применение данных по Y (с учетом индивидуальной нормализации)
            if item.y_mode == "Нормированный":
                any_normalized = True
                max_y = y_masked.max() if y_masked.size and y_masked.max() > 0 else 1.0
                base_y = (y_masked / max_y) * 100 if y_masked.size else np.array([])
                line.set_ydata(base_y + item.y_offset)
            else:
                line.set_ydata(y_masked + item.y_offset)

            # Применение данных по X
            line.set_xdata(t_masked)

            # Применение стилей линии
            line.set_color(item.color)
            line.set_linestyle(item.linestyle)
            line.set_linewidth(item.line_width)
            line.set_zorder(i + 10)

            # Легенда
            show_leg = item.show_in_legend
            line.set_label(item.label if show_leg else "_nolegend_")

            # Обновляем глобальный Viewport
            global_x_min = min(global_x_min, item.x_min)
            global_x_max = max(global_x_max, item.x_max)
            global_y_min = min(global_y_min, item.y_min)
            global_y_max = max(global_y_max, item.y_max)

        # 3. Настройка осей (Viewport)
        if has_visible:
            safe_x_max = (
                global_x_max if global_x_max > global_x_min else global_x_min + 0.01
            )
            self.ax.set_xlim(global_x_min, safe_x_max)

            safe_y_max = (
                global_y_max if global_y_max > global_y_min else global_y_min + 0.01
            )
            self.ax.set_ylim(global_y_min, safe_y_max)
        else:
            self.ax.set_xlim(0, 1)
            self.ax.set_ylim(0, 100)

        # 4. Отрисовка меток
        self._draw_markers(data_manager.plots)

        # 5. Применение глобальных стилей
        self._apply_style(config, any_normalized)

    def _draw_markers(self, plots: List[PlotItem]) -> None:
        """Отрисовывает метки и линии связи."""
        for artist in self.helper_artists:
            artist.remove()
        self.helper_artists.clear()

        for p in plots:
            if not p.visible:
                continue
            for m in p.markers:
                # Пропускаем скрытые метки
                if not getattr(m, "visible", True):
                    continue

                z = 1 if m.layer == "Задний" else 50
                txt = m.text if m.text.strip() else f"{m.anchor_x:.2f}"

                if m.offset_y >= 0:
                    va_val = "bottom"
                    rel_pos = (0.5, 0.0)
                else:
                    va_val = "top"
                    rel_pos = (0.5, 1.0)

                arrowprops = None
                if m.show_connector:
                    arrowprops = dict(
                        arrowstyle="-",
                        color=m.color,
                        lw=m.width,
                        shrinkA=0,
                        shrinkB=0,
                        relpos=rel_pos,
                    )

                text_artist = self.ax.annotate(
                    txt,
                    xy=(m.anchor_x, m.anchor_y),
                    xytext=(m.anchor_x + m.offset_x, m.anchor_y + m.offset_y),
                    textcoords="data",
                    color=m.color,
                    fontsize=m.font_size,
                    va=va_val,
                    ha="center",
                    fontweight="bold",
                    zorder=z + 1,
                    rotation=m.label_rotation,
                    arrowprops=arrowprops,
                )
                self.helper_artists.append(text_artist)

    def _apply_style(self, config: StyleConfig, any_normalized: bool) -> None:
        """Применяет настройки оформления к осям, сетке и легенде."""
        self.ax.set_title(
            config.title_text,
            fontfamily=self._resolve_font(config, "title", "font"),
            fontweight=self._resolve_font(config, "title", "weight"),
            fontstyle=self._resolve_font(config, "title", "style"),
            fontsize=config.title_size,
        )

        y_label_text = config.y_label_norm if any_normalized else config.y_label_abs

        for axis, label in [
            (self.ax.xaxis, config.x_label),
            (self.ax.yaxis, y_label_text),
        ]:
            axis.set_label_text(
                label,
                fontfamily=self._resolve_font(config, "label", "font"),
                fontweight=self._resolve_font(config, "label", "weight"),
                fontstyle=self._resolve_font(config, "label", "style"),
                fontsize=config.label_size,
            )

        for ax_obj in [self.ax.xaxis, self.ax.yaxis]:
            for tick in ax_obj.get_ticklabels():
                tick.set_fontfamily(self._resolve_font(config, "tick", "font"))
                tick.set_fontweight(self._resolve_font(config, "tick", "weight"))
                tick.set_fontstyle(self._resolve_font(config, "tick", "style"))
                tick.set_fontsize(config.tick_size)

        self.ax.tick_params(
            which="major",
            width=config.major_tick_width,
            length=config.major_tick_length,
        )
        self.ax.tick_params(
            which="minor",
            width=config.minor_tick_width,
            length=config.minor_tick_length,
        )

        self.ax.xaxis.set_major_locator(
            MultipleLocator(config.x_major_step)
            if config.x_major_step > 0
            else AutoLocator()
        )
        self.ax.xaxis.set_minor_locator(
            MultipleLocator(config.x_minor_step)
            if config.x_minor_step > 0
            else NullLocator()
        )
        self.ax.yaxis.set_major_locator(
            MultipleLocator(config.y_major_step)
            if config.y_major_step > 0
            else AutoLocator()
        )
        self.ax.yaxis.set_minor_locator(
            MultipleLocator(config.y_minor_step)
            if config.y_minor_step > 0
            else NullLocator()
        )

        for spine in self.ax.spines.values():
            spine.set_linewidth(config.spine_width)

        self.ax.grid(False)
        self.ax.grid(
            visible=True, which="major", alpha=config.grid_alpha, lw=config.grid_width
        )

        if self.ax.get_legend():
            self.ax.get_legend().remove()

        if config.show_legend and self.plot_lines:
            leg = self.ax.legend(
                fontsize=config.legend_size, loc=config.legend_position
            )
            if leg:
                plt.setp(
                    leg.get_texts(),
                    fontfamily=self._resolve_font(config, "legend", "font"),
                    fontweight=self._resolve_font(config, "legend", "weight"),
                    fontstyle=self._resolve_font(config, "legend", "style"),
                )

    def resize_figure(self, width: float, height: float) -> None:
        self.fig.set_size_inches(width, height)

    def save_figure(self, filepath: str) -> None:
        ext = filepath.split(".")[-1].lower()
        if ext == "png":
            self.fig.savefig(filepath, format="png", bbox_inches="tight", dpi=300)
        else:
            self.fig.savefig(filepath, format="svg", bbox_inches="tight")

    def clear(self) -> None:
        for line in self.plot_lines.values():
            line.remove()
        self.plot_lines.clear()

        for artist in self.helper_artists:
            artist.remove()
        self.helper_artists.clear()

        self.hover_point.set_visible(False)
        self.hover_text.set_visible(False)

        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)

    def update_hover(
        self, event_x: float, event_y: float, event_xdata: float, event_ydata: float
    ):
        candidates = []
        RADIUS_PX = 5

        inv_trans = self.ax.transData.inverted()
        p1 = inv_trans.transform((event_x - RADIUS_PX, event_y - RADIUS_PX))
        p2 = inv_trans.transform((event_x + RADIUS_PX, event_y + RADIUS_PX))

        x_min, x_max = min(p1[0], p2[0]), max(p1[0], p2[0])
        y_min, y_max = min(p1[1], p2[1]), max(p1[1], p2[1])

        for line in self.plot_lines.values():
            if not line.get_visible():
                continue
            x_data = line.get_xdata()
            y_data = line.get_ydata()
            if len(x_data) == 0:
                continue

            mask = (
                (x_data >= x_min)
                & (x_data <= x_max)
                & (y_data >= y_min)
                & (y_data <= y_max)
            )
            if not np.any(mask):
                continue

            f_x = x_data[mask]
            f_y = y_data[mask]

            xy_data = np.column_stack((f_x, f_y))
            xy_pixels = self.ax.transData.transform(xy_data)

            dists = np.hypot(xy_pixels[:, 0] - event_x, xy_pixels[:, 1] - event_y)
            valid_indices = np.where(dists <= RADIUS_PX)[0]

            for idx in valid_indices:
                candidates.append({"px": f_x[idx], "py": f_y[idx], "dist": dists[idx]})

        if candidates:
            best = min(candidates, key=lambda c: (-c["py"], c["dist"]))
            closest_data = (best["px"], best["py"])

            self.hover_point.set_data([closest_data[0]], [closest_data[1]])
            self.hover_text.set_text(
                f"X: {closest_data[0]:.3f}\nY: {closest_data[1]:.2f}"
            )
            self.hover_text.xy = closest_data
            self.hover_point.set_visible(True)
            self.hover_text.set_visible(True)
            return closest_data
        else:
            self.hover_point.set_visible(False)
            self.hover_text.set_visible(False)
            return None

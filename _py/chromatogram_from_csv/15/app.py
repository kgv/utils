# app.py
import tkinter as tk
from tkinter import filedialog, colorchooser
import json
import os
import numpy as np

from models import PlotMarker, StyleConfig
from data_manager import DataManager
from plotter import ChromatogramPlotter
from ui.main_window import MainWindow
from ui.control_panel import ControlPanel


class AppController:
    def __init__(self):
        self.data_manager = DataManager()
        self.plotter = ChromatogramPlotter()

        self.palette = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

        # Инициализация UI
        self.main_window = MainWindow(self, self.plotter.get_figure())
        self.control_panel = ControlPanel(self.main_window, self)

        # Применяем дефолтные стили к UI
        self.control_panel.tab_labels.set_values(self.data_manager.config)
        self.control_panel.tab_style.set_values(self.data_manager.config)

        self.ui_ready = True

        # --- Переменная состояния и привязка событий мыши ---
        self.current_hover_data = None
        self.main_window.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.main_window.canvas.mpl_connect("button_press_event", self.on_mouse_click)

        self.request_refresh(force=True)

    def run(self):
        self.main_window.mainloop()

    def request_refresh(self, force: bool = False) -> None:
        if not getattr(self, "ui_ready", False):
            return

        # Отрисовка
        self.plotter.refresh(self.data_manager)
        self.main_window.redraw_canvas()

    def refresh_ui(self):
        """Вспомогательный метод для обновления обеих панелей во вкладке Файлы."""
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        dx, dy = self._get_steps()
        self.control_panel.tab_files.update_markers(self.data_manager.plots, dx, dy)

    # --- Обработчики событий мыши (Hover и Клик) ---
    def on_mouse_move(self, event):
        if not getattr(self, "ui_ready", False):
            return

        if not event.inaxes:
            if self.current_hover_data is not None:
                self.current_hover_data = None
                self.plotter.hover_point.set_visible(False)
                self.plotter.hover_text.set_visible(False)
                self.main_window.redraw_canvas()
            return

        result = self.plotter.update_hover(event.x, event.y, event.xdata, event.ydata)

        if result != self.current_hover_data:
            self.current_hover_data = result
            self.main_window.redraw_canvas()

    def on_mouse_click(self, event):
        if event.inaxes and event.button == 1 and self.current_hover_data:
            x, y = self.current_hover_data
            clipboard_text = f"{x}\t{y}".replace(".", ",")

            self.main_window.clipboard_clear()
            self.main_window.clipboard_append(clipboard_text)

            self.plotter.hover_text.set_text("Скопировано!")
            self.main_window.redraw_canvas()

    # --- Обработчики файлов и графиков ---
    def on_add_files(self):
        paths = filedialog.askopenfilenames(
            filetypes=[("Data", "*.csv *.txt"), ("All", "*.*")]
        )
        if not paths:
            return

        for p in paths:
            color = self.palette[len(self.data_manager.plots) % len(self.palette)]
            self.data_manager.add_plot(p, color, 1.5)

        self.refresh_ui()
        self.request_refresh(force=True)

    def on_clear_all(self):
        self.data_manager.clear_all()
        self.plotter.clear()
        self.refresh_ui()
        self.request_refresh(force=True)

    def update_plot(self, idx: int, key: str, val: any):
        try:
            if key in [
                "line_width",
                "x_offset",
                "y_offset",
                "x_min",
                "x_max",
                "y_min",
                "y_max",
            ]:
                val = float(str(val).replace(",", "."))

            setattr(self.data_manager.plots[idx], key, val)

            if key in ["convert_sec_to_min", "reverse_x"]:
                self.data_manager.recalculate_time_data(reset_bounds=True)
                self.refresh_ui()
            elif key == "x_offset":
                self.data_manager.recalculate_time_data(reset_bounds=False)
            elif key == "visible":
                # Если изменилась видимость, нужно перерисовать панель меток
                self.refresh_ui()

            self.request_refresh()
        except ValueError:
            pass

    def on_move_plot(self, idx: int, direction: int):
        self.data_manager.move_plot(idx, direction)
        self.refresh_ui()
        self.request_refresh(force=True)

    def on_remove_plot(self, idx: int):
        self.data_manager.remove_plot(idx)
        self.refresh_ui()
        self.request_refresh(force=True)

    def on_fit_y_to_visible(self, idx: int):
        p = self.data_manager.plots[idx]
        mask = (p.t >= p.x_min) & (p.t <= p.x_max)

        if p.y_mode == "Нормированный":
            v_y = p.y_orig[mask]
            max_y = v_y.max() if v_y.size and v_y.max() > 0 else 1.0
            v = (v_y / max_y) * 100 + p.y_offset if v_y.size else np.array([])
        else:
            v = p.y_orig[mask] + p.y_offset

        if v.size:
            m_min, m_max = v.min(), v.max()
            yr = m_max - m_min if m_max > m_min else (m_max if m_max > 0 else 1)
            p.y_min = m_min - yr * 0.02
            p.y_max = m_max + yr * 0.05

            self.refresh_ui()
            self.request_refresh(force=True)

    def on_export_file_settings(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if not path:
            return

        plots_data = []
        for p in self.data_manager.plots:
            plot_dict = {
                "filepath": p.filepath,
                "color": p.color,
                "label": p.label,
                "linestyle": p.linestyle,
                "line_width": p.line_width,
                "show_in_legend": p.show_in_legend,
                "x_offset": p.x_offset,
                "y_offset": p.y_offset,
                "visible": p.visible,
                "y_mode": p.y_mode,
                "convert_sec_to_min": p.convert_sec_to_min,
                "reverse_x": p.reverse_x,
                "x_min": p.x_min,
                "x_max": p.x_max,
                "y_min": p.y_min,
                "y_max": p.y_max,
                "markers": [m.__dict__ for m in p.markers],
            }
            plots_data.append(plot_dict)

        export_data = {
            "style_config": self.data_manager.config.__dict__,
            "plots": plots_data,
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)

    def on_import_file_settings(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if isinstance(data, dict):
                style_data = data.get("style_config", {})
                plots_data = data.get("plots", [])

                for k, v in style_data.items():
                    if hasattr(self.data_manager.config, k):
                        setattr(self.data_manager.config, k, v)

                self.control_panel.tab_labels.set_values(self.data_manager.config)
                self.control_panel.tab_style.set_values(self.data_manager.config)
                self.on_apply_figure_size(
                    self.data_manager.config.fig_width,
                    self.data_manager.config.fig_height,
                    custom=True,
                )
            else:
                plots_data = data

            for p_dict in plots_data:
                filepath = p_dict.get("filepath")
                if not filepath or not os.path.exists(filepath):
                    print(f"Файл не найден: {filepath}")
                    continue

                plot_item = self.data_manager.add_plot(
                    filepath,
                    p_dict.get("color", "#000000"),
                    p_dict.get("line_width", 1.5),
                )
                if not plot_item:
                    continue

                plot_item.label = p_dict.get("label", plot_item.label)
                plot_item.linestyle = p_dict.get("linestyle", "-")
                plot_item.show_in_legend = p_dict.get("show_in_legend", True)
                plot_item.x_offset = p_dict.get("x_offset", 0.0)
                plot_item.y_offset = p_dict.get("y_offset", 0.0)
                plot_item.visible = p_dict.get("visible", True)

                plot_item.y_mode = p_dict.get("y_mode", "Абсолютный")
                plot_item.convert_sec_to_min = p_dict.get("convert_sec_to_min", False)
                plot_item.reverse_x = p_dict.get("reverse_x", False)

                if "x_min" in p_dict:
                    plot_item.x_min = p_dict["x_min"]
                if "x_max" in p_dict:
                    plot_item.x_max = p_dict["x_max"]
                if "y_min" in p_dict:
                    plot_item.y_min = p_dict["y_min"]
                if "y_max" in p_dict:
                    plot_item.y_max = p_dict["y_max"]

                for m_dict in p_dict.get("markers", []):
                    ax = m_dict.get("anchor_x", 0.0)
                    ay = m_dict.get("anchor_y", 0.0)

                    if "label_x" in m_dict and "offset_x" not in m_dict:
                        ox = m_dict["label_x"] - ax
                    else:
                        ox = m_dict.get("offset_x", 0.0)

                    if "label_y" in m_dict and "offset_y" not in m_dict:
                        oy = m_dict["label_y"] - ay
                    else:
                        oy = m_dict.get("offset_y", 0.0)

                    m = PlotMarker(
                        anchor_x=ax,
                        anchor_y=ay,
                        offset_x=ox,
                        offset_y=oy,
                    )
                    for k, v in m_dict.items():
                        if hasattr(m, k) and k not in ["id", "label_x", "label_y"]:
                            setattr(m, k, v)
                    plot_item.markers.append(m)

            self.data_manager.recalculate_time_data(reset_bounds=False)
            self.refresh_ui()
            self.request_refresh(force=True)

        except Exception as e:
            print(f"Ошибка импорта настроек: {e}")

    # --- Обработчики стилей ---
    def update_style(self, key: str, val: any):
        setattr(self.data_manager.config, key, val)
        self.request_refresh()

    def on_apply_figure_size(self, w: float, h: float, custom: bool = False):
        try:
            w, h = float(w), float(h)
            self.data_manager.config.fig_width = w
            self.data_manager.config.fig_height = h
            self.plotter.resize_figure(w, h)

            w_px, h_px = int(w * self.plotter.fig.dpi), int(h * self.plotter.fig.dpi)
            self.main_window.geometry(f"{w_px}x{h_px}")

            if custom:
                self.control_panel.tab_style.preset_cb.set("Свой размер")
            self.request_refresh(force=True)
        except ValueError:
            pass

    def on_reset_style(self):
        self.data_manager.config = StyleConfig()
        self.control_panel.tab_labels.set_values(self.data_manager.config)
        self.control_panel.tab_style.set_values(self.data_manager.config)
        self.control_panel.tab_style.preset_cb.set("По умолчанию (10x6)")
        self.on_apply_figure_size(10.0, 6.0)
        self.request_refresh(force=True)

    # --- Обработчики вспомогательных линий ---
    def _get_steps(self):
        xlim, ylim = self.plotter.ax.get_xlim(), self.plotter.ax.get_ylim()
        return (
            abs(xlim[1] - xlim[0]) / 100.0 or 0.1,
            abs(ylim[1] - ylim[0]) / 100.0 or 0.1,
        )

    def on_add_marker(self, idx: int):
        xlim, ylim = self.plotter.ax.get_xlim(), self.plotter.ax.get_ylim()

        anchor_x = round(np.mean(xlim), 2)
        anchor_y = round(np.mean(ylim), 2)
        offset_x = 0.0
        offset_y = round(abs(ylim[1] - ylim[0]) * 0.05, 2)

        self.data_manager.add_marker(idx, anchor_x, anchor_y, offset_x, offset_y)
        self.refresh_ui()
        self.request_refresh(force=True)

    def update_marker(self, plot_idx: int, marker_idx: int, key: str, val: any):
        try:
            if key in [
                "anchor_x",
                "anchor_y",
                "offset_x",
                "offset_y",
                "label_rotation",
                "width",
            ]:
                val = float(str(val).replace(",", "."))
            elif key == "font_size":
                val = int(float(str(val).replace(",", ".")))
            setattr(self.data_manager.plots[plot_idx].markers[marker_idx], key, val)
            self.request_refresh()
        except ValueError:
            pass

    def on_remove_marker(self, plot_idx: int, marker_idx: int):
        self.data_manager.remove_marker(plot_idx, marker_idx)
        self.refresh_ui()
        self.request_refresh(force=True)

    def on_auto_marker_pos(self, plot_idx: int, marker_idx: int):
        p = self.data_manager.plots[plot_idx]
        m = p.markers[marker_idx]

        if len(p.t) == 0 or p.id not in self.plotter.plot_lines:
            return

        x_data = self.plotter.plot_lines[p.id].get_xdata()
        y_data = self.plotter.plot_lines[p.id].get_ydata()
        
        if len(x_data) == 0:
            return

        idx_closest = np.argmin(np.abs(x_data - m.anchor_x))

        # Оставляем anchor_x без изменений, меняем только anchor_y
        m.anchor_y = round(float(y_data[idx_closest]), 3)

        lim = self.plotter.ax.get_ylim()
        padding = abs(lim[1] - lim[0]) * 0.02

        m.offset_x = 0.0
        m.offset_y = round(padding, 3)

        self.refresh_ui()
        self.request_refresh(force=True)

    def on_auto_marker_pos_all(self, plot_idx: int):
        p = self.data_manager.plots[plot_idx]

        if len(p.t) == 0 or p.id not in self.plotter.plot_lines:
            return

        x_data = self.plotter.plot_lines[p.id].get_xdata()
        y_data = self.plotter.plot_lines[p.id].get_ydata()
        
        if len(x_data) == 0:
            return
            
        lim_y = self.plotter.ax.get_ylim()
        padding = abs(lim_y[1] - lim_y[0]) * 0.02

        for m in p.markers:
            idx_closest = np.argmin(np.abs(x_data - m.anchor_x))
            
            # Оставляем anchor_x без изменений, меняем только anchor_y
            m.anchor_y = round(float(y_data[idx_closest]), 3)
            m.offset_x = 0.0
            m.offset_y = round(padding, 3)

        self.refresh_ui()
        self.request_refresh(force=True)

    # --- Утилиты ---
    def show_color_picker(self, idx: int, is_marker: bool, marker_idx: int = -1):
        if is_marker:
            current = self.data_manager.plots[idx].markers[marker_idx].color
        else:
            current = self.data_manager.plots[idx].color

        new_c = colorchooser.askcolor(initialcolor=current)[1]
        if new_c:
            if is_marker:
                self.data_manager.plots[idx].markers[marker_idx].color = new_c
            else:
                self.data_manager.plots[idx].color = new_c

            self.refresh_ui()
            self.request_refresh(force=True)

    def on_export_style(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(
                    self.data_manager.config.__dict__, f, indent=4, ensure_ascii=False
                )

    def on_import_style(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for k, v in data.items():
                    if hasattr(self.data_manager.config, k):
                        setattr(self.data_manager.config, k, v)

                self.control_panel.tab_labels.set_values(self.data_manager.config)
                self.control_panel.tab_style.set_values(self.data_manager.config)
                self.on_apply_figure_size(
                    self.data_manager.config.fig_width,
                    self.data_manager.config.fig_height,
                    custom=True,
                )
                self.request_refresh(force=True)
            except Exception as e:
                print(f"Error importing style: {e}")

    def on_save_plot(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".png", filetypes=[("PNG", "*.png"), ("SVG", "*.svg")]
        )
        if path:
            self.plotter.save_figure(path)

    def on_close(self):
        self.main_window.quit()
        self.main_window.destroy()


if __name__ == "__main__":
    app = AppController()
    app.run()

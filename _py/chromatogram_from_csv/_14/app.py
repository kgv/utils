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

        [
            # Красный
            "#d62728",
            "#ff9896",
            "#9c1c1d",
            # Коричневый
            "#8c564b",
            "#c49c94",
            "#5e3a32",
            # Оранжевый
            "#ff7f0e",
            "#ffbb78",
            "#cc660b",
            # Оливковый
            "#bcbd22",
            "#dbdb8d",
            "#8c8d19",
            # Зеленый
            "#2ca02c",
            "#98df8a",
            "#1f7a1f",
            # Бирюзовый
            "#17becf",
            "#9edae5",
            "#118d99",
            # Синий
            "#1f77b4",
            "#aec7e8",
            "#165785",
            # Фиолетовый
            "#9467bd",
            "#c5b0d5",
            "#6b4a8a",
            # Розовый
            "#e377c2",
            "#f7b6d2",
            "#a6578d",
            # Серый
            "#7f7f7f",
            "#c7c7c7",
            "#5c5c5c",
        ]

        # Палитра цветов
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

        y_mode = self.control_panel.tab_scale.mode_var.get()

        # Получаем итоговые границы из всех графиков
        g_x_min, g_x_max, g_y_min, g_y_max = self.data_manager.get_global_limits()

        self.plotter.refresh(
            self.data_manager, g_x_min, g_x_max, y_mode, g_y_min, g_y_max
        )
        self.main_window.redraw_canvas()

    # --- Обработчики событий мыши (Hover и Клик) ---
    def on_mouse_move(self, event):
        if not getattr(self, "ui_ready", False):
            return

        # Если мышь ушла за пределы осей
        if not event.inaxes:
            if self.current_hover_data is not None:
                self.current_hover_data = None
                self.plotter.hover_point.set_visible(False)
                self.plotter.hover_text.set_visible(False)
                self.main_window.redraw_canvas()
            return

        # Обновляем позицию маркера
        result = self.plotter.update_hover(event.x, event.y, event.xdata, event.ydata)

        # Перерисовываем только если точка изменилась (оптимизация производительности)
        if result != self.current_hover_data:
            self.current_hover_data = result
            self.main_window.redraw_canvas()

    def on_mouse_click(self, event):
        # Копируем в буфер обмена при клике левой кнопкой (event.button == 1)
        if event.inaxes and event.button == 1 and self.current_hover_data:
            x, y = self.current_hover_data
            # Формат с табуляцией позволяет вставить данные сразу в две ячейки Excel
            clipboard_text = f"{x}\t{y}".replace(".", ",")

            self.main_window.clipboard_clear()
            self.main_window.clipboard_append(clipboard_text)

            # Визуальный отклик
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

        self.control_panel.tab_scale.update_list(self.data_manager.plots)
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_clear_all(self):
        self.data_manager.clear_all()
        self.plotter.clear()
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, 0.1, 0.1)
        self.control_panel.tab_scale.update_list(self.data_manager.plots)
        self.request_refresh(force=True)

    def update_plot(self, idx: int, key: str, val: any):
        try:
            if key in ["line_width", "x_offset", "y_offset"]:
                val = float(str(val).replace(",", "."))

            old_val = getattr(self.data_manager.plots[idx], key)
            setattr(self.data_manager.plots[idx], key, val)

            if key == "x_offset":
                diff = val - old_val
                self.data_manager.plots[idx].x_min += diff
                self.data_manager.plots[idx].x_max += diff
                self.data_manager.recalculate_time_data()
                self.control_panel.tab_scale.on_plot_selected()
            elif key == "y_offset":
                diff = val - old_val
                self.data_manager.plots[idx].y_min += diff
                self.data_manager.plots[idx].y_max += diff
                self.control_panel.tab_scale.on_plot_selected()

            self.request_refresh()
        except ValueError:
            pass

    def on_move_plot(self, idx: int, direction: int):
        self.data_manager.move_plot(idx, direction)
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_remove_plot(self, idx: int):
        self.data_manager.remove_plot(idx)
        self.control_panel.tab_scale.update_list(self.data_manager.plots)
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_export_file_settings(self):
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON", "*.json")]
        )
        if not path:
            return

        self.data_manager.config.y_mode = self.control_panel.tab_scale.mode_var.get()
        self.data_manager.config.x_min = self.control_panel.tab_scale.scale_min.get()
        self.data_manager.config.x_max = self.control_panel.tab_scale.scale_max.get()
        self.data_manager.config.y_min = self.control_panel.tab_scale.y_min_var.get()
        self.data_manager.config.y_max = self.control_panel.tab_scale.y_max_var.get()

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
                "x_min": p.x_min,
                "x_max": p.x_max,
                "y_min": p.y_min,
                "y_max": p.y_max,
                "visible": p.visible,
                "markers": [m.__dict__ for m in p.markers],
            }
            plots_data.append(plot_dict)

        # Сохраняем и стили, и настройки файлов
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

            # Поддержка нового формата (словарь со стилями и графиками) и старого (только список графиков)
            if isinstance(data, dict):
                style_data = data.get("style_config", {})
                plots_data = data.get("plots", [])

                # Применяем глобальные стили
                for k, v in style_data.items():
                    if hasattr(self.data_manager.config, k):
                        setattr(self.data_manager.config, k, v)

                # Обновляем UI для стилей
                self.control_panel.tab_labels.set_values(self.data_manager.config)
                self.control_panel.tab_style.set_values(self.data_manager.config)
                self.control_panel.tab_scale.convert_sec_to_min_var.set(
                    self.data_manager.config.convert_sec_to_min
                )
                self.control_panel.tab_scale.reverse_x_var.set(
                    self.data_manager.config.reverse_x
                )
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
                plot_item.x_min = p_dict.get("x_min", plot_item.x_min)
                plot_item.x_max = p_dict.get("x_max", plot_item.x_max)
                plot_item.y_min = p_dict.get("y_min", plot_item.y_min)
                plot_item.y_max = p_dict.get("y_max", plot_item.y_max)
                plot_item.visible = p_dict.get("visible", True)

                # Загрузка markers
                for m_dict in p_dict.get("markers", []):
                    ax = m_dict.get("anchor_x", 0.0)
                    ay = m_dict.get("anchor_y", 0.0)

                    # Поддержка старых файлов (пересчет абсолютных координат в смещение)
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

            self.data_manager.recalculate_time_data()
            self.control_panel.tab_scale.update_list(self.data_manager.plots)
            # Поддержка старых файлов (применяем старые глобальные границы ко всем графикам)
            if isinstance(data, dict) and "style_config" in data:
                cfg = data["style_config"]
                if "x_min" in cfg and "x_max" in cfg:
                    for p in self.data_manager.plots:
                        p.x_min = cfg["x_min"]
                        p.x_max = cfg["x_max"]
                        p.y_min = cfg.get("y_min", p.y_min)
                        p.y_max = cfg.get("y_max", p.y_max)
                        
            self.data_manager.recalculate_time_data()
            self.control_panel.tab_scale.update_list(self.data_manager.plots)
            dx, dy = self._get_steps()
            self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
            self.request_refresh(force=True)

        except Exception as e:
            print(f"Ошибка импорта настроек: {e}")

    # --- Обработчики масштаба ---

    def on_x_scale_scroll(self, event=None):
        selection = self.control_panel.tab_scale.target_plot_var.get()
        if not selection: return
        idx = int(selection.split(":")[0])
        p = self.data_manager.plots[idx]
        
        p.x_min = self.control_panel.tab_scale.scale_min.get()
        p.x_max = self.control_panel.tab_scale.scale_max.get()
        
        self.control_panel.tab_scale.ent_min.delete(0, tk.END)
        self.control_panel.tab_scale.ent_min.insert(0, f"{p.x_min:.3f}")
        self.control_panel.tab_scale.ent_max.delete(0, tk.END)
        self.control_panel.tab_scale.ent_max.insert(0, f"{p.x_max:.3f}")
        self.request_refresh()

    def on_x_scale_entry(self):
        selection = self.control_panel.tab_scale.target_plot_var.get()
        if not selection: return
        idx = int(selection.split(":")[0])
        p = self.data_manager.plots[idx]
        
        try:
            v_min = float(self.control_panel.tab_scale.ent_min.get().replace(",", "."))
            v_max = float(self.control_panel.tab_scale.ent_max.get().replace(",", "."))
            p.x_min = v_min
            p.x_max = v_max
            self.control_panel.tab_scale.scale_min.set(v_min)
            self.control_panel.tab_scale.scale_max.set(v_max)
            self.request_refresh(force=True)
        except ValueError:
            self.on_x_scale_scroll()

    def on_manual_y_change(self):
        selection = self.control_panel.tab_scale.target_plot_var.get()
        if not selection: return
        idx = int(selection.split(":")[0])
        p = self.data_manager.plots[idx]
        
        try:
            v_min = float(self.control_panel.tab_scale.ent_y_min.get().replace(",", "."))
            v_max = float(self.control_panel.tab_scale.ent_y_max.get().replace(",", "."))
            p.y_min = v_min
            p.y_max = v_max
            self.control_panel.tab_scale.y_min_var.set(v_min)
            self.control_panel.tab_scale.y_max_var.set(v_max)
            self.request_refresh(force=True)
        except ValueError:
            pass

    def on_fit_y_to_visible(self):
        selection = self.control_panel.tab_scale.target_plot_var.get()
        if not selection: return
        idx = int(selection.split(":")[0])
        p = self.data_manager.plots[idx]
        
        y_mode = self.control_panel.tab_scale.mode_var.get()
        
        mask = (p.t >= p.x_min) & (p.t <= p.x_max)
        if y_mode == "Нормированный":
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

            self.control_panel.tab_scale.y_min_var.set(p.y_min)
            self.control_panel.tab_scale.y_max_var.set(p.y_max)
            self.control_panel.tab_scale.ent_y_min.delete(0, tk.END)
            self.control_panel.tab_scale.ent_y_min.insert(0, f"{p.y_min:.2f}")
            self.control_panel.tab_scale.ent_y_max.delete(0, tk.END)
            self.control_panel.tab_scale.ent_y_max.insert(0, f"{p.y_max:.2f}")

            self.request_refresh(force=True)

    def on_time_unit_change(self):
        is_min = self.control_panel.tab_scale.convert_sec_to_min_var.get()
        self.data_manager.config.convert_sec_to_min = is_min
        
        # Масштабируем границы графиков при смене единиц измерения
        factor = 1/60.0 if is_min else 60.0
        for p in self.data_manager.plots:
            p.x_min = (p.x_min - p.x_offset) * factor + p.x_offset
            p.x_max = (p.x_max - p.x_offset) * factor + p.x_offset
            
        self.data_manager.recalculate_time_data()
        self.control_panel.tab_scale.on_plot_selected()
        self.request_refresh(force=True)

    def on_reverse_x_change(self):
        self.data_manager.config.reverse_x = (
            self.control_panel.tab_scale.reverse_x_var.get()
        )
        self.request_refresh(force=True)

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

    def on_add_marker(self):
        plot_str = self.control_panel.tab_helpers.target_plot_var.get()
        if not plot_str:
            return
        plot_idx = int(plot_str.split(":")[0])

        xlim, ylim = self.plotter.ax.get_xlim(), self.plotter.ax.get_ylim()

        # По умолчанию ставим метку по центру видимой области
        anchor_x = round(np.mean(xlim), 2)
        anchor_y = round(np.mean(ylim), 2)
        offset_x = 0.0
        # Смещение чуть выше точки привязки (на 5% от высоты графика)
        offset_y = round(abs(ylim[1] - ylim[0]) * 0.05, 2)

        self.data_manager.add_marker(plot_idx, anchor_x, anchor_y, offset_x, offset_y)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
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
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_auto_marker_pos(self, plot_idx: int, marker_idx: int):
        p = self.data_manager.plots[plot_idx]
        m = p.markers[marker_idx]

        if len(p.t) == 0 or p.id not in self.plotter.plot_lines:
            return

        y_data = self.plotter.plot_lines[p.id].get_ydata()

        # Ищем ближайшую точку по оси X (времени) к заданному anchor_x
        idx_closest = np.argmin(np.abs(p.t - m.anchor_x))

        m.anchor_x = round(p.t[idx_closest], 3)
        m.anchor_y = round(y_data[idx_closest], 3)

        lim = self.plotter.ax.get_ylim()
        padding = abs(lim[1] - lim[0]) * 0.02

        m.offset_x = 0.0
        m.offset_y = round(padding, 3)

        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_auto_marker_pos_all(self, plot_idx: int):
        p = self.data_manager.plots[plot_idx]

        if len(p.t) == 0 or p.id not in self.plotter.plot_lines:
            return

        y_data = self.plotter.plot_lines[p.id].get_ydata()
        lim_y = self.plotter.ax.get_ylim()
        padding = abs(lim_y[1] - lim_y[0]) * 0.02

        for m in p.markers:
            idx_closest = np.argmin(np.abs(p.t - m.anchor_x))
            m.anchor_x = round(p.t[idx_closest], 3)
            m.anchor_y = round(y_data[idx_closest], 3)
            m.offset_x = 0.0
            m.offset_y = round(padding, 3)

        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
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
                dx, dy = self._get_steps()
                self.control_panel.tab_helpers.update_list(
                    self.data_manager.plots, dx, dy
                )
            else:
                self.data_manager.plots[idx].color = new_c
                self.control_panel.tab_files.update_list(self.data_manager.plots)
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
                self.control_panel.tab_scale.convert_sec_to_min_var.set(
                    self.data_manager.config.convert_sec_to_min
                )
                self.control_panel.tab_scale.reverse_x_var.set(
                    self.data_manager.config.reverse_x
                )
                self.on_apply_figure_size(
                    self.data_manager.config.fig_width,
                    self.data_manager.config.fig_height,
                    custom=True,
                )
                self.data_manager.recalculate_time_data()
                self.control_panel.tab_scale.update_list(self.data_manager.plots)
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

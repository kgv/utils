# app.py
import tkinter as tk
from tkinter import filedialog, colorchooser
import json
import os
import numpy as np

from models import HelperLine, StyleConfig
from data_manager import DataManager
from plotter import ChromatogramPlotter
from ui.main_window import MainWindow
from ui.control_panel import ControlPanel

class AppController:
    def __init__(self):
        self.data_manager = DataManager()
        self.plotter = ChromatogramPlotter()
        
        # Палитра цветов
        self.palette = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # Инициализация UI
        self.main_window = MainWindow(self, self.plotter.get_figure())
        self.control_panel = ControlPanel(self.main_window, self)
        
        # Применяем дефолтные стили к UI
        self.control_panel.tab_labels.set_values(self.data_manager.config)
        self.control_panel.tab_style.set_values(self.data_manager.config)
        
        self.ui_ready = True
        self.request_refresh(force=True)

    def run(self):
        self.main_window.mainloop()

    def request_refresh(self, force: bool = False) -> None:
        if not getattr(self, 'ui_ready', False): return

        # Сбор параметров из UI
        x_min = self.control_panel.tab_scale.scale_min.get()
        x_max = self.control_panel.tab_scale.scale_max.get()
        y_mode = self.control_panel.tab_scale.mode_var.get()
        auto_y = self.control_panel.tab_scale.auto_y_var.get()
        y_min = self.control_panel.tab_scale.y_min_var.get()
        y_max = self.control_panel.tab_scale.y_max_var.get()

        # Отрисовка
        new_y_min, new_y_max = self.plotter.refresh(
            self.data_manager, x_min, x_max, y_mode, auto_y, y_min, y_max
        )

        # Обновление UI (если был автомасштаб Y)
        if auto_y:
            self.control_panel.tab_scale.y_min_var.set(new_y_min)
            self.control_panel.tab_scale.y_max_var.set(new_y_max)
            self.control_panel.tab_scale.ent_y_min.delete(0, tk.END)
            self.control_panel.tab_scale.ent_y_min.insert(0, f"{new_y_min:.2f}")
            self.control_panel.tab_scale.ent_y_max.delete(0, tk.END)
            self.control_panel.tab_scale.ent_y_max.insert(0, f"{new_y_max:.2f}")

        self.main_window.redraw_canvas()

    # --- Обработчики файлов и графиков ---
    def on_add_files(self):
        paths = filedialog.askopenfilenames(filetypes=[("Data", "*.csv *.txt"), ("All", "*.*")])
        if not paths: return
        
        for p in paths:
            color = self.palette[len(self.data_manager.plots) % len(self.palette)]
            self.data_manager.add_plot(p, color, self.data_manager.config.line_width)
            
        self._sync_x_bounds()
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_clear_all(self):
        self.data_manager.clear_all()
        self.plotter.clear()
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, 0.1, 0.1)
        self._sync_x_bounds()
        self.request_refresh(force=True)

    def update_plot(self, idx: int, key: str, val: any):
        try:
            if key in ['line_width', 'x_offset', 'y_offset']: val = float(str(val).replace(',', '.'))
            setattr(self.data_manager.plots[idx], key, val)
            if key == 'x_offset': self.data_manager.recalculate_time_data()
            self.request_refresh()
        except ValueError: pass

    def on_move_plot(self, idx: int, direction: int):
        self.data_manager.move_plot(idx, direction)
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_remove_plot(self, idx: int):
        self.data_manager.remove_plot(idx)
        self._sync_x_bounds()
        self.control_panel.tab_files.update_list(self.data_manager.plots)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_export_file_settings(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if not path: return
        
        export_data = []
        for p in self.data_manager.plots:
            plot_dict = {
                'filepath': p.filepath,
                'color': p.color,
                'label': p.label,
                'linestyle': p.linestyle,
                'line_width': p.line_width,
                'show_in_legend': p.show_in_legend,
                'x_offset': p.x_offset,
                'y_offset': p.y_offset,
                'visible': p.visible,
                'helpers': [h.__dict__ for h in p.helpers]
            }
            export_data.append(plot_dict)
            
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=4, ensure_ascii=False)

    def on_import_file_settings(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if not path: return
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for p_dict in data:
                filepath = p_dict.get('filepath')
                if not filepath or not os.path.exists(filepath):
                    print(f"Файл не найден: {filepath}")
                    continue
                    
                plot_item = self.data_manager.add_plot(filepath, p_dict.get('color', '#000000'), p_dict.get('line_width', 1.5))
                if not plot_item: continue
                
                plot_item.label = p_dict.get('label', plot_item.label)
                plot_item.linestyle = p_dict.get('linestyle', '-')
                plot_item.show_in_legend = p_dict.get('show_in_legend', True)
                plot_item.x_offset = p_dict.get('x_offset', 0.0)
                plot_item.y_offset = p_dict.get('y_offset', 0.0)
                plot_item.visible = p_dict.get('visible', True)
                
                for h_dict in p_dict.get('helpers', []):
                    h = HelperLine(
                        line_type=h_dict['line_type'], 
                        pos=h_dict['pos'], 
                        start=h_dict['start'], 
                        end=h_dict['end'], 
                        label_pos=h_dict['label_pos']
                    )
                    for k, v in h_dict.items():
                        if hasattr(h, k) and k != 'id':
                            setattr(h, k, v)
                    plot_item.helpers.append(h)
                    
            self.data_manager.recalculate_time_data()
            self._sync_x_bounds()
            self.control_panel.tab_files.update_list(self.data_manager.plots)
            dx, dy = self._get_steps()
            self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
            self.request_refresh(force=True)
            
        except Exception as e:
            print(f"Ошибка импорта настроек файлов: {e}")

    # --- Обработчики масштаба ---
    def _sync_x_bounds(self):
        b_min, b_max = self.data_manager.all_data_bounds
        if b_min == float('inf'): b_min, b_max = 0, 1
        self.control_panel.tab_scale.update_x_bounds(b_min, b_max)
        
        # Если текущие значения выходят за рамки, корректируем
        if self.control_panel.tab_scale.scale_min.get() < b_min: self.control_panel.tab_scale.scale_min.set(b_min)
        if self.control_panel.tab_scale.scale_max.get() > b_max: self.control_panel.tab_scale.scale_max.set(b_max)
        self.on_x_scale_scroll()

    def on_x_scale_scroll(self, event=None):
        s_min = self.control_panel.tab_scale.scale_min.get()
        s_max = self.control_panel.tab_scale.scale_max.get()
        self.control_panel.tab_scale.ent_min.delete(0, tk.END); self.control_panel.tab_scale.ent_min.insert(0, f"{s_min:.3f}")
        self.control_panel.tab_scale.ent_max.delete(0, tk.END); self.control_panel.tab_scale.ent_max.insert(0, f"{s_max:.3f}")
        self.request_refresh()

    def on_x_scale_entry(self):
        try:
            v_min = float(self.control_panel.tab_scale.ent_min.get().replace(',', '.'))
            v_max = float(self.control_panel.tab_scale.ent_max.get().replace(',', '.'))
            self.control_panel.tab_scale.scale_min.set(v_min)
            self.control_panel.tab_scale.scale_max.set(v_max)
            self.request_refresh(force=True)
        except ValueError: self.on_x_scale_scroll()

    def on_manual_y_change(self):
        try:
            v_min = float(self.control_panel.tab_scale.ent_y_min.get().replace(',', '.'))
            v_max = float(self.control_panel.tab_scale.ent_y_max.get().replace(',', '.'))
            self.control_panel.tab_scale.y_min_var.set(v_min)
            self.control_panel.tab_scale.y_max_var.set(v_max)
            self.control_panel.tab_scale.auto_y_var.set(False)
            self.request_refresh(force=True)
        except ValueError: pass

    def on_fit_y_to_visible(self):
        if self.control_panel.tab_scale.mode_var.get() == "Абсолютный":
            s = self.control_panel.tab_scale.scale_min.get()
            e = self.control_panel.tab_scale.scale_max.get()
            m_min, m_max = float('inf'), float('-inf')
            
            for item in self.data_manager.plots:
                if not item.visible: continue
                mask = (item.t >= s) & (item.t <= e)
                v = item.y_orig[mask] + item.y_offset
                if v.size:
                    m_min, m_max = min(m_min, v.min()), max(m_max, v.max())
                    
            if m_max != float('-inf'):
                yr = m_max - m_min if m_max > m_min else (m_max if m_max > 0 else 1)
                self.control_panel.tab_scale.y_min_var.set(m_min - yr * 0.02)
                self.control_panel.tab_scale.y_max_var.set(m_max + yr * 0.05)
                self.control_panel.tab_scale.auto_y_var.set(False)
                self.request_refresh(force=True)

    def on_time_unit_change(self):
        self.data_manager.config.convert_sec_to_min = self.control_panel.tab_scale.convert_sec_to_min_var.get()
        self.data_manager.recalculate_time_data()
        self._sync_x_bounds()
        self.request_refresh(force=True)

    def on_global_x_offset_change(self):
        try:
            val = float(self.control_panel.tab_scale.offset_entry.get().replace(',', '.'))
            self.data_manager.config.time_offset = val
            self.data_manager.recalculate_time_data()
            self._sync_x_bounds()
            self.request_refresh(force=True)
        except ValueError: pass

    def on_reverse_x_change(self):
        self.data_manager.config.reverse_x = self.control_panel.tab_scale.reverse_x_var.get()
        self.request_refresh(force=True)

    # --- Обработчики стилей ---
    def update_style(self, key: str, val: any):
        setattr(self.data_manager.config, key, val)
        if key == 'line_width':
            for item in self.data_manager.plots: item.line_width = val
            self.control_panel.tab_files.update_list(self.data_manager.plots)
        self.request_refresh()

    def on_apply_figure_size(self, w: float, h: float, custom: bool = False):
        try:
            w, h = float(w), float(h)
            self.data_manager.config.fig_width = w
            self.data_manager.config.fig_height = h
            self.plotter.resize_figure(w, h)
            
            w_px, h_px = int(w * self.plotter.fig.dpi), int(h * self.plotter.fig.dpi)
            self.main_window.geometry(f"{w_px}x{h_px}")
            
            if custom: self.control_panel.tab_style.preset_cb.set("Свой размер")
            self.request_refresh(force=True)
        except ValueError: pass

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
        return abs(xlim[1] - xlim[0]) / 100.0 or 0.1, abs(ylim[1] - ylim[0]) / 100.0 or 0.1

    def on_add_helper(self):
        plot_str = self.control_panel.tab_helpers.target_plot_var.get()
        if not plot_str: return
        plot_idx = int(plot_str.split(':')[0])
        line_type = self.control_panel.tab_helpers.h_type.get()
        
        xlim, ylim = self.plotter.ax.get_xlim(), self.plotter.ax.get_ylim()
        is_v = line_type == 'V'
        pos = round(np.mean(xlim if is_v else ylim), 2)
        start = round(ylim[0] if is_v else xlim[0], 2)
        end = round(ylim[1] if is_v else xlim[1], 2)
        
        self.data_manager.add_helper_line(plot_idx, line_type, pos, start, end)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def update_helper(self, plot_idx: int, helper_idx: int, key: str, val: any):
        try:
            if key in ['pos', 'start', 'end', 'label_offset', 'label_rotation', 'label_pos', 'width']:
                val = float(str(val).replace(',', '.'))
            elif key == 'font_size':
                val = int(float(str(val).replace(',', '.')))
            setattr(self.data_manager.plots[plot_idx].helpers[helper_idx], key, val)
            self.request_refresh()
        except ValueError: pass

    def on_remove_helper(self, plot_idx: int, helper_idx: int):
        self.data_manager.remove_helper_line(plot_idx, helper_idx)
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    def on_auto_label_pos(self, plot_idx: int, helper_idx: int):
        p = self.data_manager.plots[plot_idx]
        h = p.helpers[helper_idx]
        
        if len(p.t) == 0: 
            return
            
        y_data = self.plotter.plot_lines[p.id].get_ydata()
        
        if h.line_type == 'V':
            # Ищем ближайшую точку по оси X (времени)
            idx_closest = np.argmin(np.abs(p.t - h.pos))
            val = y_data[idx_closest]
            lim = self.plotter.ax.get_ylim()
        else:
            # Ищем ближайшую точку по оси Y (интенсивности)
            idx_closest = np.argmin(np.abs(y_data - h.pos))
            val = p.t[idx_closest]
            lim = self.plotter.ax.get_xlim()
            
        # Добавляем небольшой отступ (2% от видимого диапазона оси)
        padding = abs(lim[1] - lim[0]) * 0.02
        h.label_pos = round(val + padding, 2)
        
        dx, dy = self._get_steps()
        self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
        self.request_refresh(force=True)

    # --- Утилиты ---
    def show_color_picker(self, idx: int, is_helper: bool, helper_idx: int = -1):
        if is_helper:
            current = self.data_manager.plots[idx].helpers[helper_idx].color
        else:
            current = self.data_manager.plots[idx].color
            
        new_c = colorchooser.askcolor(initialcolor=current)[1]
        if new_c:
            if is_helper:
                self.data_manager.plots[idx].helpers[helper_idx].color = new_c
                dx, dy = self._get_steps()
                self.control_panel.tab_helpers.update_list(self.data_manager.plots, dx, dy)
            else:
                self.data_manager.plots[idx].color = new_c
                self.control_panel.tab_files.update_list(self.data_manager.plots)
            self.request_refresh(force=True)

    def on_export_style(self):
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.data_manager.config.__dict__, f, indent=4, ensure_ascii=False)

    def on_import_style(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
                for k, v in data.items():
                    if hasattr(self.data_manager.config, k): setattr(self.data_manager.config, k, v)
                
                self.control_panel.tab_labels.set_values(self.data_manager.config)
                self.control_panel.tab_style.set_values(self.data_manager.config)
                self.control_panel.tab_scale.convert_sec_to_min_var.set(self.data_manager.config.convert_sec_to_min)
                self.control_panel.tab_scale.reverse_x_var.set(self.data_manager.config.reverse_x)
                self.control_panel.tab_scale.time_offset_var.set(self.data_manager.config.time_offset)
                
                self.on_apply_figure_size(self.data_manager.config.fig_width, self.data_manager.config.fig_height, custom=True)
                self.data_manager.recalculate_time_data()
                self._sync_x_bounds()
                self.request_refresh(force=True)
            except Exception as e: print(f"Error importing style: {e}")

    def on_save_plot(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png"), ("SVG", "*.svg")])
        if path: self.plotter.save_figure(path)

    def on_close(self):
        self.main_window.quit()
        self.main_window.destroy()

if __name__ == "__main__":
    app = AppController()
    app.run()
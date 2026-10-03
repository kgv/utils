# ui/tab_scale.py
import tkinter as tk
from tkinter import ttk
from typing import List
import numpy as np
from models import PlotItem

class TabScale(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.plots: List[PlotItem] = []
        
        self.target_plot_var = tk.StringVar(self)
        self.mode_var = tk.StringVar(self, value="Абсолютный")
        self.convert_sec_to_min_var = tk.BooleanVar(self, value=False)
        self.reverse_x_var = tk.BooleanVar(self, value=False)
        self.y_min_var = tk.DoubleVar(self, value=0.0)
        self.y_max_var = tk.DoubleVar(self, value=100.0)
        
        self.setup_ui()

    def setup_ui(self) -> None:
        # Выбор файла
        f_top = ttk.Frame(self, padding=(20, 20, 20, 5))
        f_top.pack(fill="x")
        ttk.Label(f_top, text="Файл:").pack(side="left", padx=(0, 5))
        self.plot_cb = ttk.Combobox(f_top, textvariable=self.target_plot_var, state="readonly", width=40)
        self.plot_cb.pack(side="left")
        self.plot_cb.bind("<<ComboboxSelected>>", lambda e: self.render_settings())

        self.settings_frame = ttk.Frame(self, padding=(20, 5, 20, 20))
        self.settings_frame.pack(fill="both", expand=True)
        
        ttk.Label(self.settings_frame, text="Режим:", font='Arial 10 bold').pack(anchor="w")
        ttk.Radiobutton(self.settings_frame, text="Абсолютный", variable=self.mode_var, value="Абсолютный", 
                        command=self.on_mode_change).pack(anchor="w")
        ttk.Radiobutton(self.settings_frame, text="Нормированный", variable=self.mode_var, value="Нормированный", 
                        command=self.on_mode_change).pack(anchor="w")
        
        ttk.Checkbutton(self.settings_frame, text="Переводить время (X) из секунд в минуты", 
                        variable=self.convert_sec_to_min_var, 
                        command=self.on_time_unit_change).pack(anchor="w", pady=(10, 0))

        ttk.Checkbutton(self.settings_frame, text="Инвертировать данные по оси X (справа налево)", 
                        variable=self.reverse_x_var, 
                        command=self.on_reverse_x_change).pack(anchor="w", pady=(5, 0))
        
        # Настройки оси X
        ttk.Label(self.settings_frame, text="Ось X (Время):", font='Arial 10 bold').pack(anchor="w", pady=(10, 5))
        
        f_min = ttk.Frame(self.settings_frame); f_min.pack(fill="x")
        self.scale_min = ttk.Scale(f_min, from_=0, to=1, orient="horizontal", command=self.on_x_scale_scroll)
        self.scale_min.pack(side="left", fill="x", expand=True)
        self.ent_min = ttk.Entry(f_min, width=10)
        self.ent_min.pack(side="right", padx=5)
        self.ent_min.bind("<Return>", lambda e: [self.on_x_scale_entry(), self.focus_set()])
        
        f_max = ttk.Frame(self.settings_frame); f_max.pack(fill="x")
        self.scale_max = ttk.Scale(f_max, from_=0, to=1, orient="horizontal", command=self.on_x_scale_scroll)
        self.scale_max.pack(side="left", fill="x", expand=True)
        self.ent_max = ttk.Entry(f_max, width=10)
        self.ent_max.pack(side="right", padx=5)
        self.ent_max.bind("<Return>", lambda e: [self.on_x_scale_entry(), self.focus_set()])
            
        # Настройки оси Y
        ttk.Separator(self.settings_frame, orient="horizontal").pack(fill="x", pady=15)
        ttk.Label(self.settings_frame, text="Ось Y (Интенсивность):", font='Arial 10 bold').pack(anchor="w")
        
        y_frame = ttk.Frame(self.settings_frame)
        y_frame.pack(fill="x")
        ttk.Label(y_frame, text="Min Y:").pack(side="left")
        self.ent_y_min = ttk.Entry(y_frame, width=12, textvariable=self.y_min_var)
        self.ent_y_min.pack(side="left", padx=5)
        self.ent_y_min.bind("<Return>", lambda e: [self.on_manual_y_change(), self.focus_set()])
        self.ent_y_min.bind("<FocusOut>", lambda e: self.on_manual_y_change())
        
        ttk.Label(y_frame, text="Max Y:").pack(side="left", padx=(10, 0))
        self.ent_y_max = ttk.Entry(y_frame, width=12, textvariable=self.y_max_var)
        self.ent_y_max.pack(side="left", padx=5)
        self.ent_y_max.bind("<Return>", lambda e: [self.on_manual_y_change(), self.focus_set()])
        self.ent_y_max.bind("<FocusOut>", lambda e: self.on_manual_y_change())

        ttk.Button(self.settings_frame, text="🔍 Подогнать Y по видимому X", 
                   command=self.on_fit_y_to_visible).pack(fill="x", pady=15)

        self.set_ui_state("disabled")

    def set_ui_state(self, state: str):
        for child in self.settings_frame.winfo_children():
            try:
                child.configure(state=state)
            except tk.TclError:
                pass
            if isinstance(child, ttk.Frame):
                for subchild in child.winfo_children():
                    try:
                        subchild.configure(state=state)
                    except tk.TclError:
                        pass

    def update_list(self, plots: List[PlotItem]) -> None:
        self.plots = plots
        current_selection = self.target_plot_var.get()
        plot_names = [f"{i}: {p.label}" for i, p in enumerate(plots)]
        self.plot_cb["values"] = plot_names

        if current_selection in plot_names:
            self.plot_cb.set(current_selection)
        elif plot_names:
            self.plot_cb.set(plot_names[0])
        else:
            self.plot_cb.set("")

        self.render_settings()

    def get_selected_plot(self) -> PlotItem:
        selection = self.target_plot_var.get()
        if not selection or not self.plots: return None
        idx = int(selection.split(":")[0])
        if 0 <= idx < len(self.plots):
            return self.plots[idx]
        return None

    def render_settings(self):
        p = self.get_selected_plot()
        if not p:
            self.set_ui_state("disabled")
            return
        
        self.set_ui_state("normal")
        
        self.mode_var.set(p.y_mode)
        self.convert_sec_to_min_var.set(p.convert_sec_to_min)
        self.reverse_x_var.set(p.reverse_x)
        
        if len(p.t) > 0:
            t_min, t_max = float(p.t.min()), float(p.t.max())
        else:
            t_min, t_max = 0.0, 1.0
            
        self.scale_min.config(from_=t_min, to=t_max)
        self.scale_max.config(from_=t_min, to=t_max)
        
        self.scale_min.set(p.x_min)
        self.scale_max.set(p.x_max)
        
        self.ent_min.delete(0, tk.END)
        self.ent_min.insert(0, f"{p.x_min:.3f}")
        self.ent_max.delete(0, tk.END)
        self.ent_max.insert(0, f"{p.x_max:.3f}")
        
        self.y_min_var.set(p.y_min)
        self.y_max_var.set(p.y_max)
        self.ent_y_min.delete(0, tk.END)
        self.ent_y_min.insert(0, f"{p.y_min:.2f}")
        self.ent_y_max.delete(0, tk.END)
        self.ent_y_max.insert(0, f"{p.y_max:.2f}")

    def on_mode_change(self):
        p = self.get_selected_plot()
        if p:
            p.y_mode = self.mode_var.get()
            self.controller.request_refresh()

    def on_time_unit_change(self):
        p = self.get_selected_plot()
        if p:
            p.convert_sec_to_min = self.convert_sec_to_min_var.get()
            self.controller.data_manager.recalculate_time_data(reset_bounds=True)
            self.render_settings()
            self.controller.request_refresh(force=True)

    def on_reverse_x_change(self):
        p = self.get_selected_plot()
        if p:
            p.reverse_x = self.reverse_x_var.get()
            self.controller.data_manager.recalculate_time_data(reset_bounds=True)
            self.render_settings()
            self.controller.request_refresh(force=True)

    def on_x_scale_scroll(self, event=None):
        p = self.get_selected_plot()
        if p:
            p.x_min = self.scale_min.get()
            p.x_max = self.scale_max.get()
            self.ent_min.delete(0, tk.END)
            self.ent_min.insert(0, f"{p.x_min:.3f}")
            self.ent_max.delete(0, tk.END)
            self.ent_max.insert(0, f"{p.x_max:.3f}")
            self.controller.request_refresh()

    def on_x_scale_entry(self):
        p = self.get_selected_plot()
        if p:
            try:
                v_min = float(self.ent_min.get().replace(",", "."))
                v_max = float(self.ent_max.get().replace(",", "."))
                p.x_min = v_min
                p.x_max = v_max
                self.scale_min.set(v_min)
                self.scale_max.set(v_max)
                self.controller.request_refresh(force=True)
            except ValueError:
                self.render_settings()

    def on_manual_y_change(self, event=None):
        p = self.get_selected_plot()
        if p:
            try:
                v_min = float(self.ent_y_min.get().replace(",", "."))
                v_max = float(self.ent_y_max.get().replace(",", "."))
                p.y_min = v_min
                p.y_max = v_max
                self.y_min_var.set(v_min)
                self.y_max_var.set(v_max)
                self.controller.request_refresh(force=True)
            except ValueError:
                self.render_settings()

    def on_fit_y_to_visible(self):
        p = self.get_selected_plot()
        if not p or not p.visible:
            return
            
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
            self.render_settings()
            self.controller.request_refresh(force=True)
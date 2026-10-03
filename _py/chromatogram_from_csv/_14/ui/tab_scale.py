# ui/tab_scale.py
import tkinter as tk
from tkinter import ttk
from typing import List
from models import PlotItem

class TabScale(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.plots: List[PlotItem] = []
        
        self.mode_var = tk.StringVar(self, value="Абсолютный")
        self.convert_sec_to_min_var = tk.BooleanVar(self, value=False)
        self.reverse_x_var = tk.BooleanVar(self, value=False)
        
        self.target_plot_var = tk.StringVar(self)
        self.y_min_var = tk.DoubleVar(self, value=0.0)
        self.y_max_var = tk.DoubleVar(self, value=100.0)
        
        self.setup_ui()

    def setup_ui(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both")
        
        # --- Глобальные настройки ---
        ttk.Label(frame, text="Глобальные настройки:", font='Arial 10 bold').pack(anchor="w", pady=(0, 5))
        
        f_mode = ttk.Frame(frame)
        f_mode.pack(fill="x", anchor="w")
        ttk.Label(f_mode, text="Режим Y:").pack(side="left", padx=(0, 10))
        ttk.Radiobutton(f_mode, text="Абсолютный", variable=self.mode_var, value="Абсолютный", 
                        command=self.controller.request_refresh).pack(side="left")
        ttk.Radiobutton(f_mode, text="Нормированный", variable=self.mode_var, value="Нормированный", 
                        command=self.controller.request_refresh).pack(side="left", padx=10)
        
        ttk.Checkbutton(frame, text="Переводить время (X) из секунд в минуты", 
                        variable=self.convert_sec_to_min_var, 
                        command=self.controller.on_time_unit_change).pack(anchor="w", pady=(10, 0))

        ttk.Checkbutton(frame, text="Инвертировать ось X (справа налево)", 
                        variable=self.reverse_x_var, 
                        command=self.controller.on_reverse_x_change).pack(anchor="w", pady=(5, 0))
        
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)
        
        # --- Индивидуальные настройки ---
        ttk.Label(frame, text="Индивидуальные настройки масштаба:", font='Arial 10 bold').pack(anchor="w", pady=(0, 10))
        
        f_sel = ttk.Frame(frame)
        f_sel.pack(fill="x", pady=5)
        ttk.Label(f_sel, text="График:").pack(side="left")
        self.plot_cb = ttk.Combobox(f_sel, textvariable=self.target_plot_var, state="readonly", width=30)
        self.plot_cb.pack(side="left", padx=5)
        self.plot_cb.bind("<<ComboboxSelected>>", lambda e: self.on_plot_selected())
        
        self.color_indicator = tk.Label(f_sel, width=3, relief="solid", borderwidth=1, bg="#d9d9d9")
        self.color_indicator.pack(side="left", padx=5)
        
        # Настройки оси X
        ttk.Label(frame, text="Ось X (Время):").pack(anchor="w", pady=(10, 5))
        
        f_min = ttk.Frame(frame); f_min.pack(fill="x")
        self.scale_min = ttk.Scale(f_min, from_=0, to=1, orient="horizontal", command=self.controller.on_x_scale_scroll)
        self.scale_min.pack(side="left", fill="x", expand=True)
        self.ent_min = ttk.Entry(f_min, width=10)
        self.ent_min.pack(side="right", padx=5)
        self.ent_min.bind("<Return>", lambda e: [self.controller.on_x_scale_entry(), self.focus_set()])
        
        f_max = ttk.Frame(frame); f_max.pack(fill="x")
        self.scale_max = ttk.Scale(f_max, from_=0, to=1, orient="horizontal", command=self.controller.on_x_scale_scroll)
        self.scale_max.pack(side="left", fill="x", expand=True)
        self.ent_max = ttk.Entry(f_max, width=10)
        self.ent_max.pack(side="right", padx=5)
        self.ent_max.bind("<Return>", lambda e: [self.controller.on_x_scale_entry(), self.focus_set()])
            
        # Настройки оси Y
        ttk.Label(frame, text="Ось Y (Интенсивность):").pack(anchor="w", pady=(15, 5))
        
        y_frame = ttk.Frame(frame)
        y_frame.pack(fill="x")
        ttk.Label(y_frame, text="Min Y:").pack(side="left")
        self.ent_y_min = ttk.Entry(y_frame, width=12, textvariable=self.y_min_var)
        self.ent_y_min.pack(side="left", padx=5)
        self.ent_y_min.bind("<Return>", lambda e: [self.controller.on_manual_y_change(), self.focus_set()])
        self.ent_y_min.bind("<FocusOut>", lambda e: self.controller.on_manual_y_change())
        
        ttk.Label(y_frame, text="Max Y:").pack(side="left", padx=(10, 0))
        self.ent_y_max = ttk.Entry(y_frame, width=12, textvariable=self.y_max_var)
        self.ent_y_max.pack(side="left", padx=5)
        self.ent_y_max.bind("<Return>", lambda e: [self.controller.on_manual_y_change(), self.focus_set()])
        self.ent_y_max.bind("<FocusOut>", lambda e: self.controller.on_manual_y_change())

        self.btn_fit = ttk.Button(frame, text="🔍 Подогнать Y по видимому X", 
                   command=self.controller.on_fit_y_to_visible)
        self.btn_fit.pack(fill="x", pady=15)

    def update_list(self, plots: List[PlotItem]) -> None:
        self.plots = plots
        current = self.target_plot_var.get()
        plot_names = [f"{i}: {p.label}" for i, p in enumerate(plots)]
        self.plot_cb["values"] = plot_names
        
        if current in plot_names:
            self.plot_cb.set(current)
        elif plot_names:
            self.plot_cb.set(plot_names[0])
        else:
            self.plot_cb.set("")
            
        self.on_plot_selected()

    def on_plot_selected(self) -> None:
        selection = self.target_plot_var.get()
        if not selection or not self.plots:
            self.color_indicator.config(bg="#d9d9d9")
            self.scale_min.config(state="disabled")
            self.scale_max.config(state="disabled")
            self.btn_fit.config(state="disabled")
            return
            
        self.scale_min.config(state="normal")
        self.scale_max.config(state="normal")
        self.btn_fit.config(state="normal")
        
        idx = int(selection.split(":")[0])
        if idx >= len(self.plots): return
        p = self.plots[idx]
        
        self.color_indicator.config(bg=p.color)
        
        # Обновляем границы ползунков по фактическим данным графика
        t_min = p.t.min() if len(p.t) else 0.0
        t_max = p.t.max() if len(p.t) else 1.0
        if t_min == t_max: t_max += 1.0
        
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
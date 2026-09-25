# ui/tab_scale.py
import tkinter as tk
from tkinter import ttk

class TabScale(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Переменные состояния UI
        self.mode_var = tk.StringVar(self, value="Абсолютный")
        self.convert_sec_to_min_var = tk.BooleanVar(self, value=False)
        self.reverse_x_var = tk.BooleanVar(self, value=False)
        
        self.y_min_var = tk.DoubleVar(self, value=0.0)
        self.y_max_var = tk.DoubleVar(self, value=100.0)
        
        self.setup_ui()

    def setup_ui(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both")
        
        ttk.Label(frame, text="Режим:", font='Arial 10 bold').pack(anchor="w")
        ttk.Radiobutton(frame, text="Абсолютный", variable=self.mode_var, value="Абсолютный", 
                        command=self.controller.request_refresh).pack(anchor="w")
        ttk.Radiobutton(frame, text="Нормированный", variable=self.mode_var, value="Нормированный", 
                        command=self.controller.request_refresh).pack(anchor="w")
        
        ttk.Checkbutton(frame, text="Переводить время (X) из секунд в минуты", 
                        variable=self.convert_sec_to_min_var, 
                        command=self.controller.on_time_unit_change).pack(anchor="w", pady=(10, 0))

        ttk.Checkbutton(frame, text="Инвертировать ось X (справа налево)", 
                        variable=self.reverse_x_var, 
                        command=self.controller.on_reverse_x_change).pack(anchor="w", pady=(5, 0))
        
        # Настройки оси X
        ttk.Label(frame, text="Ось X (Время):", font='Arial 10 bold').pack(anchor="w", pady=(10, 5))
        
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
        ttk.Separator(frame, orient="horizontal").pack(fill="x", pady=15)
        ttk.Label(frame, text="Ось Y (Интенсивность):", font='Arial 10 bold').pack(anchor="w")
        
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

        ttk.Button(frame, text="🔍 Подогнать Y по видимому X", 
                   command=self.controller.on_fit_y_to_visible).pack(fill="x", pady=15)

    def update_x_bounds(self, min_val: float, max_val: float) -> None:
        """Обновляет границы ползунков оси X."""
        self.scale_min.config(from_=min_val, to=max_val)
        self.scale_max.config(from_=min_val, to=max_val)
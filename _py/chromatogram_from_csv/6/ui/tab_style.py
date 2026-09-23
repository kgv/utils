# ui/tab_style.py
import tkinter as tk
from tkinter import ttk

class TabStyle(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.font_vars = {}
        self.style_widgets = {}
        
        self.fig_w_var = tk.DoubleVar(value=10.0)
        self.fig_h_var = tk.DoubleVar(value=6.0)
        
        self.setup_ui()

    def setup_ui(self) -> None:
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)
        
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        f = ttk.Frame(scroll_frame, padding=20)
        f.pack(fill="both")
        f.columnconfigure(1, weight=1)
        
        io_frame = ttk.Frame(f)
        io_frame.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,15))
        ttk.Button(io_frame, text="💾 Экспорт стиля", command=self.controller.on_export_style).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(io_frame, text="📂 Импорт стиля", command=self.controller.on_import_style).pack(side="left", expand=True, fill="x", padx=2)

        # Размер графика
        size_frame = ttk.LabelFrame(f, text="Размер графика (дюймы, 1 дюйм = 100 пикселей)", padding=10)
        size_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 15))
        
        ttk.Label(size_frame, text="Ширина:").pack(side="left", padx=(0, 5))
        ent_w = ttk.Entry(size_frame, textvariable=self.fig_w_var, width=6)
        ent_w.pack(side="left")
        ent_w.bind("<Return>", lambda e: self.controller.on_apply_figure_size(self.fig_w_var.get(), self.fig_h_var.get(), custom=True))
        
        ttk.Label(size_frame, text="Высота:").pack(side="left", padx=(15, 5))
        ent_h = ttk.Entry(size_frame, textvariable=self.fig_h_var, width=6)
        ent_h.pack(side="left")
        ent_h.bind("<Return>", lambda e: self.controller.on_apply_figure_size(self.fig_w_var.get(), self.fig_h_var.get(), custom=True))
        
        ttk.Label(size_frame, text="Пресеты:").pack(side="left", padx=(20, 5))
        self.preset_cb = ttk.Combobox(size_frame, values=[
            "По умолчанию (10x6)", "HD (12.8x7.2)", "FullHD (19.2x10.8)", 
            "4K (38.4x21.6)", "A4 Альбомная (11.7x8.3)", "Квадрат (10x10)", "Свой размер"
        ], state="readonly", width=22)
        self.preset_cb.set("По умолчанию (10x6)")
        self.preset_cb.pack(side="left")
        self.preset_cb.bind("<<ComboboxSelected>>", self.on_preset_selected)

        # Шрифты
        self.create_font_row(f, "Общий шрифт", "gen", 2, include_inherit=False)
        self.create_font_row(f, "Заголовок", "title", 5, size_range=(8, 30))
        self.create_font_row(f, "Подписи осей", "label", 7, size_range=(8, 24))
        self.create_font_row(f, "Числа на осях", "tick", 9, size_range=(6, 20))
        self.create_font_row(f, "Легенда", "legend", 11, size_range=(6, 20))

        # Ползунки стилей
        style_rows = [
            ("Линии графиков", 'line_width', 0.5, 5), ("Толщина рамки", 'spine_width', 0.1, 3),
            ("Осн. деления (толщ)", 'major_tick_width', 0.1, 3), ("Осн. деления (длина)", 'major_tick_length', 0, 15),
            ("Пром. деления (толщ)", 'minor_tick_width', 0.1, 3), ("Пром. деления (длина)", 'minor_tick_length', 0, 15),
            ("Сетка (толщина)", 'grid_width', 0.1, 2), ("Сетка (прозрачность)", 'grid_alpha', 0, 1)
        ]
        r_idx = 14
        for lbl, p, f_val, t_val in style_rows:
            self.create_style_row(f, lbl, p, f_val, t_val, r_idx)
            r_idx += 1

        ttk.Separator(f, orient="horizontal").grid(row=r_idx, column=0, columnspan=3, sticky="ew", pady=15)
        r_idx += 1
        
        # Шаги делений
        tick_rows = [("X Основной", 'x_major_step', 10), ("Y Основной", 'y_major_step', 1000000),
                     ("X Промежут.", 'x_minor_step', 5), ("Y Промежут.", 'y_minor_step', 500000)]
        for lbl, p, lim in tick_rows:
            self.create_style_row(f, lbl, p, 0, lim, r_idx)
            r_idx += 1
            
        ttk.Button(f, text="🔄 Сбросить всё", command=self.controller.on_reset_style).grid(row=r_idx, column=0, columnspan=3, sticky="ew", pady=20)

    def on_preset_selected(self, event=None) -> None:
        preset = self.preset_cb.get()
        presets = {
            "HD (12.8x7.2)": (12.8, 7.2),
            "FullHD (19.2x10.8)": (19.2, 10.8),
            "4K (38.4x21.6)": (38.4, 21.6),
            "A4 Альбомная (11.7x8.3)": (11.69, 8.27),
            "Квадрат (10x10)": (10.0, 10.0),
            "По умолчанию (10x6)": (10.0, 6.0)
        }
        if preset in presets:
            w, h = presets[preset]
            self.fig_w_var.set(w)
            self.fig_h_var.set(h)
            self.controller.on_apply_figure_size(w, h, custom=False)

    def create_font_row(self, master, label, prefix, row, include_inherit=True, size_range=None) -> None:
        ttk.Label(master, text=label+":", font='Arial 9 bold').grid(row=row, column=0, sticky="w", pady=(5,0))
        f_frame = ttk.Frame(master)
        f_frame.grid(row=row+1, column=0, columnspan=3, sticky="ew")
        
        families = ["Arial", "Times New Roman", "Verdana", "Courier New", "Tahoma"]
        weights = ["normal", "bold", "light"]
        styles = ["normal", "italic"]
        
        if include_inherit:
            families = ["Inherit"] + families
            weights = ["Inherit"] + weights
            styles = ["Inherit"] + styles
            
        for prop, vals, w in [('font', families, 15), ('weight', weights, 10), ('style', styles, 10)]:
            var = tk.StringVar()
            cb = ttk.Combobox(f_frame, textvariable=var, values=vals, width=w, state="readonly")
            cb.pack(side="left", padx=2)
            self.font_vars[f'{prefix}_{prop}'] = var
            var.trace_add("write", lambda *a, k=f'{prefix}_{prop}', v=var: self.controller.update_style(k, v.get()))
            
        if size_range:
            p_name = f'{prefix}_size'
            s = ttk.Scale(f_frame, from_=size_range[0], to=size_range[1], command=lambda v, k=p_name: self.on_scale_change(k, v))
            s.pack(side="left", fill="x", expand=True, padx=5)
            e = ttk.Entry(f_frame, width=4)
            e.pack(side="left")
            e.bind("<Return>", lambda ev, k=p_name, en=e: self.on_entry_change(k, en.get()))
            self.style_widgets[p_name] = {'scale': s, 'entry': e}

    def create_style_row(self, master, label, param, f, t, row) -> None:
        ttk.Label(master, text=label+":").grid(row=row, column=0, sticky="w")
        s = ttk.Scale(master, from_=f, to=t, command=lambda v, k=param: self.on_scale_change(k, v))
        s.grid(row=row, column=1, sticky="ew", padx=5)
        e = ttk.Entry(master, width=8)
        e.grid(row=row, column=2)
        e.bind("<Return>", lambda ev, k=param, en=e: self.on_entry_change(k, en.get()))
        self.style_widgets[param] = {'scale': s, 'entry': e}

    def on_scale_change(self, key: str, val: str) -> None:
        v = float(val)
        self.style_widgets[key]['entry'].delete(0, tk.END)
        self.style_widgets[key]['entry'].insert(0, f"{v:.2f}")
        self.controller.update_style(key, v)

    def on_entry_change(self, key: str, val: str) -> None:
        try:
            v = float(val.replace(',', '.'))
            self.style_widgets[key]['scale'].set(v)
            self.controller.update_style(key, v)
        except ValueError:
            pass

    def set_values(self, config) -> None:
        """Заполняет UI значениями из конфига."""
        for k, var in self.font_vars.items():
            var.set(getattr(config, k))
            
        for k, w in self.style_widgets.items():
            val = getattr(config, k)
            w['scale'].set(val)
            w['entry'].delete(0, tk.END)
            w['entry'].insert(0, f"{val:.2f}")
            
        self.fig_w_var.set(config.fig_width)
        self.fig_h_var.set(config.fig_height)
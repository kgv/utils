# ui/tab_labels.py
import tkinter as tk
from tkinter import ttk

class TabLabels(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.label_entries = {}
        self.legend_var = tk.BooleanVar(self, value=True)
        
        # Словари для перевода позиций легенды
        self.legend_pos_map = {
            "Автоматически": "best",
            "Сверху справа": "upper right",
            "Сверху слева": "upper left",
            "Снизу слева": "lower left",
            "Снизу справа": "lower right",
            "Справа": "right",
            "По центру слева": "center left",
            "По центру справа": "center right",
            "Снизу по центру": "lower center",
            "Сверху по центру": "upper center",
            "По центру": "center"
        }
        self.legend_pos_rev_map = {v: k for k, v in self.legend_pos_map.items()}
        
        self.setup_ui()

    def setup_ui(self) -> None:
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both")
        
        fields = [
            ("Заголовок:", 'title_text'), 
            ("Ось X:", 'x_label'), 
            ("Ось Y (Абс):", 'y_label_abs'), 
            ("Ось Y (Норм):", 'y_label_norm')
        ]
        
        for txt, key in fields:
            ttk.Label(frame, text=txt).pack(anchor="w")
            ent = ttk.Entry(frame)
            ent.pack(fill="x", pady=2)
            ent.bind("<KeyRelease>", lambda e, k=key, en=ent: self.controller.update_style(k, en.get()))
            self.label_entries[key] = ent
            
        # Блок настроек легенды
        leg_frame = ttk.Frame(frame)
        leg_frame.pack(anchor="w", pady=15, fill="x")
        
        ttk.Checkbutton(leg_frame, text="Показывать легенду", variable=self.legend_var, 
                        command=lambda: self.controller.update_style('show_legend', self.legend_var.get())).pack(side="left")
                        
        ttk.Label(leg_frame, text="Позиция:").pack(side="left", padx=(20, 5))
        self.cb_leg_pos = ttk.Combobox(leg_frame, values=list(self.legend_pos_map.keys()), state="readonly", width=20)
        self.cb_leg_pos.pack(side="left")
        self.cb_leg_pos.bind("<<ComboboxSelected>>", self.on_legend_pos_change)

    def on_legend_pos_change(self, event=None):
        ru_val = self.cb_leg_pos.get()
        en_val = self.legend_pos_map.get(ru_val, "best")
        self.controller.update_style('legend_position', en_val)

    def set_values(self, config) -> None:
        """Заполняет поля текущими значениями из конфига."""
        for key, ent in self.label_entries.items():
            ent.delete(0, tk.END)
            ent.insert(0, getattr(config, key))
            
        self.legend_var.set(config.show_legend)
        
        # Устанавливаем позицию легенды в Combobox
        current_pos = getattr(config, 'legend_position', 'best')
        ru_val = self.legend_pos_rev_map.get(current_pos, "Автоматически")
        self.cb_leg_pos.set(ru_val)
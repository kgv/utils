# ui/tab_labels.py
import tkinter as tk
from tkinter import ttk

class TabLabels(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.label_entries = {}
        self.legend_var = tk.BooleanVar(value=True)
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
            
        ttk.Checkbutton(frame, text="Легенда", variable=self.legend_var, 
                        command=lambda: self.controller.update_style('show_legend', self.legend_var.get())).pack(anchor="w", pady=10)

    def set_values(self, config) -> None:
        """Заполняет поля текущими значениями из конфига."""
        for key, ent in self.label_entries.items():
            ent.delete(0, tk.END)
            ent.insert(0, getattr(config, key))
        self.legend_var.set(config.show_legend)
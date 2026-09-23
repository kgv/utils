# ui/control_panel.py
import tkinter as tk
from tkinter import ttk
from ui.tab_files import TabFiles
from ui.tab_scale import TabScale
from ui.tab_labels import TabLabels
from ui.tab_helpers import TabHelpers
from ui.tab_style import TabStyle

class ControlPanel(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Панель управления")
        self.geometry("1150x950")
        self.protocol("WM_DELETE_WINDOW", self.controller.on_close)
        
        self.auto_update_var = tk.BooleanVar(value=True)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tab_files = TabFiles(self.notebook, controller)
        self.tab_scale = TabScale(self.notebook, controller)
        self.tab_labels = TabLabels(self.notebook, controller)
        self.tab_helpers = TabHelpers(self.notebook, controller)
        self.tab_style = TabStyle(self.notebook, controller)
        
        self.notebook.add(self.tab_files, text=" 📂 Файлы ")
        self.notebook.add(self.tab_scale, text=" 📏 Масштаб ")
        self.notebook.add(self.tab_labels, text=" 📝 Подписи ")
        self.notebook.add(self.tab_helpers, text=" 📍 Линии ")
        self.notebook.add(self.tab_style, text=" 🎨 Оформление ")
        
        self.setup_bottom_panel()

    def setup_bottom_panel(self) -> None:
        bottom_panel = ttk.Frame(self, padding=10)
        bottom_panel.pack(side="bottom", fill="x")

        ttk.Checkbutton(bottom_panel, text="Авто-обновление", 
                        variable=self.auto_update_var).pack(side="left", padx=10)

        btn_apply = ttk.Button(bottom_panel, text="🔄 ПРИМЕНИТЬ ИЗМЕНЕНИЯ", 
                               command=lambda: self.controller.request_refresh(force=True))
        btn_apply.pack(side="left", expand=True, fill="x", padx=5)

        ttk.Button(bottom_panel, text="💾 Сохранить график", 
                   command=self.controller.on_save_plot).pack(side="left", expand=True, fill="x", padx=5)
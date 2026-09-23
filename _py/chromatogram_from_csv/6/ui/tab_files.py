# ui/tab_files.py
import tkinter as tk
from tkinter import ttk
from typing import List
from models import PlotItem
from ui.utils import ToolTip

class TabFiles(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.setup_ui()

    def setup_ui(self) -> None:
        f_btns = ttk.Frame(self, padding=10)
        f_btns.pack(fill="x")
        
        ttk.Button(f_btns, text="➕ Добавить файлы", command=self.controller.on_add_files).pack(side="left", padx=5)
        ttk.Button(f_btns, text="🗑️ Очистить всё", command=self.controller.on_clear_all).pack(side="left", padx=5)
        
        h_header = ttk.Frame(self, padding=(15, 0))
        h_header.pack(fill="x")
        
        cols = [("Слой", 60), ("Вид", 40), ("Цвет", 40), ("Стиль", 50), 
                ("Толщ", 50), ("Смещ. X", 60), ("Смещ. Y", 60), ("Лег", 40), ("Имя в легенде", 200)]
        for t, w in cols: 
            ttk.Label(h_header, text=t, width=int(w/7), font='Arial 8 bold').pack(side="left", padx=2)
        
        self.f_canvas = tk.Canvas(self)
        self.f_scroll = ttk.Scrollbar(self, orient="vertical", command=self.f_canvas.yview)
        self.f_frame = ttk.Frame(self.f_canvas)
        
        self.f_frame.bind("<Configure>", lambda e: self.f_canvas.configure(scrollregion=self.f_canvas.bbox("all")))
        self.f_canvas.create_window((0, 0), window=self.f_frame, anchor="nw")
        self.f_canvas.configure(yscrollcommand=self.f_scroll.set)
        
        self.f_canvas.pack(side="left", fill="both", expand=True)
        self.f_scroll.pack(side="right", fill="y")

    def update_list(self, plots: List[PlotItem]) -> None:
        """Перерисовывает список файлов на основе актуальных данных."""
        for w in self.f_frame.winfo_children():
            w.destroy()
            
        for i, item in enumerate(reversed(plots)):
            idx = len(plots) - 1 - i
            f = ttk.Frame(self.f_frame)
            f.pack(fill="x", pady=2, padx=5)
            
            # 1. Слой (перемещение)
            ttk.Button(f, text="↑", width=2, command=lambda ix=idx: self.controller.on_move_plot(ix, 1)).pack(side="left")
            ttk.Button(f, text="↓", width=2, command=lambda ix=idx: self.controller.on_move_plot(ix, -1)).pack(side="left", padx=(0,5))
            
            # 2. Видимость
            vis_v = tk.BooleanVar(value=item.visible)
            ttk.Checkbutton(f, variable=vis_v, command=lambda ix=idx, v=vis_v: self.controller.update_plot(ix, 'visible', v.get())).pack(side="left", padx=7)
            
            # 3. Цвет
            btn_c = tk.Button(f, bg=item.color, width=2, relief="flat",
                              command=lambda ix=idx: self.controller.show_color_picker(ix, is_helper=False))
            btn_c.pack(side="left", padx=2)
            
            # 4. Стиль линии
            cb = ttk.Combobox(f, values=["-", "--", ":", "-."], width=3, state="readonly")
            cb.set(item.linestyle)
            cb.pack(side="left", padx=2)
            cb.bind("<<ComboboxSelected>>", lambda e, ix=idx, c=cb: self.controller.update_plot(ix, 'linestyle', c.get()))
            
            # 5. Толщина линии
            sp = tk.Spinbox(f, from_=0.1, to=10, increment=0.1, width=4)
            sp.insert(0, f"{item.line_width:.1f}")
            sp.pack(side="left", padx=2)
            sp.bind("<Return>", lambda e, ix=idx, s=sp: [self.controller.update_plot(ix, 'line_width', s.get()), self.focus_set()])
            sp.bind("<FocusOut>", lambda e, ix=idx, s=sp: self.controller.update_plot(ix, 'line_width', s.get()))
            
            # 6. Смещение по X
            sp_x = tk.Spinbox(f, from_=-1e9, to=1e9, increment=0.1, width=5)
            sp_x.insert(0, f"{item.x_offset:.2f}")
            sp_x.pack(side="left", padx=2)
            sp_x.bind("<Return>", lambda e, ix=idx, s=sp_x: [self.controller.update_plot(ix, 'x_offset', s.get()), self.focus_set()])
            sp_x.bind("<FocusOut>", lambda e, ix=idx, s=sp_x: self.controller.update_plot(ix, 'x_offset', s.get()))
            
            # 7. Смещение по Y
            sp_y = tk.Spinbox(f, from_=-1e12, to=1e12, increment=10, width=6)
            sp_y.insert(0, f"{item.y_offset:.2f}")
            sp_y.pack(side="left", padx=2)
            sp_y.bind("<Return>", lambda e, ix=idx, s=sp_y: [self.controller.update_plot(ix, 'y_offset', s.get()), self.focus_set()])
            sp_y.bind("<FocusOut>", lambda e, ix=idx, s=sp_y: self.controller.update_plot(ix, 'y_offset', s.get()))
            
            # 8. Легенда
            leg_v = tk.BooleanVar(value=item.show_in_legend)
            ttk.Checkbutton(f, variable=leg_v, command=lambda ix=idx, v=leg_v: self.controller.update_plot(ix, 'show_in_legend', v.get())).pack(side="left", padx=5)
            
            # 9. Удаление
            ttk.Button(f, text="🗑️", width=3, command=lambda ix=idx: self.controller.on_remove_plot(ix)).pack(side="right", padx=2)
            
            # 10. Название
            ent = ttk.Entry(f)
            ent.insert(0, item.label)
            ent.pack(side="left", fill="x", expand=True)
            ent.bind("<KeyRelease>", lambda e, ix=idx, en=ent: self.controller.update_plot(ix, 'label', en.get()))
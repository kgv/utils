# ui/tab_helpers.py
import tkinter as tk
from tkinter import ttk
from typing import List
from models import HelperLine
from ui.utils import ToolTip

class TabHelpers(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.h_type = tk.StringVar(value="V")
        self.setup_ui()

    def setup_ui(self) -> None:
        io_frame = ttk.Frame(self)
        io_frame.pack(fill="x", pady=(0, 10))
        ttk.Button(io_frame, text="💾 Экспорт линий", command=self.controller.on_export_helpers).pack(side="left", expand=True, fill="x", padx=2)
        ttk.Button(io_frame, text="📂 Импорт линий", command=self.controller.on_import_helpers).pack(side="left", expand=True, fill="x", padx=2)

        f_add = ttk.LabelFrame(self, text="Добавить линию", padding=10)
        f_add.pack(fill="x")
        
        ttk.Radiobutton(f_add, text="Вертикаль", variable=self.h_type, value="V").grid(row=0, column=0)
        ttk.Radiobutton(f_add, text="Горизонталь", variable=self.h_type, value="H").grid(row=0, column=1)
        ttk.Button(f_add, text="➕ Создать", command=lambda: self.controller.on_add_helper(self.h_type.get())).grid(row=0, column=2, padx=20)
        
        self.h_canvas = tk.Canvas(self)
        self.h_scroll = ttk.Scrollbar(self, orient="vertical", command=self.h_canvas.yview)
        self.h_frame = ttk.Frame(self.h_canvas)
        
        self.h_frame.bind("<Configure>", lambda e: self.h_canvas.configure(scrollregion=self.h_canvas.bbox("all")))
        self.h_canvas.create_window((0, 0), window=self.h_frame, anchor="nw")
        self.h_canvas.configure(yscrollcommand=self.h_scroll.set)
        
        self.h_canvas.pack(side="left", fill="both", expand=True)
        self.h_scroll.pack(side="right", fill="y")

    def update_list(self, helpers: List[HelperLine], x_step: float, y_step: float) -> None:
        for w in self.h_frame.winfo_children():
            w.destroy()
            
        for i, h in enumerate(helpers):
            f_row = ttk.Frame(self.h_frame)
            f_row.pack(fill="x", pady=2)
            
            lbl_type = ttk.Label(f_row, text=h.line_type, width=3)
            lbl_type.pack(side="left")
            ToolTip(lbl_type, "Тип линии (V - вертикальная, H - горизонтальная)")
            
            is_v = h.line_type == 'V'
            step_main = x_step if is_v else y_step
            step_range = y_step if is_v else x_step
            
            # Координаты
            for k, w, step, tip in [
                ('pos', 7, step_main, "Позиция линии"), 
                ('start', 7, step_range, "Начало линии"), 
                ('end', 7, step_range, "Конец линии")
            ]:
                sp = tk.Spinbox(f_row, from_=-1e9, to=1e9, increment=step, width=w)
                sp.delete(0, tk.END)
                sp.insert(0, str(getattr(h, k)))
                sp.pack(side="left", padx=1)
                sp.bind("<Return>", lambda ev, ix=i, key=k, s=sp: [self.controller.update_helper(ix, key, s.get()), self.focus_set()])
                sp.bind("<FocusOut>", lambda ev, ix=i, key=k, s=sp: self.controller.update_helper(ix, key, s.get()))
                ToolTip(sp, tip)

            # Текст
            e_txt = ttk.Entry(f_row, width=10)
            e_txt.insert(0, h.text)
            e_txt.pack(side="left", padx=1)
            e_txt.bind("<KeyRelease>", lambda ev, ix=i, en=e_txt: self.controller.update_helper(ix, 'text', en.get()))
            ToolTip(e_txt, "Текст подписи")
            
            # Позиция текста
            sp_p = tk.Spinbox(f_row, from_=-1e12, to=1e12, increment=step_range, width=7)
            sp_p.delete(0, tk.END)
            sp_p.insert(0, str(h.label_pos))
            sp_p.pack(side="left", padx=1)
            sp_p.bind("<Return>", lambda ev, ix=i, s=sp_p: [self.controller.update_helper(ix, 'label_pos', s.get()), self.focus_set()])
            sp_p.bind("<FocusOut>", lambda ev, ix=i, s=sp_p: self.controller.update_helper(ix, 'label_pos', s.get()))
            ToolTip(sp_p, "Координата текста")

            btn_auto = ttk.Button(f_row, text="Авто", width=4, command=lambda ix=i: self.controller.on_auto_label_pos(ix))
            btn_auto.pack(side="left", padx=1)
            ToolTip(btn_auto, "Установить по наибольшему значению видимых графиков")

            # Смещение, поворот, размер шрифта
            for k, w, step, tip in [
                ('label_offset', 5, step_main, "Смещение текста от линии"),
                ('label_rotation', 4, 15, "Угол поворота текста"),
                ('font_size', 3, 1, "Размер шрифта")
            ]:
                sp_o = tk.Spinbox(f_row, from_=-1e9, to=1e9, increment=step, width=w)
                sp_o.delete(0, tk.END)
                sp_o.insert(0, str(getattr(h, k)))
                sp_o.pack(side="left", padx=1)
                sp_o.bind("<Return>", lambda ev, ix=i, key=k, s=sp_o: [self.controller.update_helper(ix, key, s.get()), self.focus_set()])
                sp_o.bind("<FocusOut>", lambda ev, ix=i, key=k, s=sp_o: self.controller.update_helper(ix, key, s.get()))
                ToolTip(sp_o, tip)

            # Слой
            cb_l = ttk.Combobox(f_row, values=["Задний", "Передний"], width=8, state="readonly")
            cb_l.set(h.layer)
            cb_l.pack(side="left", padx=1)
            cb_l.bind("<<ComboboxSelected>>", lambda e, ix=i, c=cb_l: self.controller.update_helper(ix, 'layer', c.get()))
            
            # Толщина
            sp_w = tk.Spinbox(f_row, from_=0.0, to=10.0, increment=0.1, width=4)
            sp_w.delete(0, tk.END)
            sp_w.insert(0, str(h.width))
            sp_w.pack(side="left", padx=1)
            sp_w.bind("<Return>", lambda ev, ix=i, s=sp_w: [self.controller.update_helper(ix, 'width', s.get()), self.focus_set()])
            sp_w.bind("<FocusOut>", lambda ev, ix=i, s=sp_w: self.controller.update_helper(ix, 'width', s.get()))
            
            # Цвет и удаление
            btn_c = tk.Button(f_row, bg=h.color, width=2, relief="flat", command=lambda ix=i: self.controller.show_color_picker(ix, is_helper=True))
            btn_c.pack(side="left", padx=2)
            
            ttk.Button(f_row, text="🗑️", width=3, command=lambda idx=i: self.controller.on_remove_helper(idx)).pack(side="right")
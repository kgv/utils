# ui/tab_helpers.py
import tkinter as tk
from tkinter import ttk
from typing import List
from models import PlotItem
from ui.utils import ToolTip

class TabHelpers(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.h_type = tk.StringVar(self, value="V")
        self.target_plot_var = tk.StringVar(self)
        self.setup_ui()

    def setup_ui(self) -> None:
        f_add = ttk.LabelFrame(self, text="Добавить линию", padding=10)
        f_add.pack(fill="x", pady=(0, 10))
        
        ttk.Label(f_add, text="Файл:").grid(row=0, column=0, padx=5)
        self.plot_cb = ttk.Combobox(f_add, textvariable=self.target_plot_var, state="readonly", width=25)
        self.plot_cb.grid(row=0, column=1, padx=5)
        
        ttk.Radiobutton(f_add, text="Вертикаль", variable=self.h_type, value="V").grid(row=0, column=2, padx=5)
        ttk.Radiobutton(f_add, text="Горизонталь", variable=self.h_type, value="H").grid(row=0, column=3, padx=5)
        ttk.Button(f_add, text="➕ Создать", command=self.controller.on_add_helper).grid(row=0, column=4, padx=20)
        
        self.h_canvas = tk.Canvas(self)
        self.h_scroll = ttk.Scrollbar(self, orient="vertical", command=self.h_canvas.yview)
        self.h_frame = ttk.Frame(self.h_canvas)
        
        self.h_frame.bind("<Configure>", lambda e: self.h_canvas.configure(scrollregion=self.h_canvas.bbox("all")))
        self.h_canvas.create_window((0, 0), window=self.h_frame, anchor="nw")
        self.h_canvas.configure(yscrollcommand=self.h_scroll.set)
        
        self.h_canvas.pack(side="left", fill="both", expand=True)
        self.h_scroll.pack(side="right", fill="y")

    def update_list(self, plots: List[PlotItem], x_step: float, y_step: float) -> None:
        # Обновляем список файлов в комбобоксе
        plot_names = [f"{i}: {p.label}" for i, p in enumerate(plots)]
        self.plot_cb['values'] = plot_names
        if plot_names and self.target_plot_var.get() not in plot_names:
            self.plot_cb.set(plot_names[0])
        elif not plot_names:
            self.plot_cb.set("")

        for w in self.h_frame.winfo_children():
            w.destroy()
            
        for p_idx, p in enumerate(plots):
            if not p.helpers: continue
            
            f_header = ttk.Frame(self.h_frame)
            f_header.pack(fill="x", pady=(10, 2), padx=5)
            
            lbl = ttk.Label(f_header, text=f"Файл: {p.label}", font="Arial 9 bold", foreground="#0055A4")
            lbl.pack(side="left")
            
            btn_auto_all = ttk.Button(f_header, text="Авто для всех", command=lambda p_ix=p_idx: self.controller.on_auto_label_pos_all(p_ix))
            btn_auto_all.pack(side="left", padx=15)
            ToolTip(btn_auto_all, "Установить позиции всех подписей этого файла по графику")
            
            for h_idx, h in enumerate(p.helpers):
                f_row = ttk.Frame(self.h_frame)
                f_row.pack(fill="x", pady=2, padx=(15, 0))
                
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
                    sp.config(command=lambda p_ix=p_idx, h_ix=h_idx, key=k, s=sp: self.controller.update_helper(p_ix, h_ix, key, s.get()))
                    sp.delete(0, tk.END)
                    sp.insert(0, str(getattr(h, k)))
                    sp.pack(side="left", padx=1)
                    sp.bind("<Return>", lambda ev, p_ix=p_idx, h_ix=h_idx, key=k, s=sp: [self.controller.update_helper(p_ix, h_ix, key, s.get()), self.focus_set()])
                    sp.bind("<FocusOut>", lambda ev, p_ix=p_idx, h_ix=h_idx, key=k, s=sp: self.controller.update_helper(p_ix, h_ix, key, s.get()))
                    ToolTip(sp, tip)

                # Текст
                e_txt = ttk.Entry(f_row, width=10)
                e_txt.insert(0, h.text)
                e_txt.pack(side="left", padx=1)
                e_txt.bind("<KeyRelease>", lambda ev, p_ix=p_idx, h_ix=h_idx, en=e_txt: self.controller.update_helper(p_ix, h_ix, 'text', en.get()))
                ToolTip(e_txt, "Текст подписи")
                
                # Позиция текста
                sp_p = tk.Spinbox(f_row, from_=-1e12, to=1e12, increment=step_range, width=7)
                sp_p.config(command=lambda p_ix=p_idx, h_ix=h_idx, s=sp_p: self.controller.update_helper(p_ix, h_ix, 'label_pos', s.get()))
                sp_p.delete(0, tk.END)
                sp_p.insert(0, str(h.label_pos))
                sp_p.pack(side="left", padx=1)
                sp_p.bind("<Return>", lambda ev, p_ix=p_idx, h_ix=h_idx, s=sp_p: [self.controller.update_helper(p_ix, h_ix, 'label_pos', s.get()), self.focus_set()])
                sp_p.bind("<FocusOut>", lambda ev, p_ix=p_idx, h_ix=h_idx, s=sp_p: self.controller.update_helper(p_ix, h_ix, 'label_pos', s.get()))
                ToolTip(sp_p, "Координата текста")

                btn_auto = ttk.Button(f_row, text="Авто", width=4, command=lambda p_ix=p_idx, h_ix=h_idx: self.controller.on_auto_label_pos(p_ix, h_ix))
                btn_auto.pack(side="left", padx=1)
                ToolTip(btn_auto, "Установить по наибольшему значению видимых графиков")

                # Смещение, поворот, размер шрифта
                for k, w, step, tip in [
                    ('label_offset', 5, step_main, "Смещение текста от линии"),
                    ('label_rotation', 4, 15, "Угол поворота текста"),
                    ('font_size', 3, 1, "Размер шрифта")
                ]:
                    sp_o = tk.Spinbox(f_row, from_=-1e9, to=1e9, increment=step, width=w)
                    sp_o.config(command=lambda p_ix=p_idx, h_ix=h_idx, key=k, s=sp_o: self.controller.update_helper(p_ix, h_ix, key, s.get()))
                    sp_o.delete(0, tk.END)
                    sp_o.insert(0, str(getattr(h, k)))
                    sp_o.pack(side="left", padx=1)
                    sp_o.bind("<Return>", lambda ev, p_ix=p_idx, h_ix=h_idx, key=k, s=sp_o: [self.controller.update_helper(p_ix, h_ix, key, s.get()), self.focus_set()])
                    sp_o.bind("<FocusOut>", lambda ev, p_ix=p_idx, h_ix=h_idx, key=k, s=sp_o: self.controller.update_helper(p_ix, h_ix, key, s.get()))
                    ToolTip(sp_o, tip)

                # Слой
                cb_l = ttk.Combobox(f_row, values=["Задний", "Передний"], width=8, state="readonly")
                cb_l.set(h.layer)
                cb_l.pack(side="left", padx=1)
                cb_l.bind("<<ComboboxSelected>>", lambda e, p_ix=p_idx, h_ix=h_idx, c=cb_l: self.controller.update_helper(p_ix, h_ix, 'layer', c.get()))
                ToolTip(cb_l, "Слой")
                
                # Толщина
                sp_w = tk.Spinbox(f_row, from_=0.0, to=10.0, increment=0.1, width=4)
                sp_w.config(command=lambda p_ix=p_idx, h_ix=h_idx, s=sp_w: self.controller.update_helper(p_ix, h_ix, 'width', s.get()))
                sp_w.delete(0, tk.END)
                sp_w.insert(0, str(h.width))
                sp_w.pack(side="left", padx=1)
                sp_w.bind("<Return>", lambda ev, p_ix=p_idx, h_ix=h_idx, s=sp_w: [self.controller.update_helper(p_ix, h_ix, 'width', s.get()), self.focus_set()])
                sp_w.bind("<FocusOut>", lambda ev, p_ix=p_idx, h_ix=h_idx, s=sp_w: self.controller.update_helper(p_ix, h_ix, 'width', s.get()))
                ToolTip(sp_w, "Толщина")
                
                # Цвет
                btn_c = tk.Button(f_row, bg=h.color, width=2, relief="flat", command=lambda p_ix=p_idx, h_ix=h_idx: self.controller.show_color_picker(p_ix, is_helper=True, helper_idx=h_ix))
                btn_c.pack(side="left", padx=2)
                ToolTip(btn_c, "Цвет")

                # Удаление
                ttk.Button(f_row, text="🗑️", width=3, command=lambda p_ix=p_idx, h_ix=h_idx: self.controller.on_remove_helper(p_ix, h_ix)).pack(side="right")
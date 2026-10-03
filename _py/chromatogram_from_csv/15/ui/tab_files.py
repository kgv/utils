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
        # Верхняя панель кнопок
        f_btns = ttk.Frame(self, padding=10)
        f_btns.pack(fill="x")

        ttk.Button(f_btns, text="➕ Добавить файлы", command=self.controller.on_add_files).pack(side="left", padx=5)
        ttk.Button(f_btns, text="🗑️ Очистить всё", command=self.controller.on_clear_all).pack(side="left", padx=5)
        ttk.Button(f_btns, text="💾 Экспорт настроек", command=self.controller.on_export_file_settings).pack(side="left", padx=5)
        ttk.Button(f_btns, text="📂 Импорт настроек", command=self.controller.on_import_file_settings).pack(side="left", padx=5)

        # Разделитель на две панели (Левая - Файлы, Правая - Метки)
        self.paned = ttk.PanedWindow(self, orient="horizontal")
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        # --- Левая панель (Файлы) ---
        self.f_container = ttk.Frame(self.paned)
        self.paned.add(self.f_container, weight=3)
        
        ttk.Label(self.f_container, text="Список файлов и настройки масштаба", font="Arial 10 bold").pack(anchor="w", pady=(0, 5))
        
        self.f_canvas = tk.Canvas(self.f_container)
        self.f_scroll = ttk.Scrollbar(self.f_container, orient="vertical", command=self.f_canvas.yview)
        self.f_frame = ttk.Frame(self.f_canvas)

        self.f_frame.bind("<Configure>", lambda e: self.f_canvas.configure(scrollregion=self.f_canvas.bbox("all")))
        self.f_canvas.create_window((0, 0), window=self.f_frame, anchor="nw")
        self.f_canvas.configure(yscrollcommand=self.f_scroll.set)

        self.f_canvas.pack(side="left", fill="both", expand=True)
        self.f_scroll.pack(side="right", fill="y")

        # --- Правая панель (Метки) ---
        self.m_container = ttk.Frame(self.paned)
        self.paned.add(self.m_container, weight=2)
        
        ttk.Label(self.m_container, text="Метки видимых файлов", font="Arial 10 bold").pack(anchor="w", pady=(0, 5))
        
        self.m_canvas = tk.Canvas(self.m_container)
        self.m_scroll = ttk.Scrollbar(self.m_container, orient="vertical", command=self.m_canvas.yview)
        self.m_frame = ttk.Frame(self.m_canvas)

        self.m_frame.bind("<Configure>", lambda e: self.m_canvas.configure(scrollregion=self.m_canvas.bbox("all")))
        self.m_canvas.create_window((0, 0), window=self.m_frame, anchor="nw")
        self.m_canvas.configure(yscrollcommand=self.m_scroll.set)

        self.m_canvas.pack(side="left", fill="both", expand=True)
        self.m_scroll.pack(side="right", fill="y")

    def update_list(self, plots: List[PlotItem]) -> None:
        """Перерисовывает список файлов на основе актуальных данных."""
        for w in self.f_frame.winfo_children():
            w.destroy()

        self.plot_vars = []

        for idx, item in enumerate(plots):
            f_main = ttk.LabelFrame(self.f_frame, text=f"Файл {idx+1}: {item.label}")
            f_main.pack(fill="x", pady=4, padx=5)

            # --- Ряд 1: Базовые настройки ---
            r1 = ttk.Frame(f_main)
            r1.pack(fill="x", pady=2, padx=2)

            ttk.Button(r1, text="↑", width=2, command=lambda ix=idx: self.controller.on_move_plot(ix, -1)).pack(side="left")
            ttk.Button(r1, text="↓", width=2, command=lambda ix=idx: self.controller.on_move_plot(ix, 1)).pack(side="left", padx=(0, 5))

            vis_v = tk.BooleanVar(value=item.visible)
            self.plot_vars.append(vis_v)
            ttk.Checkbutton(r1, text="Вид", variable=vis_v, command=lambda ix=idx, v=vis_v: self.controller.update_plot(ix, "visible", v.get())).pack(side="left", padx=2)

            tk.Button(r1, bg=item.color, width=2, relief="flat", command=lambda ix=idx: self.controller.show_color_picker(ix, is_marker=False)).pack(side="left", padx=2)

            cb_style = ttk.Combobox(r1, values=["-", "--", ":", "-."], width=3, state="readonly")
            cb_style.set(item.linestyle)
            cb_style.pack(side="left", padx=2)
            cb_style.bind("<<ComboboxSelected>>", lambda e, ix=idx, c=cb_style: self.controller.update_plot(ix, "linestyle", c.get()))

            sp_w = tk.Spinbox(r1, from_=0.1, to=10, increment=0.1, width=4)
            sp_w.delete(0, tk.END)
            sp_w.insert(0, f"{item.line_width:.1f}")
            sp_w.pack(side="left", padx=2)
            sp_w.bind("<Return>", lambda e, ix=idx, s=sp_w: [self.controller.update_plot(ix, "line_width", s.get()), self.focus_set()])
            sp_w.bind("<FocusOut>", lambda e, ix=idx, s=sp_w: self.controller.update_plot(ix, "line_width", s.get()))
            ToolTip(sp_w, "Толщина линии")

            sp_x = tk.Spinbox(r1, from_=-1e9, to=1e9, increment=0.1, width=5)
            sp_x.delete(0, tk.END)
            sp_x.insert(0, f"{item.x_offset:.2f}")
            sp_x.pack(side="left", padx=2)
            sp_x.bind("<Return>", lambda e, ix=idx, s=sp_x: [self.controller.update_plot(ix, "x_offset", s.get()), self.focus_set()])
            sp_x.bind("<FocusOut>", lambda e, ix=idx, s=sp_x: self.controller.update_plot(ix, "x_offset", s.get()))
            ToolTip(sp_x, "Смещение по X")

            sp_y = tk.Spinbox(r1, from_=-1e12, to=1e12, increment=10, width=6)
            sp_y.delete(0, tk.END)
            sp_y.insert(0, f"{item.y_offset:.2f}")
            sp_y.pack(side="left", padx=2)
            sp_y.bind("<Return>", lambda e, ix=idx, s=sp_y: [self.controller.update_plot(ix, "y_offset", s.get()), self.focus_set()])
            sp_y.bind("<FocusOut>", lambda e, ix=idx, s=sp_y: self.controller.update_plot(ix, "y_offset", s.get()))
            ToolTip(sp_y, "Смещение по Y")

            leg_v = tk.BooleanVar(value=item.show_in_legend)
            self.plot_vars.append(leg_v)
            ttk.Checkbutton(r1, text="Легенда", variable=leg_v, command=lambda ix=idx, v=leg_v: self.controller.update_plot(ix, "show_in_legend", v.get())).pack(side="left", padx=5)

            ttk.Button(r1, text="🗑️", width=3, command=lambda ix=idx: self.controller.on_remove_plot(ix)).pack(side="right", padx=2)

            ent = ttk.Entry(r1)
            ent.insert(0, item.label)
            ent.pack(side="left", fill="x", expand=True, padx=2)
            ent.bind("<KeyRelease>", lambda e, ix=idx, en=ent: self.controller.update_plot(ix, "label", en.get()))

            # --- Ряд 2: Настройки масштаба и метки ---
            r2 = ttk.Frame(f_main)
            r2.pack(fill="x", pady=2, padx=2)

            cb_mode = ttk.Combobox(r2, values=["Абсолютный", "Нормированный"], width=13, state="readonly")
            cb_mode.set(item.y_mode)
            cb_mode.pack(side="left", padx=2)
            cb_mode.bind("<<ComboboxSelected>>", lambda e, ix=idx, c=cb_mode: self.controller.update_plot(ix, "y_mode", c.get()))

            sec_v = tk.BooleanVar(value=item.convert_sec_to_min)
            self.plot_vars.append(sec_v)
            ttk.Checkbutton(r2, text="Сек->Мин", variable=sec_v, command=lambda ix=idx, v=sec_v: self.controller.update_plot(ix, "convert_sec_to_min", v.get())).pack(side="left", padx=2)

            rev_v = tk.BooleanVar(value=item.reverse_x)
            self.plot_vars.append(rev_v)
            ttk.Checkbutton(r2, text="Инверс X", variable=rev_v, command=lambda ix=idx, v=rev_v: self.controller.update_plot(ix, "reverse_x", v.get())).pack(side="left", padx=2)

            ttk.Label(r2, text="X:").pack(side="left", padx=(5, 1))
            e_xmin = ttk.Entry(r2, width=6)
            e_xmin.insert(0, f"{item.x_min:.3f}")
            e_xmin.pack(side="left")
            e_xmin.bind("<Return>", lambda e, ix=idx, en=e_xmin: [self.controller.update_plot(ix, "x_min", en.get()), self.focus_set()])
            e_xmin.bind("<FocusOut>", lambda e, ix=idx, en=e_xmin: self.controller.update_plot(ix, "x_min", en.get()))
            
            e_xmax = ttk.Entry(r2, width=6)
            e_xmax.insert(0, f"{item.x_max:.3f}")
            e_xmax.pack(side="left", padx=(1, 5))
            e_xmax.bind("<Return>", lambda e, ix=idx, en=e_xmax: [self.controller.update_plot(ix, "x_max", en.get()), self.focus_set()])
            e_xmax.bind("<FocusOut>", lambda e, ix=idx, en=e_xmax: self.controller.update_plot(ix, "x_max", en.get()))

            ttk.Label(r2, text="Y:").pack(side="left", padx=(5, 1))
            e_ymin = ttk.Entry(r2, width=7)
            e_ymin.insert(0, f"{item.y_min:.2f}")
            e_ymin.pack(side="left")
            e_ymin.bind("<Return>", lambda e, ix=idx, en=e_ymin: [self.controller.update_plot(ix, "y_min", en.get()), self.focus_set()])
            e_ymin.bind("<FocusOut>", lambda e, ix=idx, en=e_ymin: self.controller.update_plot(ix, "y_min", en.get()))
            
            e_ymax = ttk.Entry(r2, width=7)
            e_ymax.insert(0, f"{item.y_max:.2f}")
            e_ymax.pack(side="left", padx=(1, 5))
            e_ymax.bind("<Return>", lambda e, ix=idx, en=e_ymax: [self.controller.update_plot(ix, "y_max", en.get()), self.focus_set()])
            e_ymax.bind("<FocusOut>", lambda e, ix=idx, en=e_ymax: self.controller.update_plot(ix, "y_max", en.get()))

            ttk.Button(r2, text="Авто Y", width=6, command=lambda ix=idx: self.controller.on_fit_y_to_visible(ix)).pack(side="left", padx=2)
            
            ttk.Button(r2, text="➕ Метка", width=8, command=lambda ix=idx: self.controller.on_add_marker(ix)).pack(side="right", padx=2)
            ttk.Button(r2, text="Авто метки", width=10, command=lambda ix=idx: self.controller.on_auto_marker_pos_all(ix)).pack(side="right", padx=2)

    def update_markers(self, plots: List[PlotItem], x_step: float, y_step: float) -> None:
        """Перерисовывает список меток только для видимых файлов."""
        for w in self.m_frame.winfo_children():
            w.destroy()

        self.marker_vars = []

        for p_idx, p in enumerate(plots):
            if not p.visible or not p.markers:
                continue

            f_group = ttk.LabelFrame(self.m_frame, text=f"{p.label}", labelanchor='n')
            f_group.pack(fill="x", pady=5, padx=5)

            for m_idx, m in enumerate(p.markers):
                f_m = ttk.Frame(f_group)
                f_m.pack(fill="x", pady=4, padx=2)
                
                # Ряд 1 метки
                r1 = ttk.Frame(f_m)
                r1.pack(fill="x")
                
                for k, w, step, tip in [("anchor_x", 6, x_step, "X привязки"), ("anchor_y", 6, y_step, "Y привязки")]:
                    sp = tk.Spinbox(r1, from_=-1e9, to=1e9, increment=step, width=w)
                    sp.delete(0, tk.END)
                    sp.insert(0, str(getattr(m, k)))
                    sp.pack(side="left", padx=1)
                    sp.bind("<Return>", lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: [self.controller.update_marker(p_ix, m_ix, key, s.get()), self.focus_set()])
                    sp.bind("<FocusOut>", lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: self.controller.update_marker(p_ix, m_ix, key, s.get()))
                    ToolTip(sp, tip)

                ttk.Button(r1, text="Авто", width=4, command=lambda p_ix=p_idx, m_ix=m_idx: self.controller.on_auto_marker_pos(p_ix, m_ix)).pack(side="left", padx=2)

                for k, w, step, tip in [("offset_x", 5, x_step, "Смещение X"), ("offset_y", 5, y_step, "Смещение Y")]:
                    sp = tk.Spinbox(r1, from_=-1e9, to=1e9, increment=step, width=w)
                    sp.delete(0, tk.END)
                    sp.insert(0, str(getattr(m, k)))
                    sp.pack(side="left", padx=1)
                    sp.bind("<Return>", lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: [self.controller.update_marker(p_ix, m_ix, key, s.get()), self.focus_set()])
                    sp.bind("<FocusOut>", lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: self.controller.update_marker(p_ix, m_ix, key, s.get()))
                    ToolTip(sp, tip)

                e_txt = ttk.Entry(r1, width=10)
                e_txt.insert(0, m.text)
                e_txt.pack(side="left", fill="x", expand=True, padx=2)
                e_txt.bind("<KeyRelease>", lambda ev, p_ix=p_idx, m_ix=m_idx, en=e_txt: self.controller.update_marker(p_ix, m_ix, "text", en.get()))
                
                ttk.Button(r1, text="🗑️", width=3, command=lambda p_ix=p_idx, m_ix=m_idx: self.controller.on_remove_marker(p_ix, m_ix)).pack(side="right")

                # Ряд 2 метки
                r2 = ttk.Frame(f_m)
                r2.pack(fill="x", pady=(2, 0))
                
                for k, w, step, tip in [("font_size", 3, 1, "Размер шрифта"), ("label_rotation", 4, 15, "Угол поворота")]:
                    sp_o = tk.Spinbox(r2, from_=-1e9, to=1e9, increment=step, width=w)
                    sp_o.delete(0, tk.END)
                    sp_o.insert(0, str(getattr(m, k)))
                    sp_o.pack(side="left", padx=1)
                    sp_o.bind("<Return>", lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp_o: [self.controller.update_marker(p_ix, m_ix, key, s.get()), self.focus_set()])
                    sp_o.bind("<FocusOut>", lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp_o: self.controller.update_marker(p_ix, m_ix, key, s.get()))
                    ToolTip(sp_o, tip)

                cb_conn_var = tk.BooleanVar(value=getattr(m, "show_connector", False))
                self.marker_vars.append(cb_conn_var)
                ttk.Checkbutton(r2, text="Связь", variable=cb_conn_var, command=lambda p_ix=p_idx, m_ix=m_idx, v=cb_conn_var: self.controller.update_marker(p_ix, m_ix, "show_connector", v.get())).pack(side="left", padx=2)

                sp_w = tk.Spinbox(r2, from_=0.0, to=10.0, increment=0.1, width=4)
                sp_w.delete(0, tk.END)
                sp_w.insert(0, str(m.width))
                sp_w.pack(side="left", padx=1)
                sp_w.bind("<Return>", lambda ev, p_ix=p_idx, m_ix=m_idx, s=sp_w: [self.controller.update_marker(p_ix, m_ix, "width", s.get()), self.focus_set()])
                sp_w.bind("<FocusOut>", lambda ev, p_ix=p_idx, m_ix=m_idx, s=sp_w: self.controller.update_marker(p_ix, m_ix, "width", s.get()))
                ToolTip(sp_w, "Толщина линии связи")

                cb_l = ttk.Combobox(r2, values=["Задний", "Передний"], width=8, state="readonly")
                cb_l.set(m.layer)
                cb_l.pack(side="left", padx=2)
                cb_l.bind("<<ComboboxSelected>>", lambda e, p_ix=p_idx, m_ix=m_idx, c=cb_l: self.controller.update_marker(p_ix, m_ix, "layer", c.get()))

                tk.Button(r2, bg=m.color, width=2, relief="flat", command=lambda p_ix=p_idx, m_ix=m_idx: self.controller.show_color_picker(p_ix, is_marker=True, marker_idx=m_ix)).pack(side="left", padx=2)
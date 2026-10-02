import tkinter as tk
from tkinter import ttk
from typing import List
from models import PlotItem
from ui.utils import ToolTip


class TabHelpers(ttk.Frame):
    def __init__(self, parent: ttk.Notebook, controller):
        super().__init__(parent)
        self.controller = controller
        self.target_plot_var = tk.StringVar(self)
        self.setup_ui()

    def setup_ui(self) -> None:
        f_add = ttk.LabelFrame(self, text="Добавить метку", padding=10)
        f_add.pack(fill="x", pady=(0, 10))

        ttk.Label(f_add, text="Файл:").grid(row=0, column=0, padx=5)
        self.plot_cb = ttk.Combobox(
            f_add, textvariable=self.target_plot_var, state="readonly", width=25
        )
        self.plot_cb.grid(row=0, column=1, padx=5)

        # Радиокнопки удалены, так как теперь у нас только один тип - Метка (Marker)
        ttk.Button(
            f_add, text="➕ Создать", command=self.controller.on_add_marker
        ).grid(row=0, column=2, padx=20)

        self.h_canvas = tk.Canvas(self)
        self.h_scroll = ttk.Scrollbar(
            self, orient="vertical", command=self.h_canvas.yview
        )
        self.h_frame = ttk.Frame(self.h_canvas)

        self.h_frame.bind(
            "<Configure>",
            lambda e: self.h_canvas.configure(scrollregion=self.h_canvas.bbox("all")),
        )
        self.h_canvas.create_window((0, 0), window=self.h_frame, anchor="nw")
        self.h_canvas.configure(yscrollcommand=self.h_scroll.set)

        self.h_canvas.pack(side="left", fill="both", expand=True)
        self.h_scroll.pack(side="right", fill="y")

    def update_list(self, plots: List[PlotItem], x_step: float, y_step: float) -> None:
        # Обновляем список файлов в комбобоксе
        plot_names = [f"{i}: {p.label}" for i, p in enumerate(plots)]
        self.plot_cb["values"] = plot_names
        if plot_names and self.target_plot_var.get() not in plot_names:
            self.plot_cb.set(plot_names[0])
        elif not plot_names:
            self.plot_cb.set("")

        self.marker_vars = getattr(self, "marker_vars", [])
        self.marker_vars.clear()

        for w in self.h_frame.winfo_children():
            w.destroy()

        for p_idx, p in enumerate(plots):
            if not p.markers:
                continue

            f_header = ttk.Frame(self.h_frame)
            f_header.pack(fill="x", pady=(10, 2), padx=5)

            lbl = ttk.Label(
                f_header,
                text=f"Файл: {p.label}",
                font="Arial 9 bold",
                foreground="#0055A4",
            )
            lbl.pack(side="left")

            btn_auto_all = ttk.Button(
                f_header,
                text="Авто для всех",
                command=lambda p_ix=p_idx: self.controller.on_auto_marker_pos_all(p_ix),
            )
            btn_auto_all.pack(side="left", padx=15)
            ToolTip(
                btn_auto_all, "Установить позиции всех меток этого файла по графику"
            )

            for m_idx, m in enumerate(p.markers):
                f_row = ttk.Frame(self.h_frame)
                f_row.pack(fill="x", pady=2, padx=(5, 0))

                # 1. Координаты привязки (Anchor)
                for k, w, step, tip in [
                    ("anchor_x", 7, x_step, "X привязки (на графике)"),
                    ("anchor_y", 7, y_step, "Y привязки (на графике)"),
                ]:
                    sp = tk.Spinbox(f_row, from_=-1e9, to=1e9, increment=step, width=w)
                    sp.config(
                        command=lambda p_ix=p_idx, m_ix=m_idx, key=k, s=sp: self.controller.update_marker(
                            p_ix, m_ix, key, s.get()
                        )
                    )
                    sp.delete(0, tk.END)
                    sp.insert(0, str(getattr(m, k)))
                    sp.pack(side="left", padx=1)
                    sp.bind(
                        "<Return>",
                        lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: [
                            self.controller.update_marker(p_ix, m_ix, key, s.get()),
                            self.focus_set(),
                        ],
                    )
                    sp.bind(
                        "<FocusOut>",
                        lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: self.controller.update_marker(
                            p_ix, m_ix, key, s.get()
                        ),
                    )
                    ToolTip(sp, tip)

                # Кнопка Авто для конкретной метки
                btn_auto = ttk.Button(
                    f_row,
                    text="Авто",
                    width=4,
                    command=lambda p_ix=p_idx, m_ix=m_idx: self.controller.on_auto_marker_pos(
                        p_ix, m_ix
                    ),
                )
                btn_auto.pack(side="left", padx=(1, 5))
                ToolTip(btn_auto, "Найти Y на графике по заданному X привязки")

                # 2. Координаты текста (Label)
                for k, w, step, tip in [
                    ("label_x", 7, x_step, "X текста"),
                    ("label_y", 7, y_step, "Y текста"),
                ]:
                    sp = tk.Spinbox(f_row, from_=-1e9, to=1e9, increment=step, width=w)
                    sp.config(
                        command=lambda p_ix=p_idx, m_ix=m_idx, key=k, s=sp: self.controller.update_marker(
                            p_ix, m_ix, key, s.get()
                        )
                    )
                    sp.delete(0, tk.END)
                    sp.insert(0, str(getattr(m, k)))
                    sp.pack(side="left", padx=1)
                    sp.bind(
                        "<Return>",
                        lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: [
                            self.controller.update_marker(p_ix, m_ix, key, s.get()),
                            self.focus_set(),
                        ],
                    )
                    sp.bind(
                        "<FocusOut>",
                        lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp: self.controller.update_marker(
                            p_ix, m_ix, key, s.get()
                        ),
                    )
                    ToolTip(sp, tip)

                # 3. Текст метки
                e_txt = ttk.Entry(f_row, width=10)
                e_txt.insert(0, m.text)
                e_txt.pack(side="left", padx=(5, 1))
                e_txt.bind(
                    "<KeyRelease>",
                    lambda ev, p_ix=p_idx, m_ix=m_idx, en=e_txt: self.controller.update_marker(
                        p_ix, m_ix, "text", en.get()
                    ),
                )
                ToolTip(e_txt, "Текст метки")

                # 4. Размер шрифта и угол поворота
                for k, w, step, tip in [
                    ("font_size", 3, 1, "Размер шрифта"),
                    ("label_rotation", 4, 15, "Угол поворота текста"),
                ]:
                    sp_o = tk.Spinbox(
                        f_row, from_=-1e9, to=1e9, increment=step, width=w
                    )
                    sp_o.config(
                        command=lambda p_ix=p_idx, m_ix=m_idx, key=k, s=sp_o: self.controller.update_marker(
                            p_ix, m_ix, key, s.get()
                        )
                    )
                    sp_o.delete(0, tk.END)
                    sp_o.insert(0, str(getattr(m, k)))
                    sp_o.pack(side="left", padx=1)
                    sp_o.bind(
                        "<Return>",
                        lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp_o: [
                            self.controller.update_marker(p_ix, m_ix, key, s.get()),
                            self.focus_set(),
                        ],
                    )
                    sp_o.bind(
                        "<FocusOut>",
                        lambda ev, p_ix=p_idx, m_ix=m_idx, key=k, s=sp_o: self.controller.update_marker(
                            p_ix, m_ix, key, s.get()
                        ),
                    )
                    ToolTip(sp_o, tip)

                # 5. Линия связи (Connector)
                cb_conn_var = tk.BooleanVar(
                    self, value=getattr(m, "show_connector", False)
                )
                self.marker_vars.append(cb_conn_var)
                cb_conn = ttk.Checkbutton(
                    f_row,
                    text="Связь",
                    variable=cb_conn_var,
                    command=lambda p_ix=p_idx, m_ix=m_idx, v=cb_conn_var: self.controller.update_marker(
                        p_ix, m_ix, "show_connector", v.get()
                    ),
                )
                cb_conn.pack(side="left", padx=(5, 1))
                ToolTip(
                    cb_conn, "Показывать линию связи между текстом и точкой привязки"
                )

                # Толщина линии связи
                sp_w = tk.Spinbox(f_row, from_=0.0, to=10.0, increment=0.1, width=4)
                sp_w.config(
                    command=lambda p_ix=p_idx, m_ix=m_idx, s=sp_w: self.controller.update_marker(
                        p_ix, m_ix, "width", s.get()
                    )
                )
                sp_w.delete(0, tk.END)
                sp_w.insert(0, str(m.width))
                sp_w.pack(side="left", padx=1)
                sp_w.bind(
                    "<Return>",
                    lambda ev, p_ix=p_idx, m_ix=m_idx, s=sp_w: [
                        self.controller.update_marker(p_ix, m_ix, "width", s.get()),
                        self.focus_set(),
                    ],
                )
                sp_w.bind(
                    "<FocusOut>",
                    lambda ev, p_ix=p_idx, m_ix=m_idx, s=sp_w: self.controller.update_marker(
                        p_ix, m_ix, "width", s.get()
                    ),
                )
                ToolTip(sp_w, "Толщина линии связи")

                # 6. Слой
                cb_l = ttk.Combobox(
                    f_row, values=["Задний", "Передний"], width=8, state="readonly"
                )
                cb_l.set(m.layer)
                cb_l.pack(side="left", padx=(5, 1))
                cb_l.bind(
                    "<<ComboboxSelected>>",
                    lambda e, p_ix=p_idx, m_ix=m_idx, c=cb_l: self.controller.update_marker(
                        p_ix, m_ix, "layer", c.get()
                    ),
                )
                ToolTip(cb_l, "Слой отрисовки")

                # 7. Цвет
                btn_c = tk.Button(
                    f_row,
                    bg=m.color,
                    width=2,
                    relief="flat",
                    command=lambda p_ix=p_idx, m_ix=m_idx: self.controller.show_color_picker(
                        p_ix, is_marker=True, marker_idx=m_ix
                    ),
                )
                btn_c.pack(side="left", padx=2)
                ToolTip(btn_c, "Цвет текста и линии связи")

                # 8. Удаление
                ttk.Button(
                    f_row,
                    text="🗑️",
                    width=3,
                    command=lambda p_ix=p_idx, m_ix=m_idx: self.controller.on_remove_marker(
                        p_ix, m_ix
                    ),
                ).pack(side="right")

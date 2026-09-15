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

        ttk.Button(
            f_btns, text="➕ Добавить файлы", command=self.controller.on_add_files
        ).pack(side="left", padx=5)
        ttk.Button(
            f_btns, text="🗑️ Очистить всё", command=self.controller.on_clear_all
        ).pack(side="left", padx=5)
        ttk.Button(
            f_btns,
            text="💾 Экспорт настроек",
            command=self.controller.on_export_file_settings,
        ).pack(side="left", padx=5)
        ttk.Button(
            f_btns,
            text="📂 Импорт настроек",
            command=self.controller.on_import_file_settings,
        ).pack(side="left", padx=5)

        self.f_canvas = tk.Canvas(self)
        self.f_scroll = ttk.Scrollbar(
            self, orient="vertical", command=self.f_canvas.yview
        )
        self.f_frame = ttk.Frame(self.f_canvas)

        self.f_frame.bind(
            "<Configure>",
            lambda e: self.f_canvas.configure(scrollregion=self.f_canvas.bbox("all")),
        )
        self.f_canvas.create_window((0, 0), window=self.f_frame, anchor="nw")
        self.f_canvas.configure(yscrollcommand=self.f_scroll.set)

        self.f_canvas.pack(side="left", fill="both", expand=True)
        self.f_scroll.pack(side="right", fill="y")

    def update_list(self, plots: List[PlotItem]) -> None:
        """Перерисовывает список файлов на основе актуальных данных."""
        for w in self.f_frame.winfo_children():
            w.destroy()

        # Создаем список для хранения переменных, чтобы их не удалил сборщик мусора
        self.plot_vars = []

        for idx, item in enumerate(plots):
            f = ttk.Frame(self.f_frame)
            f.pack(fill="x", pady=2, padx=5)

            # 1. Слой (перемещение)
            btn_up = ttk.Button(
                f,
                text="↑",
                width=2,
                command=lambda ix=idx: self.controller.on_move_plot(ix, -1),
            )
            btn_up.pack(side="left")
            ToolTip(btn_up, "Переместить выше в списке (на задний план)")

            btn_down = ttk.Button(
                f,
                text="↓",
                width=2,
                command=lambda ix=idx: self.controller.on_move_plot(ix, 1),
            )
            btn_down.pack(side="left", padx=(0, 5))
            ToolTip(btn_down, "Переместить ниже в списке (на передний план)")

            # 2. Видимость
            vis_v = tk.BooleanVar(self, value=item.visible)
            self.plot_vars.append(vis_v)
            cb_vis = ttk.Checkbutton(
                f,
                variable=vis_v,
                command=lambda ix=idx, v=vis_v: self.controller.update_plot(
                    ix, "visible", v.get()
                ),
            )
            cb_vis.pack(side="left", padx=7)
            ToolTip(cb_vis, "Отображать график")

            # 3. Цвет
            btn_c = tk.Button(
                f,
                bg=item.color,
                width=2,
                relief="flat",
                command=lambda ix=idx: self.controller.show_color_picker(
                    ix, is_marker=False
                ),
            )
            btn_c.pack(side="left", padx=2)
            ToolTip(btn_c, "Цвет графика")

            # 4. Стиль линии
            cb_style = ttk.Combobox(
                f, values=["-", "--", ":", "-."], width=3, state="readonly"
            )
            cb_style.set(item.linestyle)
            cb_style.pack(side="left", padx=2)
            cb_style.bind(
                "<<ComboboxSelected>>",
                lambda e, ix=idx, c=cb_style: self.controller.update_plot(
                    ix, "linestyle", c.get()
                ),
            )
            ToolTip(cb_style, "Стиль линии")

            # 5. Толщина линии
            sp_w = tk.Spinbox(f, from_=0.1, to=10, increment=0.1, width=4)
            sp_w.config(
                command=lambda ix=idx, s=sp_w: self.controller.update_plot(
                    ix, "line_width", s.get()
                )
            )
            sp_w.delete(0, tk.END)
            sp_w.insert(0, f"{item.line_width:.1f}")
            sp_w.pack(side="left", padx=2)
            sp_w.bind(
                "<Return>",
                lambda e, ix=idx, s=sp_w: [
                    self.controller.update_plot(ix, "line_width", s.get()),
                    self.focus_set(),
                ],
            )
            sp_w.bind(
                "<FocusOut>",
                lambda e, ix=idx, s=sp_w: self.controller.update_plot(
                    ix, "line_width", s.get()
                ),
            )
            ToolTip(sp_w, "Толщина линии")

            # 6. Смещение по X
            sp_x = tk.Spinbox(f, from_=-1e9, to=1e9, increment=0.1, width=5)
            sp_x.config(
                command=lambda ix=idx, s=sp_x: self.controller.update_plot(
                    ix, "x_offset", s.get()
                )
            )
            sp_x.delete(0, tk.END)
            sp_x.insert(0, f"{item.x_offset:.2f}")
            sp_x.pack(side="left", padx=2)
            sp_x.bind(
                "<Return>",
                lambda e, ix=idx, s=sp_x: [
                    self.controller.update_plot(ix, "x_offset", s.get()),
                    self.focus_set(),
                ],
            )
            sp_x.bind(
                "<FocusOut>",
                lambda e, ix=idx, s=sp_x: self.controller.update_plot(
                    ix, "x_offset", s.get()
                ),
            )
            ToolTip(sp_x, "Смещение по оси X (Время)")

            # 7. Смещение по Y
            sp_y = tk.Spinbox(f, from_=-1e12, to=1e12, increment=10, width=6)
            sp_y.config(
                command=lambda ix=idx, s=sp_y: self.controller.update_plot(
                    ix, "y_offset", s.get()
                )
            )
            sp_y.delete(0, tk.END)
            sp_y.insert(0, f"{item.y_offset:.2f}")
            sp_y.pack(side="left", padx=2)
            sp_y.bind(
                "<Return>",
                lambda e, ix=idx, s=sp_y: [
                    self.controller.update_plot(ix, "y_offset", s.get()),
                    self.focus_set(),
                ],
            )
            sp_y.bind(
                "<FocusOut>",
                lambda e, ix=idx, s=sp_y: self.controller.update_plot(
                    ix, "y_offset", s.get()
                ),
            )
            ToolTip(sp_y, "Смещение по оси Y (Интенсивность)")

            # 8. Легенда
            leg_v = tk.BooleanVar(self, value=item.show_in_legend)
            self.plot_vars.append(leg_v)
            cb_leg = ttk.Checkbutton(
                f,
                variable=leg_v,
                command=lambda ix=idx, v=leg_v: self.controller.update_plot(
                    ix, "show_in_legend", v.get()
                ),
            )
            cb_leg.pack(side="left", padx=5)
            ToolTip(cb_leg, "Показывать в легенде")

            # 9. Удаление
            btn_del = ttk.Button(
                f,
                text="🗑️",
                width=3,
                command=lambda ix=idx: self.controller.on_remove_plot(ix),
            )
            btn_del.pack(side="right", padx=2)
            ToolTip(btn_del, "Удалить файл")

            # 10. Название
            ent = ttk.Entry(f)
            ent.insert(0, item.label)
            ent.pack(side="left", fill="x", expand=True)
            ent.bind(
                "<KeyRelease>",
                lambda e, ix=idx, en=ent: self.controller.update_plot(
                    ix, "label", en.get()
                ),
            )
            ToolTip(ent, "Имя графика (отображается в легенде)")

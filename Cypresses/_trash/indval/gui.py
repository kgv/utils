"""
Модуль графического интерфейса пользователя (GUI).
Реализован на базе Tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Any, Callable, Dict

import Cypresses._trash.indval.config as config


class AppGUI:
    def __init__(
        self, root: tk.Tk, run_callback: Callable[[Dict[str, Any]], None]
    ) -> None:
        self.root = root
        self.root.title("Ordination & Statistics Settings")
        self.root.geometry("512x450")
        self.run_callback = run_callback

        self.frame_controls = tk.Frame(self.root, padx=20, pady=20)
        self.frame_controls.pack(fill=tk.BOTH, expand=True)

        self.comboboxes: Dict[str, ttk.Combobox] = {}

        self._create_combobox("analysis_type", config.ANALYSIS_TYPES, default_idx=0)
        self._create_combobox("transform", config.TRANSFORM_METHODS, default_idx=1)
        self._create_combobox("distance", config.DISTANCE_METRICS, default_idx=0)
        self._create_combobox("taxonomy", config.TAXONOMY_LEVELS, default_idx=1)
        self._create_combobox("n_init", config.N_INIT_VALUES, default_idx=1)
        self._create_combobox("max_iter", config.MAX_ITER_VALUES, default_idx=1)
        self._create_combobox("seed", config.SEED_VALUES, default_idx=0, state="normal")

        self.btn_run = tk.Button(
            self.frame_controls,
            text="Запустить анализ и построить график",
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            command=self._on_run_clicked,
        )
        self.btn_run.pack(pady=20, fill=tk.X)

    def _create_combobox(
        self,
        name: str,
        values: list[str],
        default_idx: int = 0,
        state: str = "readonly",
    ) -> None:
        frame = tk.Frame(self.frame_controls)
        frame.pack(fill=tk.X, pady=5)

        tk.Label(frame, text=f"{name}:", font=("Arial", 12), width=20, anchor="w").pack(
            side=tk.LEFT
        )

        combo = ttk.Combobox(frame, values=values, state=state, font=("Arial", 12))
        combo.current(default_idx)
        combo.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.comboboxes[name] = combo

    def _on_run_clicked(self) -> None:
        try:
            params = {
                "analysis_type": self.comboboxes["analysis_type"].get(),
                "transform": self.comboboxes["transform"].get(),
                "distance": self.comboboxes["distance"].get(),
                "taxonomy": self.comboboxes["taxonomy"].get(),
                "n_init": int(self.comboboxes["n_init"].get()),
                "max_iter": int(self.comboboxes["max_iter"].get()),
                "seed": int(self.comboboxes["seed"].get()),
            }
            self.run_callback(params)
        except ValueError as e:
            messagebox.showerror(
                "Ошибка ввода", f"Проверьте правильность числовых параметров.\n{e}"
            )

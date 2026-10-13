"""
Главный модуль приложения.
Связывает загрузку данных, графический интерфейс, анализ и визуализацию.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict

import Cypresses._trash.indval.config as config
from Cypresses._trash.indval.loader import DataLoader
from Cypresses._trash.indval.analyzer import Analyzer
from Cypresses._trash.indval.visualizer import Visualizer
from Cypresses._trash.indval.gui import AppGUI


def main() -> None:
    data_loader = DataLoader(config.DATA_FILE_PATH)
    if not data_loader.load_and_prepare_data():
        print(
            "Критическая ошибка: Не удалось загрузить данные. Проверьте путь к файлу."
        )
        return

    analyzer = Analyzer()
    visualizer = Visualizer()

    def handle_run_analysis(params: Dict[str, Any]) -> None:
        try:
            x_raw = data_loader.get_features()
            y_labels = data_loader.get_taxonomy_labels(params["taxonomy"])
            feature_names = data_loader.get_feature_names()
            hover_labels = data_loader.get_hover_labels()

            result = analyzer.run_full_analysis(
                analysis_type=params["analysis_type"],
                x_raw=x_raw,
                y_labels=y_labels,
                feature_names=feature_names,
                transform_method=params["transform"],
                distance_metric=params["distance"],
                n_init=params["n_init"],
                max_iter=params["max_iter"],
                seed=params["seed"],
            )

            if result is None:
                messagebox.showerror("Ошибка анализа", "Произошла ошибка при расчетах.")
                return

            visualizer.plot_ordination(
                analysis_type=params["analysis_type"],
                coords=result.coords,
                taxonomy_labels=y_labels,
                hover_labels=hover_labels,
                taxonomy_name=params["taxonomy"],
                distance_metric=params["distance"],
                transform_method=params["transform"],
                metric_val=result.stress_or_variance,
            )

        except Exception as e:
            messagebox.showerror(
                "Непредвиденная ошибка", f"Произошла ошибка во время выполнения:\n{e}"
            )

    root = tk.Tk()
    app = AppGUI(root, run_callback=handle_run_analysis)
    root.protocol("WM_DELETE_WINDOW", root.destroy)
    root.mainloop()


if __name__ == "__main__":
    main()

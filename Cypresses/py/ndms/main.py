"""
Главный модуль приложения.
Связывает загрузку данных, графический интерфейс, анализ и визуализацию.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Any, Dict

import Cypresses.py.ndms.config as config
from Cypresses.py.ndms.loader import DataLoader
from Cypresses.py.ndms.analyzer import Analyzer
from Cypresses.py.ndms.visualizer import Visualizer
from Cypresses.py.ndms.gui import AppGUI


def main() -> None:
    """
    Точка входа в приложение. Инициализирует компоненты и запускает главный цикл.
    """
    # 1. Инициализация и загрузка данных
    data_loader = DataLoader(config.DATA_FILE_PATH)
    if not data_loader.load_and_prepare_data():
        # Если данные не загрузились, показываем ошибку в консоли (или можно через tk.messagebox)
        print(
            "Критическая ошибка: Не удалось загрузить данные. Проверьте путь к файлу."
        )
        return

    # 2. Инициализация бизнес-логики
    analyzer = Analyzer()
    visualizer = Visualizer()

    # 3. Функция-контроллер, которая будет вызвана из GUI
    def handle_run_analysis(params: Dict[str, Any]) -> None:
        """
        Получает параметры из GUI, запрашивает данные, проводит анализ и строит график.
        """
        try:
            # Получаем нужные срезы данных
            x_raw = data_loader.get_features()
            y_labels = data_loader.get_taxonomy_labels(params["taxonomy"])
            hover_labels = data_loader.get_hover_labels()

            # Запускаем анализ
            result = analyzer.run_full_analysis(
                x_raw=x_raw,
                y_labels=y_labels,
                transform_method=params["transform"],
                distance_metric=params["distance"],
                n_init=params["n_init"],
                max_iter=params["max_iter"],
                seed=params["seed"],
            )

            if result is None:
                messagebox.showerror(
                    "Ошибка анализа", "Произошла ошибка при расчете дистанций или NMDS."
                )
                return

            # Запускаем визуализацию
            visualizer.plot_nmds(
                coords=result.nmds_coords,
                taxonomy_labels=y_labels,
                hover_labels=hover_labels,
                taxonomy_name=params["taxonomy"],
                distance_metric=params["distance"],
                transform_method=params["transform"],
                stress=result.stress,
            )

        except Exception as e:
            messagebox.showerror(
                "Непредвиденная ошибка", f"Произошла ошибка во время выполнения:\n{e}"
            )

    # 4. Запуск графического интерфейса
    root = tk.Tk()
    app = AppGUI(root, run_callback=handle_run_analysis)

    # Перехват закрытия окна (опционально, для корректного завершения)
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    root.mainloop()


if __name__ == "__main__":
    main()

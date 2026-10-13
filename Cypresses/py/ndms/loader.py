"""
Модуль для загрузки и предварительной обработки данных.
Использует библиотеку Polars для высокопроизводительной работы с таблицами.
"""

import logging
import numpy as np
import polars as pl
from typing import List, Tuple

import Cypresses.py.ndms.config as config

# Настройка базового логирования
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class DataLoader:
    """
    Класс для загрузки, трансформации и хранения данных о растениях.
    """

    def __init__(self, filepath: str) -> None:
        """
        Инициализирует загрузчик данных.

        :param filepath: Путь к файлу с данными (CSV/TXT).
        """
        self.filepath: str = filepath
        self.df: pl.DataFrame | None = None
        self.features_matrix: np.ndarray | None = None
        self.hover_labels: np.ndarray | None = None

    def load_and_prepare_data(self) -> bool:
        """
        Считывает данные из файла, формирует новые колонки и матрицу признаков.

        :return: True, если данные успешно загружены, иначе False.
        """
        try:
            # Чтение данных с переопределением схемы
            raw_df = pl.read_csv(
                self.filepath,
                schema_overrides={
                    col: pl.String if t == str else pl.Int64
                    for col, t in config.SCHEMA_OVERRIDES.items()
                },
            )

            # Формирование составных колонок Species и Variety
            self.df = raw_df.with_columns(
                [
                    pl.concat_str(
                        [pl.col("Genus"), pl.col("Species")],
                        separator=" ",
                        ignore_nulls=True,
                    ).alias("Species"),
                    pl.concat_str(
                        [pl.col("Genus"), pl.col("Species"), pl.col("Variety")],
                        separator=" ",
                        ignore_nulls=True,
                    ).alias("Variety"),
                ]
            )

            # Выделение числовых признаков (удаление метаданных и заполнение null)
            clean_df = self.df.select(
                pl.all().exclude(config.META_COLUMNS).fill_null(0.0)
            )
            self.features_matrix = clean_df.to_numpy()

            # Генерация подписей для графиков
            self._generate_hover_labels()

            logging.info("Данные успешно загружены и обработаны!")
            return True

        except FileNotFoundError:
            logging.error(f"Файл не найден: {self.filepath}")
            return False
        except Exception as e:
            logging.error(f"Ошибка при загрузке данных: {e}")
            return False

    def _generate_hover_labels(self) -> None:
        """
        Генерирует массив строк для всплывающих подсказок на графике.
        """
        if self.df is None:
            return

        labels: List[str] = [
            f"{row['Variety']} {row['Identifier']} (Tree: {row['Tree']}, Vial: {row['Vial']})"
            for row in self.df.to_dicts()
        ]
        self.hover_labels = np.array(labels)

    def get_taxonomy_labels(self, taxonomy_level: str) -> np.ndarray:
        """
        Возвращает массив меток для выбранного уровня таксономии.

        :param taxonomy_level: Название колонки (например, 'Genus', 'Species').
        :return: Numpy массив со значениями таксономии.
        :raises ValueError: Если данные не загружены или колонка отсутствует.
        """
        if self.df is None:
            raise ValueError(
                "Данные еще не загружены. Вызовите load_and_prepare_data()."
            )

        if taxonomy_level not in self.df.columns:
            raise ValueError(
                f"Уровень таксономии '{taxonomy_level}' не найден в данных."
            )

        return self.df[taxonomy_level].to_numpy()

    def get_features(self) -> np.ndarray:
        """
        Возвращает матрицу признаков (X).

        :return: Numpy массив с числовыми данными.
        :raises ValueError: Если данные не загружены.
        """
        if self.features_matrix is None:
            raise ValueError("Матрица признаков не инициализирована.")
        return self.features_matrix

    def get_hover_labels(self) -> np.ndarray:
        """
        Возвращает массив подписей для точек.

        :return: Numpy массив строк.
        :raises ValueError: Если данные не загружены.
        """
        if self.hover_labels is None:
            raise ValueError("Подписи не инициализированы.")
        return self.hover_labels

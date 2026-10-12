"""
Модуль для загрузки и предварительной обработки данных.
Использует библиотеку Polars для высокопроизводительной работы с таблицами.
"""

import logging
import numpy as np
import polars as pl
from typing import List

import config

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


class DataLoader:
    def __init__(self, filepath: str) -> None:
        self.filepath: str = filepath
        self.df: pl.DataFrame | None = None
        self.features_matrix: np.ndarray | None = None
        self.feature_names: List[str] | None = None
        self.hover_labels: np.ndarray | None = None

    def load_and_prepare_data(self) -> bool:
        try:
            raw_df = pl.read_csv(
                self.filepath,
                schema_overrides={
                    col: pl.String if t == str else pl.Int64
                    for col, t in config.SCHEMA_OVERRIDES.items()
                },
            )

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

            clean_df = self.df.select(
                pl.all().exclude(config.META_COLUMNS).fill_null(0.0)
            )
            self.features_matrix = clean_df.to_numpy()
            self.feature_names = clean_df.columns  # Сохраняем названия видов

            self._generate_hover_labels()
            logging.info("Данные успешно загружены и обработаны!")
            return True

        except Exception as e:
            logging.error(f"Ошибка при загрузке данных: {e}")
            return False

    def _generate_hover_labels(self) -> None:
        if self.df is None:
            return
        labels = [
            f"{row['Variety']} {row['Identifier']} (Tree: {row['Tree']}, Vial: {row['Vial']})"
            for row in self.df.to_dicts()
        ]
        self.hover_labels = np.array(labels)

    def get_taxonomy_labels(self, taxonomy_level: str) -> np.ndarray:
        if self.df is None or taxonomy_level not in self.df.columns:
            raise ValueError(f"Уровень таксономии '{taxonomy_level}' не найден.")
        return self.df[taxonomy_level].to_numpy()

    def get_features(self) -> np.ndarray:
        if self.features_matrix is None:
            raise ValueError("Матрица не инициализирована.")
        return self.features_matrix

    def get_feature_names(self) -> List[str]:
        if self.feature_names is None:
            raise ValueError("Имена признаков не инициализированы.")
        return self.feature_names

    def get_hover_labels(self) -> np.ndarray:
        if self.hover_labels is None:
            raise ValueError("Подписи не инициализированы.")
        return self.hover_labels

"""
Модуль для проведения математического и статистического анализа данных.
Включает расчет дистанций, тесты ANOSIM/PERMANOVA и NMDS ординацию.
"""

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import DistanceMatrix, anosim, permanova
from sklearn.manifold import MDS
from typing import Optional

import Cypresses.py.ndms.config as config


@dataclass
class AnalysisResult:
    """
    Структура данных для хранения результатов анализа.
    """

    nmds_coords: np.ndarray
    stress: float
    anosim_summary: pd.Series
    permanova_summary: pd.Series


class Analyzer:
    """
    Класс, инкапсулирующий логику статистического анализа и ординации.
    """

    @staticmethod
    def transform_data(x_raw: np.ndarray, method: str) -> np.ndarray:
        """
        Применяет выбранный метод трансформации к сырым данным.

        :param x_raw: Исходная матрица признаков.
        :param method: Название метода трансформации (например, 'log1p').
        :return: Трансформированная матрица признаков.
        """
        if method == "log1p":
            return np.log1p(x_raw)
        return x_raw

    def run_full_analysis(
        self,
        x_raw: np.ndarray,
        y_labels: np.ndarray,
        transform_method: str,
        distance_metric: str,
        n_init: int,
        max_iter: int,
        seed: int,
    ) -> Optional[AnalysisResult]:
        """
        Выполняет полный цикл анализа: трансформация, расчет дистанций, статистика, NMDS.

        :param x_raw: Сырая матрица признаков.
        :param y_labels: Массив меток классов (таксономия).
        :param transform_method: Метод трансформации данных.
        :param distance_metric: Метрика расстояния.
        :param n_init: Количество инициализаций для NMDS.
        :param max_iter: Максимальное количество итераций для NMDS.
        :param seed: Random seed для воспроизводимости.
        :return: Объект AnalysisResult с результатами или None в случае ошибки.
        """
        # 1. Трансформация данных
        x_transformed = self.transform_data(x_raw, transform_method)

        # 2. Расчет матрицы расстояний
        try:
            dist_array = pdist(x_transformed, metric=distance_metric)
            dist_matrix = squareform(dist_array)
        except Exception as e:
            logging.error(f"Ошибка при расчете дистанции ({distance_metric}): {e}")
            return None

        # Преобразование в формат scikit-bio
        dm = DistanceMatrix(dist_matrix)
        grouping = list(y_labels)

        # 3. Статистические тесты
        logging.info("--- Результаты ANOSIM ---")
        anosim_res = anosim(dm, grouping, permutations=config.PERMUTATIONS_COUNT)
        logging.info(f"\n{anosim_res[['test statistic', 'p-value']]}")

        logging.info("--- Результаты PERMANOVA ---")
        permanova_res = permanova(dm, grouping, permutations=config.PERMUTATIONS_COUNT)
        logging.info(f"\n{permanova_res[['test statistic', 'p-value']]}")

        # 4. Ординация NMDS
        logging.info("--- Выполнение NMDS ординации ---")
        nmds = MDS(
            n_components=config.NMDS_COMPONENTS,
            metric="precomputed",
            metric_mds=False,
            init="random",
            normalized_stress="auto",
            n_init=n_init,
            max_iter=max_iter,
            eps=config.NMDS_EPSILON,
            random_state=seed,
        )
        nmds_coords = nmds.fit_transform(dist_matrix)
        logging.info(f"Final stress: {nmds.stress_:.4f}")

        return AnalysisResult(
            nmds_coords=nmds_coords,
            stress=nmds.stress_,
            anosim_summary=anosim_res,
            permanova_summary=permanova_res,
        )

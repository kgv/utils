"""
Модуль для проведения математического и статистического анализа данных.
Включает расчет дистанций, тесты ANOSIM/PERMANOVA, NMDS/PCA, IndVal и SIMPER.
"""

import logging
import numpy as np
import pandas as pd
from dataclasses import dataclass
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import DistanceMatrix, anosim, permanova
from sklearn.manifold import MDS
from sklearn.decomposition import PCA
from itertools import combinations
from typing import Optional, List

import config


@dataclass
class AnalysisResult:
    coords: np.ndarray
    stress_or_variance: float  # Для NMDS это stress, для PCA - explained variance
    anosim_summary: pd.Series
    permanova_summary: pd.Series


class Analyzer:
    @staticmethod
    def transform_data(x_raw: np.ndarray, method: str) -> np.ndarray:
        if method == "log1p":
            return np.log1p(x_raw)
        return x_raw

    def calculate_indval(
        self, x: np.ndarray, y: np.ndarray, feature_names: List[str]
    ) -> pd.DataFrame:
        """Расчет Indicator Value (IndVal) Дюфрена и Лежандра."""
        groups = np.unique(y)
        results = []

        for i, feature in enumerate(feature_names):
            feature_data = x[:, i]

            # A_ij (Специфичность): среднее обилие вида в группе / сумма средних обилий по всем группам
            mean_abundances = {g: np.mean(feature_data[y == g]) for g in groups}
            sum_mean_abundances = sum(mean_abundances.values())

            for g in groups:
                g_data = feature_data[y == g]
                a_ij = (
                    mean_abundances[g] / sum_mean_abundances
                    if sum_mean_abundances > 0
                    else 0
                )

                # B_ij (Верность): доля участков в группе, где вид присутствует
                b_ij = np.sum(g_data > 0) / len(g_data) if len(g_data) > 0 else 0

                indval = a_ij * b_ij
                if indval > 0:
                    results.append({"Feature": feature, "Group": g, "IndVal": indval})

        df = pd.DataFrame(results)
        if not df.empty:
            df = df.sort_values(by="IndVal", ascending=False)
        return df

    def calculate_simper(
        self, x: np.ndarray, y: np.ndarray, feature_names: List[str]
    ) -> dict:
        """Расчет Similarity Percentages (SIMPER) на основе расстояния Брея-Кертиса."""
        groups = np.unique(y)
        simper_results = {}

        for g1, g2 in combinations(groups, 2):
            data_g1 = x[y == g1]
            data_g2 = x[y == g2]

            contributions = np.zeros(x.shape[1])
            total_pairs = 0

            for row1 in data_g1:
                for row2 in data_g2:
                    denom = np.sum(row1 + row2)
                    if denom > 0:
                        contributions += np.abs(row1 - row2) / denom
                    total_pairs += 1

            if total_pairs > 0:
                avg_contributions = contributions / total_pairs
                # Сортируем признаки по вкладу
                indices = np.argsort(avg_contributions)[::-1]
                pair_res = [
                    (feature_names[i], avg_contributions[i])
                    for i in indices
                    if avg_contributions[i] > 0
                ]
                simper_results[f"{g1} vs {g2}"] = pair_res

        return simper_results

    def run_full_analysis(
        self,
        analysis_type: str,
        x_raw: np.ndarray,
        y_labels: np.ndarray,
        feature_names: List[str],
        transform_method: str,
        distance_metric: str,
        n_init: int,
        max_iter: int,
        seed: int,
    ) -> Optional[AnalysisResult]:

        x_transformed = self.transform_data(x_raw, transform_method)

        # --- IndVal и SIMPER ---
        logging.info("\n--- Результаты IndVal (Топ видов по группам) ---")
        indval_df = self.calculate_indval(x_transformed, y_labels, feature_names)
        for g in np.unique(y_labels):
            top_g = indval_df[indval_df["Group"] == g].head(config.TOP_N_FEATURES)
            logging.info(f"Группа {g}:\n{top_g.to_string(index=False)}\n")

        logging.info("--- Результаты SIMPER (Топ видов, определяющих различия) ---")
        simper_res = self.calculate_simper(x_transformed, y_labels, feature_names)
        for pair, features in simper_res.items():
            logging.info(f"Пара {pair}:")
            for feat, contrib in features[: config.TOP_N_FEATURES]:
                logging.info(f"  {feat}: {contrib:.4f}")
        logging.info("\n")

        # --- ANOSIM / PERMANOVA ---
        try:
            dist_array = pdist(x_transformed, metric=distance_metric)
            dist_matrix = squareform(dist_array)
        except Exception as e:
            logging.error(f"Ошибка при расчете дистанции ({distance_metric}): {e}")
            return None

        dm = DistanceMatrix(dist_matrix)
        grouping = list(y_labels)

        logging.info("--- Результаты ANOSIM ---")
        anosim_res = anosim(dm, grouping, permutations=config.PERMUTATIONS_COUNT)
        logging.info(f"\n{anosim_res[['test statistic', 'p-value']]}")

        logging.info("--- Результаты PERMANOVA ---")
        permanova_res = permanova(dm, grouping, permutations=config.PERMUTATIONS_COUNT)
        logging.info(f"\n{permanova_res[['test statistic', 'p-value']]}")

        # --- Ординация (NMDS или PCA) ---
        if analysis_type == "NMDS":
            logging.info("--- Выполнение NMDS ординации ---")
            nmds = MDS(
                n_components=config.ORDINATION_COMPONENTS,
                metric="precomputed",
                metric_mds=False,
                init="random",
                normalized_stress="auto",
                n_init=n_init,
                max_iter=max_iter,
                eps=config.NMDS_EPSILON,
                random_state=seed,
            )
            coords = nmds.fit_transform(dist_matrix)
            metric_val = nmds.stress_
            logging.info(f"Final stress: {metric_val:.4f}")

        elif analysis_type == "PCA":
            logging.info("--- Выполнение PCA ординации ---")
            pca = PCA(n_components=config.ORDINATION_COMPONENTS, random_state=seed)
            coords = pca.fit_transform(x_transformed)
            metric_val = sum(pca.explained_variance_ratio_)
            logging.info(f"Explained variance (2 components): {metric_val:.4f}")
        else:
            return None

        return AnalysisResult(
            coords=coords,
            stress_or_variance=metric_val,
            anosim_summary=anosim_res,
            permanova_summary=permanova_res,
        )

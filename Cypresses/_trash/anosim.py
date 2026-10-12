from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import DistanceMatrix, anosim, permanova
from sklearn.manifold import MDS
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import polars.selectors as selectors

# ==========================================
# 1. ЧТЕНИЕ И ПОДГОТОВКА ДАННЫХ (Ваш код)
# ==========================================
df = pl.read_csv(
    "Cypresses/_Wide.txt",
    schema_overrides={
        "Genus": pl.String,
        "Species": pl.String,
        "Variety": pl.String,
        "Identifier": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.String,
    },
)

clean_df = df.select(
    pl.all()
    .exclude(["Genus", "Species", "Variety", "Identifier", "Tree", "Vial"])
    .fill_null(0.0)
)
print(f"clean_df: {clean_df}")

# X = clean_df.to_numpy()
X = np.log1p(clean_df.to_numpy())
y = df["Species"].to_numpy()
features = clean_df.columns

# ==========================================
# 2. РАСЧЕТ МАТРИЦЫ РАССТОЯНИЙ (Брея-Кертиса)
# ==========================================
# В экологии (и в статье) стандартом является расстояние Брея-Кертиса
#
# - braycurtis
# - canberra
# - chebyshev
# - cityblock
# - correlation
# - cosine
# - euclidean
# - jensenshannon
# - mahalanobis
# - minkowski
# - seuclidean
# - sqeuclidean
dist_array = pdist(X, metric="braycurtis")  # 0.14670509985205316
# dist_array = pdist(X, metric="cosine")  # 0.14044414077061596
# dist_array = pdist(X, metric="correlation") # 0.1284462616921592
# dist_array = pdist(X, metric="euclidean") # 0.10734418551006265
# dist_array = pdist(X, metric="seuclidean") # 0.13257149130848048
dist_matrix = squareform(dist_array)

# Преобразуем в формат scikit-bio
dm = DistanceMatrix(dist_matrix)
grouping = list(y)

# ==========================================
# 3. СТАТИСТИЧЕСКИЕ ТЕСТЫ (ANOSIM и PERMANOVA)
# Аналог функций anosim() и adonis() из пакета vegan
# ANOSIM и PERMANOVA: Вычисляют статистическую значимость (p-value). Если p-value < 0.05, значит химический состав разных видов деревьев достоверно различается.
# ==========================================
print("--- 1. Результаты ANOSIM ---")
anosim_res = anosim(dm, grouping, permutations=999)
print(anosim_res[["test statistic", "p-value"]])
print("\n--- 2. Результаты PERMANOVA ---")
permanova_res = permanova(dm, grouping, permutations=999)
print(permanova_res[["test statistic", "p-value"]])

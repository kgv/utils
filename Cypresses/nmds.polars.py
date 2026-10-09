import polars as pl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from scipy.spatial.distance import pdist, squareform
from scipy.spatial import ConvexHull
from sklearn.manifold import MDS
from skbio.stats.distance import DistanceMatrix, anosim, permanova

# ==========================================
# 1. ЧТЕНИЕ И ПОДГОТОВКА ДАННЫХ (Ваш код)
# ==========================================
df = pl.read_csv(
    "TreeComponentWide.txt",
    schema_overrides={
        "Species": pl.String,
        "?": pl.String,
        "Object": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.String,
    },
)

clean_df = df.select(
    pl.all().exclude(["Species", "?", "Object", "Tree", "Vial"]).fill_null(0.0)
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
dist_array = pdist(X, metric="braycurtis") # 0.14670509985205316
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

# ==========================================
# 4. ОРДИНАЦИЯ NMDS И ВИЗУАЛИЗАЦИЯ (ordihull)
# Аналог metaMDS(), plot() и ordihull()
# ==========================================
print("\n--- 3. Выполнение NMDS ординации ---")
# metric=False делает шкалирование неметрическим (NMDS)
nmds = MDS(
    n_components=2,
    metric="precomputed",
    metric_mds=False,
    init="random",
    normalized_stress="auto",
    n_init=1000,  # 1000 Больше случайных стартов для поиска глобального минимума
    max_iter=1000,  # 1000 Больше итераций на каждый старт
    eps=1e-9,  # Более строгий критерий остановки (продолжать оптимизацию до упора)
    random_state=42,
)
nmds_coords = nmds.fit_transform(dist_matrix)
# 0 perfect
# 0.025 excellent
# 0.05 good
# 0.1 fair
# 0.2 poor
print(f"final_stress: {nmds.stress_}")

plt.figure(figsize=(10, 8))
unique_species = np.unique(y)
colors = matplotlib.colormaps.get_cmap("tab20")

for i, species in enumerate(unique_species):
    # Точки для конкретного вида дерева
    idx = np.where(y == species)[0]
    pts = nmds_coords[idx]

    # Рисуем точки
    plt.scatter(pts[:, 0], pts[:, 1], label=species, color=colors(i), s=50)

    # Если точек >= 3 - рисуем ordihull (выпуклую оболочку)
    if len(pts) > 2:
        hull = ConvexHull(pts)
        for simplex in hull.simplices:
            plt.plot(pts[simplex, 0], pts[simplex, 1], color=colors(i), lw=2, alpha=0.6)
        # Заливка оболочки
        plt.fill(
            pts[hull.vertices, 0], pts[hull.vertices, 1], color=colors(i), alpha=0.1
        )
    # Если ровно 2 точки - рисуем линию между ними
    elif len(pts) == 2:
        plt.plot(pts[:, 0], pts[:, 1], color=colors(i), lw=2, alpha=0.6)

plt.title("NMDS Ordination (Bray-Curtis) with ordihull")
plt.xlabel("NMDS1")
plt.ylabel("NMDS2")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()

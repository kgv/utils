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
        "Object": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.String,
    },
)

clean_df = df.select(
    pl.all().exclude(["Species", "Object", "Tree", "Vial"]).fill_null(0.0)
)

# X = clean_df.to_numpy()
X = np.log1p(clean_df.to_numpy())
y = df["Species"].to_numpy()
features = clean_df.columns

# ==========================================
# 2. РАСЧЕТ МАТРИЦЫ РАССТОЯНИЙ (Брея-Кертиса)
# ==========================================
# В экологии (и в статье) стандартом является расстояние Брея-Кертиса
#
# - "braycurtis"
# - "canberra"
# - "chebyshev"
# - "cityblock"
# - "correlation"
# - "cosine"
# - "dice"
# - "euclidean"
# - "hamming"
# - "jaccard"
# - "jensenshannon"
# - "mahalanobis"
# - "matching"
# - "minkowski"
# - "rogerstanimoto"
# - "russellrao"
# - "seuclidean"
# - "sokalsneath"
# - "sqeuclidean"
# - "yule"
# dist_array = pdist(X, metric="braycurtis") # 0.16191430499014675
dist_array = pdist(X, metric="cosine")  # 0.11964859856011284
# dist_array = pdist(X, metric="correlation") # 0.13331103104831807
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
    n_init=100,  # 1000 Больше случайных стартов для поиска глобального минимума
    max_iter=100,  # 1000 Больше итераций на каждый старт
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

    # Рисуем ordihull (выпуклую оболочку), если точек >= 3
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

# ==========================================
# 5. АНАЛИЗ ИНДИКАТОРНЫХ ВИДОВ (IndVal)
# Аналог multipatt() из пакета indicspecies
# ==========================================
print("\n--- 4. Анализ индикаторных компонентов (IndVal) ---")
# IndVal = Specificity (A) * Fidelity (B)
df_calc = pd.DataFrame(X, columns=features)
df_calc["Species"] = y

# A: Специфичность (Доля средней концентрации компонента в виде дерева от суммы средних по всем видам)
mean_abund = df_calc.groupby("Species").mean()
sum_mean_abund = mean_abund.sum(axis=0)
A = mean_abund / sum_mean_abund

# B: Верность (Доля деревьев данного вида, в которых компонент присутствует > 0)
presence = (df_calc.drop("Species", axis=1) > 0).astype(int)
presence["Species"] = y
B = presence.groupby("Species").mean()

# Итоговый индекс IndVal (от 0 до 1)
indval = A * B

# Выведем топ-3 индикаторных компонента для каждого вида дерева
for species in unique_species:
    top_components = indval.loc[species].sort_values(ascending=False).head(3)
    print(f"\nТоп индикаторы для {species}:")
    for comp, val in top_components.items():
        print(f"  - {comp}: IndVal = {val:.3f}")

# ==========================================
# 6. АНАЛИЗ SIMPER (Similarity Percentages)
# Аналог simper() из пакета vegan
# ==========================================
print("\n--- 5. Анализ SIMPER (Вклад в различия между парами) ---")


def calculate_simper(group1_name, group2_name):
    """Считает вклад каждого компонента в Брей-Кертис различие между двумя группами"""
    X1 = X[y == group1_name]
    X2 = X[y == group2_name]

    contributions = np.zeros(X.shape[1])
    total_bc = 0

    # Попарное сравнение всех деревьев из Группы 1 со всеми из Группы 2
    for i in range(X1.shape[0]):
        for j in range(X2.shape[0]):
            diff = np.abs(X1[i] - X2[j])
            summ = X1[i] + X2[j]
            sum_summ = np.sum(summ)
            if sum_summ > 0:
                contributions += diff / sum_summ
                total_bc += np.sum(diff / sum_summ)

    # Переводим в проценты
    simper_pct = (contributions / total_bc) * 100

    # Собираем в DataFrame
    res = pd.DataFrame(
        {"Component": features, "Contribution_%": simper_pct}
    ).sort_values("Contribution_%", ascending=False)

    return res


# Пример: сравним два первых уникальных вида дерева из вашего датасета
if len(unique_species) >= 2:
    sp1, sp2 = unique_species[0], unique_species[1]
    print(f"\nSIMPER: Что отличает '{sp1}' от '{sp2}'?")
    simper_res = calculate_simper(sp1, sp2)
    print(simper_res.head(5).to_string(index=False))

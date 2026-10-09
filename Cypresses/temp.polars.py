from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_selection import f_classif, chi2
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import cosine_distances
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances
from sklearn.preprocessing import normalize
import numpy as np
import polars as pl
import polars.selectors as cs

# Чтение данных
df = pl.read_csv(
    "TreeComponentWide.txt",
    schema_overrides={
        "Species": pl.String,
        "Object": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.String,
    },
)
print(f"read: {df}")

clean_df = df.select(
    pl.all()
    .exclude(
        [
            "Species",
            "Object",
            "Tree",
            "Vial",
        ]
    )
    .fill_null(0.0)
)
print(f"fill_null: {clean_df}")

# Извлекаем матрицу признаков (только компоненты) в формат NumPy
X = clean_df.to_numpy()
# Целевая переменная (виды деревьев)
Y = df["Species"].to_numpy()

# Метод А: ANOVA F-test (Дисперсионный анализ)
# Идеально для непрерывных данных. Проверяет, насколько сильно различаются
# средние значения компонента у разных видов деревьев.
f_scores, p_values_anova = f_classif(X, Y)
print(f"f_scores: {f_scores}; p_values_anova: {p_values_anova}")

# Метод Б: Тот самый Chi-square (Хи-квадрат)
# Работает, так как концентрации не бывают отрицательными (X >= 0).
# Оценивает статистическую зависимость между компонентом и видом.
chi2_scores, p_values_chi2 = chi2(X, Y)

# Метод В: Random Forest (Случайный лес) - Машинное обучение
# Строит множество деревьев решений и смотрит, какие компоненты
# чаще всего и эффективнее всего разделяют виды. (Самый надежный метод для сложных данных).
rf = RandomForestClassifier(
    n_estimators=1000,  # Увеличиваем количество деревьев до 1000 для максимальной стабильности
    random_state=42,
    class_weight="balanced",  # Заставляем алгоритм обращать равное внимание на редкие и частые виды деревьев
    n_jobs=-1,  # Используем все ядра процессора, чтобы 1000 деревьев посчитались мгновенно
)
rf.fit(X, Y)
rf_importances = rf.feature_importances_

# ==========================================
# 3. СОБИРАЕМ РЕЗУЛЬТАТЫ В POLARS
# ==========================================

importance_df = (
    pl.DataFrame(
        {
            "Component": clean_df.columns,
            "RF_Importance": rf_importances,
            "ANOVA_F": f_scores,
            "ANOVA_P": p_values_anova,
            "Chi2_Score": chi2_scores,
        }
    )
    .with_columns(
        cs.float().round(2)
        # Округляем для красоты
        # pl.col("RF_Importance").round(4),
        # pl.col("ANOVA_F").round(2),
        # pl.col("ANOVA_F").round(2),
        # pl.col("Chi2_Score").round(2),
    )
    .sort("RF_Importance", descending=True)
)  # Сортируем по важности от Случайного леса
print(importance_df)
importance_df.write_csv("importance_df.txt")

# # # Считаем попарное косинусное расстояние
# # dist_cosine = cosine_distances(X)
# # # Оборачиваем результат обратно в красивый Polars DataFrame
# # trees = df["Tree"].to_list()
# # distances_df = (
# #     pl.DataFrame(dist_cosine, schema=[f"{tree}" for tree in trees])
# #     .with_columns(pl.Series("Tree", trees))
# #     .select(["Tree", pl.all().exclude("Tree")])
# # )
# # print(distances_df)
# # distances_df.write_csv("tree_cosine_distances.txt")

# # А) Косинусное
# dist_cosine = cosine_distances(X)

# # Б) Брей-Кертис
# dist_braycurtis = pairwise_distances(X, metric='braycurtis')

# # В) Хеллингер (через L1-нормализацию и Евклида)
# X_norm = normalize(X, norm='l1')
# dist_hellinger = euclidean_distances(np.sqrt(X_norm)) / np.sqrt(2)

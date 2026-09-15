from sklearn.feature_selection import f_classif
from statsmodels.stats.multitest import multipletests
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
    pl.all().exclude(["Species", "Object", "Tree", "Vial"]).fill_null(0.0)
)
print(f"clean_df: {clean_df}")

# Извлекаем матрицу признаков (только компоненты) в формат NumPy
# Почему `log2` важно: Разница между 1 ppm и 10 ppm биологически так же важна, как между 100 ppm и 1000 ppm. Логарифм уравнивает эти масштабы.
X = np.log1p(clean_df.to_numpy())
# Целевая переменная (виды деревьев)
Y = df["Species"].to_numpy()

# ANOVA F-test (Дисперсионный анализ)  
# Проверяет, насколько сильно различаются средние значения компонента у разных
# видов деревьев.
f_statistic, p_values = f_classif(X, Y)
print(f"f_statistic: {f_statistic}; p_values : {p_values }")
# Коррекция p-value (FDR)
# Применяем поправку Бенджамини-Хохберга.
# Чтобы отсеять ложноположительные результаты из-за большого количества веществ.
reject, p_values_corrected, _, _ = multipletests(p_values, alpha=0.05, method="fdr_bh")

df = (
    pl.DataFrame(
        {
            "Component": clean_df.columns,
            "F": f_statistic,
            "_P": p_values,
            "P": p_values_corrected,
        }
    )
    .sort("P")
    .with_columns(
        pl.when(pl.col("P") < 0.001)
        .then(pl.lit("***"))
        .when(pl.col("P") < 0.01)
        .then(pl.lit("**"))
        .when(pl.col("P") < 0.05)
        .then(pl.lit("*"))
        .otherwise(pl.lit("ns"))
        .alias("Stars")
    )
    # .with_columns(cs.float().round(2))
)
print(df)
df.write_csv("Anova.txt")

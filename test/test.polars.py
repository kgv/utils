from pathlib import Path
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns

N = 3
CONTROL_LINE = "54 WT"

# 1. Чтение данных
df = pl.read_csv("test/Table1.csv")
print(df.head())

# Вычищаем лишние пробелы из заголовков
df = df.rename({col: col.strip() for col in df.columns})
print(df.head())

# Вычищаем пробелы из всех строковых колонок и приводим типы
df = df.with_columns(pl.col(pl.String()).str.strip_chars()).with_columns(
    pl.col("Day").cast(pl.Int64),
    pl.col("Mean").cast(pl.Float64),
    pl.col("StandardDeviation").cast(pl.Float64),
)
print(df.head())

lines = df["Line"].unique().sort().to_list()
print(f"lines: {lines}")

days = df["Day"].unique().sort().to_list()
print(f"days: {days}")

fatty_acids = df["FattyAcid"].unique().sort().to_list()
print(f"fatty_acids: {fatty_acids}")

# Отделяем контрольную группу
control = df.filter(pl.col("Line") == CONTROL_LINE)
print(f"control: {control}")

# Отделяем экспериментальные группы
experimental = df.filter(pl.col("Line") != CONTROL_LINE)
print(f"experimental: {experimental}")

# Объединяем линии с контролем
line_join = experimental.join(
    control.drop("Line"), on=["Day", "FattyAcid"], how="inner", suffix="_Control"
)
print(f"line_join: {line_join}")


# Функция для расчета статистики
def calc_stats(row):
    t_stat, p_val = ttest_ind_from_stats(
        mean1=row["Mean_Control"],
        std1=row["StandardDeviation_Control"],
        nobs1=N,
        mean2=row["Mean"],
        std2=row["StandardDeviation"],
        nobs2=N,
    )
    return {"p_value": p_val, "f_stat": t_stat**2}


def annotation(struct):
    p = struct["p_value"]
    f = struct["f_stat"]

    if p < 0.001:
        stars = "***"
    elif p < 0.01:
        stars = "**"
    elif p < 0.05:
        stars = "*"
    else:
        stars = "ns"

    p_text = "p<0.001" if p < 0.001 else f"p={p:.3f}"
    f_text = f"F={f:.2f}"

    return f"{stars}\n{p_text}\n{f_text}"


# Применяем расчет статистики
res = (
    line_join.with_columns(
        pl.struct(
            "Mean_Control", "StandardDeviation_Control", "Mean", "StandardDeviation"
        )
        .map_elements(
            calc_stats,
            return_dtype=pl.Struct(
                [pl.Field("p_value", pl.Float64), pl.Field("f_stat", pl.Float64)]
            ),
        )
        .struct.unnest()
    )
    .with_columns((-pl.col("p_value").log10()).alias("Log_p_value"))
    .with_columns(
        pl.struct("p_value", "f_stat")
        .map_elements(annotation, return_dtype=pl.String)
        .alias("Annotation")
    )
)
print(f"res: {res}")

# fig, axes = plot.subplots(1, 3, figsize=(19.2, 10.8), sharey=True)
fig, axes = plot.subplots(1, 3, figsize=(19.2, 6.4), sharey=True)

for i, day in enumerate(days):
    # Фильтруем данные для конкретного дня
    day_df = res.filter(pl.col("Day") == day)
    if day_df.is_empty():
        continue

    # Делаем Pivot средствами Polars и переводим в Pandas для Seaborn
    # index - строки, on - колонки, values - значения
    color = (
        day_df.pivot(values="Log_p_value", index="FattyAcid", on="Line")
        .to_pandas()
        .set_index("FattyAcid")
    )
    annot = (
        day_df.pivot(values="Annotation", index="FattyAcid", on="Line")
        .to_pandas()
        .set_index("FattyAcid")
    )

    print(f"--- Day {day} Annotations ---")
    print(annot)

    sns.heatmap(
        color,
        annot=annot,
        fmt="",
        cmap="Reds",
        ax=axes[i],
        cbar=(i == 2),
        vmin=0,
        vmax=3,
        cbar_kws={"label": "-log(p-value)"} if i == 2 else None,
        linewidths=1,
        linecolor="white",
    )

    axes[i].set_title(f"Day {day}", fontsize=14)
    axes[i].set_xlabel("", fontsize=14)
    if i == 0:
        axes[i].set_ylabel("Fatty acid", fontsize=14)
    else:
        axes[i].set_ylabel("")

plot.tight_layout()
plot.show()

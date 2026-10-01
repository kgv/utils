import polars as pl
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plot
import seaborn as sns

# ==========================================
# 1. ЧТЕНИЕ И ОЧИСТКА ДАННЫХ
# ==========================================
# Чтение CSV (Polars автоматически определяет типы, но мы читаем все как строки для очистки)
df = pl.read_csv("Mint/csv/Table1.csv", separator=",")

# Вычищаем лишние пробелы из заголовков
df = df.rename({col: col.strip() for col in df.columns})

# Вычищаем пробелы из всех строковых колонок и разбиваем "Mean±SD"
df = df.with_columns(
    # Убираем пробелы по краям у всех строковых колонок
    pl.col(pl.String).str.strip_chars()
).with_columns(
    # Разбиваем колонку Value по символу "±" и сразу кастуем во float
    pl.col("Value").str.split("±").list.get(0).cast(pl.Float64).alias("Mean"),
    pl.col("Value").str.split("±").list.get(1).cast(pl.Float64).alias("SD")
)

# ==========================================
# 2. СТАТИСТИКА (Идиоматичный Polars через JOIN)
# ==========================================
N_SAMPLES = 3
CONTROL_LINE = "54WT"

# Отделяем контрольную группу
ctrl_df = df.filter(pl.col("Line") == CONTROL_LINE).select(
    "Day", "Fatty acid",
    pl.col("Mean").alias("Mean_c"),
    pl.col("SD").alias("SD_c")
)

# Отделяем экспериментальные группы
exp_df = df.filter(pl.col("Line") != CONTROL_LINE).select(
    "Day", "Fatty acid", "Line",
    pl.col("Mean").alias("Mean_e"),
    pl.col("SD").alias("SD_e")
)

# Соединяем (Inner Join) экспериментальные данные с контролем по Дню и Кислоте.
# Это автоматически отфильтрует те случаи, где нет пары (заменяет проверки if empty).
res_df = exp_df.join(ctrl_df, on=["Day", "Fatty acid"], how="inner")

# Функция для расчета статистики (применяется к каждой строке)
def calc_stats(row):
    t_stat, p_val = ttest_ind_from_stats(
        mean1=row["Mean_c"], std1=row["SD_c"], nobs1=N_SAMPLES,
        mean2=row["Mean_e"], std2=row["SD_e"], nobs2=N_SAMPLES,
    )
    return {"p_value": p_val, "f_stat": t_stat**2}

# Применяем расчет статистики
res_df = res_df.with_columns(
    pl.struct("Mean_c", "SD_c", "Mean_e", "SD_e")
    .map_elements(
        calc_stats, 
        return_dtype=pl.Struct([pl.Field("p_value", pl.Float64), pl.Field("f_stat", pl.Float64)])
    )
    .alias("stats")
).unnest("stats") # Разворачиваем словарь в две отдельные колонки

# ==========================================
# 3. АННОТАЦИИ И ЛОГАРИФМИРОВАНИЕ
# ==========================================
def get_annotation(row):
    p = row["p_value"]
    f = row["f_stat"]

    if p is None or np.isnan(p):
        return ""

    if p < 0.001: stars = "***"
    elif p < 0.01: stars = "**"
    elif p < 0.05: stars = "*"
    else: stars = "ns"

    p_text = "p<0.001" if p < 0.001 else f"p={p:.3f}"
    f_text = f"F={f:.2f}"
    
    return f"{f_text}\n{p_text}\n({stars})"

res_df = res_df.with_columns(
    pl.struct("p_value", "f_stat")
    .map_elements(get_annotation, return_dtype=pl.String)
    .alias("Significance"),
    
    (-pl.col("p_value").log10()).alias("Log_P")
)

# ==========================================
# 4. ВИЗУАЛИЗАЦИЯ
# ==========================================
# Получаем отсортированный список уникальных дней
days = sorted(res_df["Day"].unique().to_list(), key=int)

fig, axes = plot.subplots(1, 3, figsize=(16, 6), sharey=True)

for i, day in enumerate(days):
    # Фильтруем данные для конкретного дня
    day_data = res_df.filter(pl.col("Day") == day)
    if day_data.is_empty():
        continue

    # Делаем Pivot средствами Polars и переводим в Pandas для Seaborn
    # index - строки, on - колонки, values - значения
    pivot_color = (
        day_data.pivot(values="Log_P", index="Fatty acid", on="Line")
        .to_pandas().set_index("Fatty acid")
    )
    pivot_annot = (
        day_data.pivot(values="Significance", index="Fatty acid", on="Line")
        .to_pandas().set_index("Fatty acid")
    )
    
    print(f"--- Day {day} Annotations ---")
    print(pivot_annot)

    sns.heatmap(
        pivot_color,
        annot=pivot_annot,
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
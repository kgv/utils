import polars as pl
import numpy as np
import scipy.stats as stats
from statsmodels.stats.multitest import multipletests
import seaborn as sns
import matplotlib.pyplot as plt

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
print(f"df: {df}")

# Исключаем внутренний стандарт
df = df.filter(pl.col("FattyAcid") != "17:0")

# Считаем log1p_ppm = ln(1 + ppm)
df = df.with_columns(log1p_ppm=pl.col("ppm").log1p())

# 2. Считаем среднее, дисперсию (var) и количество (count) для каждой группы
stats_df = df.group_by(["Week", "FattyAcid", "Ni"]).agg(
    mean=pl.col("log1p_ppm").mean(),
    var=pl.col("log1p_ppm").var(),
    count=pl.col("log1p_ppm").count(),
)

# 3. Выделяем контроль (Ni = 0) и переименовываем колонки
ctrl_stats = stats_df.filter(pl.col("Ni") == 0).select(
    pl.col("Week"),
    pl.col("FattyAcid"),
    pl.col("mean").alias("mean_ctrl"),
    pl.col("var").alias("var_ctrl"),
    pl.col("count").alias("count_ctrl"),
)

# 4. Соединяем опытные образцы (Ni > 0) с контролем
treat_stats = stats_df.filter(pl.col("Ni") != 0)
joined = treat_stats.join(ctrl_stats, on=["Week", "FattyAcid"], how="left")

# 5. Считаем Log2FC и промежуточные данные для Welch's t-test
# Log2FC = (ln(1+Treat) - ln(1+Ctrl)) / ln(2) = log2((1+Treat)/(1+Ctrl))
joined = joined.with_columns(
    Log2FC=(pl.col("mean") - pl.col("mean_ctrl")) / np.log(2),
    vn_treat=pl.col("var") / pl.col("count"),
    vn_ctrl=pl.col("var_ctrl") / pl.col("count_ctrl"),
)

# 6. Считаем t-статистику и степени свободы (degrees of freedom) чисто в Polars
joined = joined.with_columns(
    t_stat=(pl.col("mean") - pl.col("mean_ctrl"))
    / (pl.col("vn_treat") + pl.col("vn_ctrl")).sqrt(),
    df_num=(pl.col("vn_treat") + pl.col("vn_ctrl")) ** 2,
    df_den=(pl.col("vn_treat") ** 2 / (pl.col("count") - 1))
    + (pl.col("vn_ctrl") ** 2 / (pl.col("count_ctrl") - 1)),
).with_columns(dof=pl.col("df_num") / pl.col("df_den"))

# 7. Вычисляем p-value с помощью scipy (векторизованно, без циклов)
t_stat_arr = joined["t_stat"].to_numpy()
dof_arr = joined["dof"].to_numpy()
# sf - survival function (1 - cdf). Умножаем на 2 для двустороннего теста
p_val_arr = 2 * stats.t.sf(np.abs(t_stat_arr), dof_arr)

joined = joined.with_columns(p_value=pl.Series(p_val_arr))

# 8. Поправка на множественное тестирование (FDR Benjamini-Hochberg)
# Добавляем временный ID строки для безопасного join'а
joined = joined.with_row_index("id")

# Отбираем только те строки, где тест удался (нет NaN)
valid_mask = joined["p_value"].is_not_null() & ~joined["p_value"].is_nan()
valid_df = joined.filter(valid_mask)

if valid_df.height > 0:
    p_vals_valid = valid_df["p_value"].to_numpy()
    _, q_vals_valid, _, _ = multipletests(p_vals_valid, method="fdr_bh")

    # Возвращаем q_value обратно по ID
    valid_df = valid_df.with_columns(q_value=pl.Series(q_vals_valid)).select(
        ["id", "q_value"]
    )
    joined = joined.join(valid_df, on="id", how="left")
else:
    joined = joined.with_columns(q_value=pl.lit(None, dtype=pl.Float64))

joined = joined.drop("id")

# 9. Расставляем звездочки значимости
joined = joined.with_columns(
    Significance=pl.when(pl.col("q_value") < 0.001)
    .then(pl.lit("***"))
    .when(pl.col("q_value") < 0.01)
    .then(pl.lit("**"))
    .when(pl.col("q_value") < 0.05)
    .then(pl.lit("*"))
    .otherwise(pl.lit(""))
)

# ==========================================
# 2. ВИЗУАЛИЗАЦИЯ (Конвертация в Pandas)
# ==========================================

# Для построения графиков переводим итоговую агрегированную таблицу в Pandas
df_plot = joined.select(
    ["Week", "FattyAcid", "Ni", "Log2FC", "Significance"]
).to_pandas()

fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharey=True)
fig.suptitle(
    "Изменение профиля жирных кислот при стрессе (Ni), Log2FC (на базе log1p)",
    fontsize=16,
)

for i, week in enumerate([1, 5]):
    df_w = df_plot[df_plot["Week"] == week]

    if df_w.empty:
        continue

    # Создаем матрицы для Heatmap
    pivot_log2fc = df_w.pivot(index="FattyAcid", columns="Ni", values="Log2FC")
    pivot_sig = df_w.pivot(index="FattyAcid", columns="Ni", values="Significance")

    # Строим Heatmap
    sns.heatmap(
        pivot_log2fc,
        annot=pivot_sig,
        fmt="",
        cmap="vlag",
        center=0,
        vmin=-3,
        vmax=3,  # Настройте пределы шкалы под ваши данные
        ax=axes[i],
        cbar=(i == 1),
        linewidths=0.5,
        linecolor="gray",
    )

    axes[i].set_title(f"Неделя {week}", fontsize=14)
    axes[i].set_xlabel("Концентрация Ni (mM)", fontsize=12)
    if i == 0:
        axes[i].set_ylabel("Жирные кислоты", fontsize=12)
    else:
        axes[i].set_ylabel("")

plt.tight_layout()
plt.show()

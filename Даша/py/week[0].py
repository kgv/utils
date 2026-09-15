import polars as pl
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import seaborn as sns
import matplotlib.pyplot as plt

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
print(f"df: {df}")

# 1. Исключаем внутренний стандарт и считаем log1p_ppm = ln(1 + ppm)
df_calc = df.filter(pl.col("FattyAcid") != "17:0").with_columns(
    log1p_ppm=pl.col("ppm").log1p()
)

# 2. Группируем данные
df_agg = df_calc.group_by(["Ni", "Week", "FattyAcid"], maintain_order=True).agg(
    values=pl.col("log1p_ppm"),  # Собираем значения в список (для t-test)
    mean_val=pl.col("log1p_ppm").mean(),  # Среднее (для Log2FC)
)

# ==========================================
# НОВАЯ ЛОГИКА: Контроль = Неделя 1, Опыт = Неделя > 1
# ==========================================

# 3. Разделяем на контроль (Week = 1) и опыт (Week != 1)
df_ctrl = df_agg.filter(pl.col("Week") == 1).select(
    pl.col("Ni"),
    pl.col("FattyAcid"),
    pl.col("values").alias("ctrl_values"),
    pl.col("mean_val").alias("ctrl_mean"),
)

df_treat = df_agg.filter(pl.col("Week") != 1).select(
    pl.col("Ni"),
    pl.col("FattyAcid"),
    pl.col("Week"), # Оставляем колонку Week, так как опытных недель может быть несколько (например, 5)
    pl.col("values").alias("treat_values"),
    pl.col("mean_val").alias("treat_mean"),
)

# 4. Соединяем опыт с контролем (теперь объединяем по Ni и FattyAcid)
df_joined = df_treat.join(df_ctrl, on=["Ni", "FattyAcid"], how="left")

# 5. Считаем Log2FC (Изменение во времени: Неделя X относительно Недели 1)
df_joined = df_joined.with_columns(
    Log2FC=(pl.col("treat_mean") - pl.col("ctrl_mean")) / np.log(2)
)

# ==========================================
# 2. СТАТИСТИКА (SCIPY + STATSMODELS)
# ==========================================

treat_lists = df_joined["treat_values"].to_list()
ctrl_lists = df_joined["ctrl_values"].to_list()

p_values = []

for t_vals, c_vals in zip(treat_lists, ctrl_lists):
    t_clean = [x for x in t_vals if x is not None and not np.isnan(x)]
    c_clean = [x for x in c_vals if x is not None and not np.isnan(x)]

    if len(t_clean) >= 2 and len(c_clean) >= 2:
        stat, p = ttest_ind(t_clean, c_clean, equal_var=False)
        p_values.append(p)
    else:
        p_values.append(np.nan)

df_joined = df_joined.with_columns(p_value=pl.Series(p_values))

# FDR-поправка (для p-value)
# Применяем поправку Бенджамини-Хохберга.
# Чтобы отсеять ложноположительные результаты из-за большого количества веществ.
valid_mask = df_joined["p_value"].is_not_null() & ~df_joined["p_value"].is_nan()
df_valid = df_joined.filter(valid_mask)

if df_valid.height > 0:
    p_vals_valid = df_valid["p_value"].to_numpy()
    _, q_vals_valid, _, _ = multipletests(p_vals_valid, method="fdr_bh")

    df_valid = df_valid.with_columns(q_value=pl.Series(q_vals_valid))

    # Присоединяем обратно (ключи: Ni, FattyAcid, Week)
    df_joined = df_joined.join(
        df_valid.select(["Ni", "FattyAcid", "Week", "q_value"]),
        on=["Ni", "FattyAcid", "Week"],
        how="left",
        maintain_order="left_right",
    )
else:
    df_joined = df_joined.with_columns(q_value=pl.lit(None, dtype=pl.Float64))

# Расставляем звездочки
df_joined = df_joined.with_columns(
    Significance=pl.format(
        "{}\n{}",
        pl.when(pl.col("q_value") < 0.001).then(pl.lit("***"))
        .when(pl.col("q_value") < 0.01).then(pl.lit("**"))
        .when(pl.col("q_value") < 0.05).then(pl.lit("*"))
        .otherwise(pl.lit("")),
        pl.when(pl.col("q_value") < 0.001).then(pl.lit("p<0.001"))
        .otherwise(pl.col("q_value").round(3)),
    )
)

# ==========================================
# 3. ВИЗУАЛИЗАЦИЯ (PANDAS + SEABORN)
# ==========================================

df_plot = df_joined.select(
    ["Ni", "FattyAcid", "Week", "Log2FC", "Significance"]
).to_pandas()

# Узнаем, сколько у нас "опытных" недель (скорее всего только 5-я)
treat_weeks = df_plot["Week"].unique()

# Динамически создаем нужное количество графиков
fig, axes = plt.subplots(1, len(treat_weeks), figsize=(10 * len(treat_weeks), 8), sharey=True)

# Если график всего один, оборачиваем его в список для удобства цикла
if len(treat_weeks) == 1:
    axes = [axes]

fig.suptitle("Динамика изменения жирных кислот во времени (Неделя 5 vs Неделя 1)\nLog2FC, Welch's t-test, Benjamini/Hochberg", fontsize=16)

for i, week in enumerate(treat_weeks):
    df_w = df_plot[df_plot["Week"] == week]

    if df_w.empty:
        continue

    # 1. Извлекаем правильный порядок жирных кислот
    ordered_fa = df_w["FattyAcid"].drop_duplicates().tolist()

    # 2. Создаем матрицы и принудительно задаем им правильный порядок
    pivot_log2fc = df_w.pivot(index="FattyAcid", columns="Ni", values="Log2FC").reindex(ordered_fa)
    pivot_sig = df_w.pivot(index="FattyAcid", columns="Ni", values="Significance").reindex(ordered_fa)

    # Строим Heatmap
    sns.heatmap(
        pivot_log2fc,
        annot=pivot_sig,
        fmt="",
        cmap="vlag",
        center=0,
        vmin=-3,
        vmax=3,
        ax=axes[i],
        cbar=(i == len(treat_weeks) - 1), # Показываем шкалу только на последнем графике
        linewidths=0.5,
        linecolor="gray",
        annot_kws={"size": 8} # Уменьшенный шрифт
    )

    axes[i].set_title(f"Изменение к Неделе {week}", fontsize=14)
    axes[i].set_xlabel("Концентрация Ni (mM)", fontsize=12)
    if i == 0:
        axes[i].set_ylabel("Жирные кислоты", fontsize=12)
    else:
        axes[i].set_ylabel("")

plt.tight_layout()
plt.show()
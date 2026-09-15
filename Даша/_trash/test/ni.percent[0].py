import polars as pl
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import seaborn as sns
import matplotlib.pyplot as plt

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
print(f"df: {df}")

# 1. Исключаем внутренний стандарт
df_filtered = df.filter(pl.col("FattyAcid") != "17:0")

# НОВОЕ: Считаем сумму ppm для каждого уникального образца и вычисляем процент (%)
df_calc = df_filtered.with_columns(
    # Сумма ppm всех кислот внутри одного образца (одной пробирки)
    total_ppm=pl.col("ppm").sum().over(["Ni", "Week", "Plant", "Sample"])
).with_columns(
    # Считаем долю в процентах
    pct=(pl.col("ppm") / pl.col("total_ppm")) * 100
).with_columns(
    # Логарифмируем проценты (ln(1 + pct)) для стабилизации дисперсии и расчета Log2FC
    log1p_pct=pl.col("pct").log1p()
)

print(f"df_calc: {df_calc}")
df_calc.write_csv("Даша/output_percentages.txt")

# 2. Группируем данные: собираем все значения в списки и считаем среднее (теперь на основе процентов)
df_agg = df_calc.group_by(["Ni", "Week", "FattyAcid"], maintain_order=True).agg(
    values=pl.col("log1p_pct"),  # Собираем значения в список (для t-test)
    mean_val=pl.col("log1p_pct").mean(),  # Среднее (для Log2FC)
)

# 3. Разделяем на контроль (Ni = 0) и опыт (Ni > 0)
df_ctrl = df_agg.filter(pl.col("Ni") == 0).select(
    pl.col("Week"),
    pl.col("FattyAcid"),
    pl.col("values").alias("ctrl_values"),
    pl.col("mean_val").alias("ctrl_mean"),
)

df_treat = df_agg.filter(pl.col("Ni") != 0).select(
    pl.col("Week"),
    pl.col("FattyAcid"),
    pl.col("Ni"),
    pl.col("values").alias("treat_values"),
    pl.col("mean_val").alias("treat_mean"),
)

# 4. Соединяем опыт с контролем
df_joined = df_treat.join(df_ctrl, on=["Week", "FattyAcid"], how="left")

# 5. Считаем Log2FC (теперь это изменение доли кислоты в процентах)
df_joined = df_joined.with_columns(
    Log2FC=(pl.col("treat_mean") - pl.col("ctrl_mean")) / np.log(2)
)

# ==========================================
# 2. СТАТИСТИКА (SCIPY + STATSMODELS)
# ==========================================

# Вытаскиваем колонки со списками значений в Python
treat_lists = df_joined["treat_values"].to_list()
ctrl_lists = df_joined["ctrl_values"].to_list()

p_values = []

# Прогоняем через стандартный t-test из scipy
for t_vals, c_vals in zip(treat_lists, ctrl_lists):
    # Очищаем от возможных None/NaN
    t_clean = [x for x in t_vals if x is not None and not np.isnan(x)]
    c_clean = [x for x in c_vals if x is not None and not np.isnan(x)]

    # t-test требует минимум 2 значения в каждой группе
    if len(t_clean) >= 2 and len(c_clean) >= 2:
        # Welch's t-test (equal_var=False) - стандарт для биологии
        stat, p = ttest_ind(t_clean, c_clean, equal_var=False)
        p_values.append(p)
    else:
        p_values.append(np.nan)

# Возвращаем p-values обратно в Polars
df_joined = df_joined.with_columns(p_value=pl.Series(p_values))

# Делаем FDR-поправку (Benjamini-Hochberg) через statsmodels
valid_mask = df_joined["p_value"].is_not_null() & ~df_joined["p_value"].is_nan()
df_valid = df_joined.filter(valid_mask)

if df_valid.height > 0:
    p_vals_valid = df_valid["p_value"].to_numpy()
    _, q_vals_valid, _, _ = multipletests(p_vals_valid, method="fdr_bh")

    # Добавляем q_value к валидным строкам
    df_valid = df_valid.with_columns(q_value=pl.Series(q_vals_valid))

    # Присоединяем обратно к основной таблице
    df_joined = df_joined.join(
        df_valid.select(["Week", "FattyAcid", "Ni", "q_value"]),
        on=["Week", "FattyAcid", "Ni"],
        how="left",
        maintain_order="left_right",
    )
else:
    df_joined = df_joined.with_columns(q_value=pl.lit(None, dtype=pl.Float64))

print(f"df_joined: {df_joined}")

# Расставляем звездочки значимости
df_joined = df_joined.with_columns(
    Significance=pl.format(
        "{}\n{}()",
        pl.when(pl.col("q_value") < 0.001)
        .then(pl.lit("***"))
        .when(pl.col("q_value") < 0.01)
        .then(pl.lit("**"))
        .when(pl.col("q_value") < 0.05)
        .then(pl.lit("*"))
        .otherwise(pl.lit("")),
        pl.col("Log2FC").round(2),
    )
)

# ==========================================
# 3. ВИЗУАЛИЗАЦИЯ (PANDAS + SEABORN)
# ==========================================

# Конвертируем итоговую таблицу в Pandas для отрисовки
df_plot = df_joined.select(
    ["Week", "FattyAcid", "Ni", "Log2FC", "Significance"]
).to_pandas()

fig, axes = plt.subplots(1, 2, figsize=(12, 12), sharey=True)
fig.suptitle(
    "Изменение профиля жирных кислот при стрессе (Ni vs Ni=0)\nLog2FC (по % от суммы ЖК), Welch's t-test, FDR",
    fontsize=16,
)

for i, week in enumerate([1, 5]):
    df_w = df_plot[df_plot["Week"] == week]

    if df_w.empty:
        continue

    # Извлекаем правильный порядок жирных кислот
    ordered_fa = df_w["FattyAcid"].drop_duplicates().tolist()

    # Создаем матрицы для Heatmap
    pivot_log2fc = df_w.pivot(index="FattyAcid", columns="Ni", values="Log2FC").reindex(
        ordered_fa
    )
    pivot_sig = df_w.pivot(
        index="FattyAcid", columns="Ni", values="Significance"
    ).reindex(ordered_fa)

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
        cbar=(i == 1),
        linewidths=0.5,
        linecolor="gray",
        annot_kws={"size": 8, "weight": "bold", "color": "black"},
    )

    axes[i].set_title(f"Неделя {week}", fontsize=14)
    axes[i].set_xlabel("Концентрация Ni (mM)", fontsize=12)
    if i == 0:
        axes[i].set_ylabel("Жирные кислоты", fontsize=12)
    else:
        axes[i].set_ylabel("")

plt.tight_layout()
plt.show()
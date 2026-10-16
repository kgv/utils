import polars as pl
import numpy as np
from scipy.stats import f_oneway
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

# 2. Группируем данные: собираем все значения в списки и считаем среднее
df_agg = df_calc.group_by(["Week", "FattyAcid", "Ni"]).agg(
    values=pl.col("log1p_ppm"),  # Собираем значения в список (для ANOVA)
    mean_val=pl.col("log1p_ppm").mean(),  # Среднее (для Log2FC)
)

# 3. Разделяем на контроль (Ni = 0) и опыт (Ni > 0) для расчета Log2FC
df_ctrl = df_agg.filter(pl.col("Ni") == 0).select(
    pl.col("Week"),
    pl.col("FattyAcid"),
    pl.col("mean_val").alias("ctrl_mean"),
)

df_treat = df_agg.filter(pl.col("Ni") != 0).select(
    pl.col("Week"),
    pl.col("FattyAcid"),
    pl.col("Ni"),
    pl.col("mean_val").alias("treat_mean"),
)

# 4. Соединяем опыт с контролем
df_joined = df_treat.join(df_ctrl, on=["Week", "FattyAcid"], how="left")

# 5. Считаем Log2FC
df_joined = df_joined.with_columns(
    Log2FC=(pl.col("treat_mean") - pl.col("ctrl_mean")) / np.log(2)
)

# ==========================================
# 2. СТАТИСТИКА (ANOVA - f_oneway)
# ==========================================

anova_results = []

# Группируем исходные агрегированные данные (df_agg) по неделе и кислоте.
# Внутри каждой группы будут лежать списки значений для ВСЕХ концентраций Ni (включая контроль)
for name, group in df_agg.group_by(["Week", "FattyAcid"]):
    week, fa = name[0], name[1]
    
    # Собираем списки чистых значений для каждой концентрации Ni
    samples = []
    for vals in group["values"].to_list():
        clean_vals = [x for x in vals if x is not None and not np.isnan(x)]
        if len(clean_vals) >= 2:  # Берем только те группы, где есть хотя бы 2 повторения
            samples.append(clean_vals)
    
    # Для ANOVA нужно минимум 2 группы (например, контроль и хотя бы один опыт)
    if len(samples) >= 2:
        # f_oneway принимает произвольное количество аргументов (групп) через *
        stat, p = f_oneway(*samples)
        anova_results.append({"Week": week, "FattyAcid": fa, "p_value": p})
    else:
        anova_results.append({"Week": week, "FattyAcid": fa, "p_value": np.nan})

# Превращаем результаты ANOVA в DataFrame
df_anova = pl.DataFrame(anova_results)

# Делаем FDR-поправку (Benjamini-Hochberg) на результаты ANOVA
valid_mask = df_anova["p_value"].is_not_null() & ~df_anova["p_value"].is_nan()
df_valid = df_anova.filter(valid_mask)

if df_valid.height > 0:
    p_vals_valid = df_valid["p_value"].to_numpy()
    _, q_vals_valid, _, _ = multipletests(p_vals_valid, method="fdr_bh")

    # Добавляем q_value к валидным строкам
    df_valid = df_valid.with_columns(q_value=pl.Series(q_vals_valid))

    # Присоединяем обратно к таблице ANOVA
    df_anova = df_anova.join(
        df_valid.select(["Week", "FattyAcid", "q_value"]),
        on=["Week", "FattyAcid"],
        how="left",
    )
else:
    df_anova = df_anova.with_columns(q_value=pl.lit(None, dtype=pl.Float64))

# Присоединяем результаты ANOVA к нашей основной таблице df_joined
# ВАЖНО: Так как ANOVA дает один p-value на всю кислоту, он продублируется для всех концентраций Ni
df_joined = df_joined.join(
    df_anova.select(["Week", "FattyAcid", "q_value"]), 
    on=["Week", "FattyAcid"], 
    how="left"
)

# Расставляем звездочки значимости (с правильным приведением типов!)
df_joined = df_joined.with_columns(
    Stars=pl.when(pl.col("q_value") < 0.001).then(pl.lit("***"))
    .when(pl.col("q_value") < 0.01).then(pl.lit("**"))
    .when(pl.col("q_value") < 0.05).then(pl.lit("*"))
    .otherwise(pl.lit("")),
    
    Q=pl.when(pl.col("q_value") < 0.001).then(pl.lit("p<0.001"))
    .otherwise(pl.col("q_value").round(decimals=3).cast(pl.String))
).with_columns(
    Significance=pl.format("{}\n{}", pl.col("Stars"), pl.col("Q"))
)

# ==========================================
# 3. ВИЗУАЛИЗАЦИЯ (PANDAS + SEABORN)
# ==========================================

# Конвертируем итоговую таблицу в Pandas для отрисовки
df_plot = df_joined.select(
    ["Week", "FattyAcid", "Ni", "Log2FC", "Significance"]
).to_pandas()

fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharey=True)
fig.suptitle("Изменение профиля жирных кислот при стрессе (Ni), Log2FC\n(Значимость по ANOVA для всей кислоты)", fontsize=16)

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
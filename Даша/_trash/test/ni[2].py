import polars as pl
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================
# 0. НАСТРОЙКИ (МЕНЯТЬ ЗДЕСЬ НА ЛЕТУ)
# ==========================================

# Метод обработки нулей и расчета:
# "epsilon" -> заменяет 0 на epsilon, считает среднее, Log2FC = log2(treat_mean / ctrl_mean)
# "log1p"   -> считает ln(1 + val), считает среднее, Log2FC = (treat_mean - ctrl_mean) / ln(2)
TRANSFORM_METHOD = "log1p"  # Варианты: "epsilon" или "log1p"

# Целевая колонка в данных (ppm или pct)
TARGET_COL = "ppm"  # Варианты: "ppm" или "pct"

# Значение для замены нулей (используется только если TRANSFORM_METHOD = "epsilon")
EPSILON = np.finfo(float).eps  # Можно заменить на кастомное, например 0.001

# ==========================================
# 1. ПОДГОТОВКА ДАННЫХ
# ==========================================

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
print(f"Исходный df:\n{df.head()}")

# Определяем выражение для трансформации на основе настроек
if TRANSFORM_METHOD == "epsilon":
    transform_expr = (
        pl.when(pl.col(TARGET_COL) == 0)
        .then(pl.col(TARGET_COL) + EPSILON)
        .otherwise(pl.col(TARGET_COL))
    )
elif TRANSFORM_METHOD == "log1p":
    transform_expr = pl.col(TARGET_COL).log1p()
else:
    raise ValueError("Неизвестный TRANSFORM_METHOD. Выберите 'epsilon' или 'log1p'.")

# 1. Исключаем внутренний стандарт и применяем выбранную трансформацию
df_calc = (
    df.filter(pl.col("FattyAcid") != "17:0")
    .filter(pl.col("Plant") != 37)
    .with_columns(transform_expr.alias("processed_val"))
)

# 2. Группируем данные: собираем все значения в списки и считаем среднее
df_agg = df_calc.group_by(["Ni", "Week", "FattyAcid"], maintain_order=True).agg(
    values=pl.col("processed_val"),  # Собираем значения в список (для t-test)
    mean_val=pl.col("processed_val").mean(),  # Среднее (для Log2FC)
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

# 5. Считаем Log2FC в зависимости от выбранного метода
if TRANSFORM_METHOD == "epsilon":
    # Если значения исходные, берем логарифм отношения
    df_joined = df_joined.with_columns(
        Log2FC=(pl.col("treat_mean") / pl.col("ctrl_mean")).log(2)
    )
elif TRANSFORM_METHOD == "log1p":
    # Если значения уже логарифмированы (ln), берем разность и делим на ln(2) для перевода в Log2
    df_joined = df_joined.with_columns(
        Log2FC=(pl.col("treat_mean") - pl.col("ctrl_mean")) / np.log(2)
    )


def format_list(name):
    return pl.format(
        "[{}]", pl.col(name).cast(pl.List(pl.String)).list.join(",")
    ).alias(name)


# ==========================================
# 2. СТАТИСТИКА (SCIPY + STATSMODELS)
# ==========================================

# Вытаскиваем колонки со списками значений в Python
treat_lists = df_joined["treat_values"].to_list()
ctrl_lists = df_joined["ctrl_values"].to_list()

p_values = []

# Прогоняем через стандартный t-test из scipy
for t_vals, c_vals in zip(treat_lists, ctrl_lists):
    t_clean = [x for x in t_vals if x is not None and not np.isnan(x)]
    c_clean = [x for x in c_vals if x is not None and not np.isnan(x)]

    if len(t_clean) >= 2 and len(c_clean) >= 2:
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

    df_valid = df_valid.with_columns(q_value=pl.Series(q_vals_valid))

    df_joined = df_joined.join(
        df_valid.select(["Week", "FattyAcid", "Ni", "q_value"]),
        on=["Week", "FattyAcid", "Ni"],
        how="left",
        maintain_order="left_right",
    )
else:
    df_joined = df_joined.with_columns(q_value=pl.lit(None, dtype=pl.Float64))

print(f"Итоговый df_joined:\n{df_joined.head()}")

# Сохраняем результаты
df_joined.with_columns(
    [
        format_list("treat_values"),
        format_list("ctrl_values"),
    ]
).write_csv("Даша/output.txt")

# Расставляем звездочки значимости
df_joined = df_joined.with_columns(
    Significance=pl.format(
        "{}\n{}/{}\n{}()",
        pl.when(pl.col("q_value") < 0.001)
        .then(pl.lit("***"))
        .when(pl.col("q_value") < 0.01)
        .then(pl.lit("**"))
        .when(pl.col("q_value") < 0.05)
        .then(pl.lit("*"))
        .otherwise(pl.lit("")),
        pl.col("treat_mean").round(1),
        pl.col("ctrl_mean").round(1),
        pl.col("Log2FC").round(2),
    )
)

# ==========================================
# 3. ВИЗУАЛИЗАЦИЯ (PANDAS + SEABORN)
# ==========================================

df_plot = df_joined.select(
    ["Week", "FattyAcid", "Ni", "Log2FC", "Significance"]
).to_pandas()

fig, axes = plt.subplots(1, 2, figsize=(12, 12), sharey=True)
fig.suptitle(
    f"Изменение профиля жирных кислот при стрессе (Ni vs Ni=0)\n"
    f"Метод: {TRANSFORM_METHOD}, {TARGET_COL}\n"
    f"Log2FC, Welch's t-test, Benjamini/Hochberg",
    fontsize=14,
)

for i, week in enumerate([1, 5]):
    df_w = df_plot[df_plot["Week"] == week]

    if df_w.empty:
        continue

    ordered_fa = df_w["FattyAcid"].drop_duplicates().tolist()

    pivot_log2fc = df_w.pivot(index="FattyAcid", columns="Ni", values="Log2FC").reindex(
        ordered_fa
    )
    pivot_sig = df_w.pivot(
        index="FattyAcid", columns="Ni", values="Significance"
    ).reindex(ordered_fa)

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

import polars as pl

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
print(f"df: {df}")

df = df.filter(pl.col("FattyAcid") != "17:0")

import polars as pl
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests

df = df.to_pandas()

# Списки для сохранения результатов статистики
results = []

# 2. Считаем статистику и Log2FC
weeks = df["Week"].unique()
fatty_acids = df["FattyAcid"].unique()
treatments = [50, 250, 500, 750, 1000]  # Концентрации без контроля

for week in weeks:
    df_week = df[df["Week"] == week]

    for fa in fatty_acids:
        df_fa = df_week[df_week["FattyAcid"] == fa]

        # Данные контроля (Ni = 0)
        ctrl_data = df_fa[df_fa["Ni"] == 0]["ppm"].dropna().values
        ctrl_mean = ctrl_data.mean() if len(ctrl_data) > 0 else np.nan

        for ni in treatments:
            treat_data = df_fa[df_fa["Ni"] == ni]["ppm"].dropna().values
            treat_mean = treat_data.mean() if len(treat_data) > 0 else np.nan

            # Считаем Fold Change и Log2FC
            # Добавляем крошечное число (1e-9), чтобы избежать деления на ноль
            fc = treat_mean / (ctrl_mean + 1e-9)
            log2fc = np.log2(fc) if fc > 0 else np.nan

            # Считаем p-value (t-test Стьюдента)
            if len(ctrl_data) >= 2 and len(treat_data) >= 2:
                stat, pval = ttest_ind(
                    treat_data, ctrl_data, equal_var=False
                )  # Welch's t-test
            else:
                pval = np.nan

            results.append(
                {
                    "Week": week,
                    "FattyAcid": fa,
                    "Ni": ni,
                    "Log2FC": log2fc,
                    "p_value": pval,
                }
            )

# Создаем датафрейм с результатами
df_stats = pd.DataFrame(results)

# 3. Поправка на множественное тестирование (FDR Benjamini-Hochberg)
# Убираем NaN перед поправкой
mask_valid = df_stats["p_value"].notna()
df_stats.loc[mask_valid, "q_value"] = multipletests(
    df_stats.loc[mask_valid, "p_value"], method="fdr_bh"
)[1]


# 4. Функция для расстановки звездочек значимости
def get_asterisks(q):
    if pd.isna(q):
        return ""
    elif q < 0.001:
        return "***"
    elif q < 0.01:
        return "**"
    elif q < 0.05:
        return "*"
    else:
        return ""


df_stats["Significance"] = df_stats["q_value"].apply(get_asterisks)

# ==========================================
# 5. ПОСТРОЕНИЕ HEATMAP
# ==========================================

fig, axes = plt.subplots(1, 2, figsize=(16, 8), sharey=True)
fig.suptitle(
    "Изменение профиля жирных кислот при стрессе (Ni), Log2 Fold Change", fontsize=16
)

for i, week in enumerate([1, 5]):
    # Фильтруем данные по неделе
    df_w = df_stats[df_stats["Week"] == week]

    # Создаем сводные таблицы (pivot) для значений цвета (Log2FC) и текста (звездочки)
    pivot_log2fc = df_w.pivot(index="FattyAcid", columns="Ni", values="Log2FC")
    pivot_sig = df_w.pivot(index="FattyAcid", columns="Ni", values="Significance")

    # Сортируем кислоты по длине цепи (опционально, для красоты)
    # pivot_log2fc = pivot_log2fc.sort_index()
    # pivot_sig = pivot_sig.reindex(pivot_log2fc.index)

    # Строим Heatmap
    sns.heatmap(
        pivot_log2fc,
        annot=pivot_sig,  # Накладываем звездочки
        fmt="",  # Формат текста (пустой, так как у нас строки со звездочками)
        cmap="vlag",  # Красно-синяя палитра (vlag или RdBu_r)
        center=0,  # Центр палитры на нуле (белый цвет)
        vmin=-3,
        vmax=3,  # Ограничиваем шкалу (настройте под свои данные, например -5 до 5)
        ax=axes[i],
        cbar=(i == 1),  # Цветовую шкалу рисуем только на втором графике
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

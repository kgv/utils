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
print(f"read: {df}")

# Вычищаем лишние пробелы из заголовков
df = df.rename({col: col.strip() for col in df.columns})
print(f"rename: {df}")

# Вычищаем пробелы из всех строковых колонок и приводим типы
df = df.with_columns(pl.col(pl.String()).str.strip_chars()).with_columns(
    pl.col("Day").cast(pl.Int64),
    pl.col("Mean").cast(pl.Float64),
    pl.col("StandardDeviation").cast(pl.Float64),
)
print(f"cast: {df}")

lines = df["Line"].unique().sort().to_list()
n_lines = len(lines)
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

################################################################################

# 1. Делаем сводную таблицу:
# Строки - уникальные образцы (Line + Day)
# Колонки - жирные кислоты (FattyAcid)
# Значения - Mean
pivot_corr = df.pivot(
    index=["Line", "Day"],
    on="FattyAcid",
    values="Mean",
)
print(f"pivot_corr: {pivot_corr}")

# 2. Убираем текстовые колонки, оставляем только числа для корреляции
numeric_for_corr = pivot_corr.drop(["Line", "Day"])

# 3. Считаем матрицу корреляций средствами Polars (по умолчанию Пирсон)
corr_matrix_pl = numeric_for_corr.corr()

# 4. Переводим в Pandas для Seaborn и задаем индексы (названия строк),
# чтобы на графике были подписаны обе оси
corr_matrix_pd = corr_matrix_pl.to_pandas()
corr_matrix_pd.index = numeric_for_corr.columns

# 5. Рисуем график
plt.figure(figsize=(8, 6))
sns.heatmap(
    corr_matrix_pd,
    annot=True,  # Показывать цифры
    fmt=".2f",  # 2 знака после запятой
    cmap="coolwarm",  # Красно-синяя цветовая шкала (стандарт для корреляций)
    vmin=-1,  # Минимальное значение корреляции
    vmax=1,  # Максимальное значение корреляции
    center=0,  # Центр цветовой шкалы
    linewidths=0.5,
    linecolor="white",
)
plt.title("Общая матрица корреляций жирных кислот", fontsize=14)
plt.tight_layout()
plt.show()

################################################################################

# Создаем фигуру, где количество графиков равно количеству линий
# Если линий много, график будет широким.
fig, axes = plt.subplots(1, n_lines, figsize=(3.2 * n_lines, 3.2), sharey=True)

for i, line in enumerate(lines):
    # 1. Фильтруем данные только для текущей линии
    line_df = df.filter(pl.col("Line") == line)

    # # 2. Делаем Pivot:
    # # Строки - Дни (Day)
    # # Колонки - Жирные кислоты (FattyAcid)
    # # Значения - Mean
    # pivot_line = line_df.pivot(values="Mean", index="Day", on="FattyAcid")

    # 2. Делаем Pivot:
    # сравниваем ДНИ на основе профиля жирных кислот
    pivot_days = line_df.pivot(
        index="FattyAcid",
        on="Day",
        values="Mean",
    )

    # # 3. Убираем колонку "Day", чтобы остались только числа для корреляции
    # numeric_for_corr = pivot_days.drop("Day")

    # 3. Убираем колонку "FattyAcid", чтобы остались только числа для корреляции
    corr_days_pl = pivot_days.drop("FattyAcid").corr()

    # 4. Считаем матрицу корреляций
    corr_pl = corr_days_pl.corr()

    # 5. Переводим в Pandas и задаем индексы для Seaborn
    corr_pd = corr_pl.to_pandas()
    corr_pd.index = corr_days_pl.columns

    # 6. Рисуем тепловую карту
    sns.heatmap(
        corr_pd,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        ax=axes[i],
        cbar=(i == n_lines - 1),  # Цветовая шкала только на последнем графике
        vmin=-1,
        vmax=1,
        center=0,
        linewidths=0.5,
        linecolor="white",
    )

    axes[i].set_title(f"Line: {line}", fontsize=14)
    axes[i].set_xlabel("Fatty acid", fontsize=12)

    if i == 0:
        axes[i].set_ylabel("Fatty acid", fontsize=14)
    else:
        axes[i].set_ylabel("")

plt.tight_layout()
plt.show()

################################################################################

# # Создаем фигуру с 3 графиками в ряд
# fig, axes = plt.subplots(1, 3, figsize=(19.2, 6.4), sharey=True)

# for i, day in enumerate(days):
#     # Фильтруем данные для конкретного дня
#     day_df = df.filter(pl.col("Day") == day)

#     if day_df.is_empty():
#         continue

#     # Делаем Pivot: строки - Line, колонки - FattyAcid, значения - Mean
#     pivot_day = day_df.pivot(values="Mean", index="Line", on="FattyAcid").drop(
#         "Line"
#     )  # Убираем Line, оставляем только числа

#     # Считаем корреляцию
#     corr_pl = pivot_day.corr()

#     # Переводим в Pandas и восстанавливаем индексы строк
#     corr_pd = corr_pl.to_pandas()
#     corr_pd.index = pivot_day.columns

#     # Рисуем тепловую карту
#     sns.heatmap(
#         corr_pd,
#         annot=True,
#         fmt=".2f",
#         cmap="coolwarm",
#         ax=axes[i],
#         cbar=(i == 2),  # Показываем цветовую шкалу только на последнем графике
#         vmin=-1,
#         vmax=1,
#         center=0,
#         linewidths=0.5,
#         linecolor="white",
#     )

#     axes[i].set_title(f"Day {day} Correlation", fontsize=14)
#     axes[i].set_xlabel("", fontsize=14)
#     if i == 0:
#         axes[i].set_ylabel("Fatty acid", fontsize=14)
#     else:
#         axes[i].set_ylabel("")

# plt.tight_layout()
# plt.show()

from pathlib import Path
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns

try:
    import common

    DATA = common.dataDirectory()
except ImportError:
    DATA = Path().resolve() / "test/data"

FOUR_SESSIONS_CSV = DATA / "four_sessions.csv"

# 1. Чтение данных
four_sessions = pl.read_csv(FOUR_SESSIONS_CSV)
print(four_sessions.head())

# 2. Группировка и вычисление средних
# Сортируем по "Page", чтобы порядок совпадал с поведением pandas
means_df = four_sessions.group_by("Page").agg(pl.col("Time").mean()).sort("Page")

# Извлекаем значения в виде списка (эквивалент .values.ravel() в pandas)
observed_means = means_df.get_column("Time").to_list()
print("Observed means:", observed_means)

# Вычисляем дисперсию средних значений
variance = means_df.get_column("Time").var()
print("Variance:", variance)

# Вычисления делаем в быстром Polars, а для графика временно переходим в pandas
ax = four_sessions.to_pandas().boxplot(by="Page", column="Time", figsize=(4, 4))
ax.set_xlabel("Page")
ax.set_ylabel("Time (in seconds)")
plt.suptitle("")
plt.title("")

plt.tight_layout()
plt.show()

# ┌────────┬──────┐
# │ Page   ┆ Time │
# │ ---    ┆ ---  │
# │ str    ┆ i64  │
# ╞════════╪══════╡
# │ Page 1 ┆ 164  │
# │ Page 2 ┆ 178  │
# │ Page 3 ┆ 175  │
# │ Page 4 ┆ 155  │
# │ Page 1 ┆ 172  │
# └────────┴──────┘
# Observed means: [172.8, 182.6, 175.6, 164.6]
# Variance: 55.426666666666655
from pathlib import Path
import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as stats
import statsmodels.api as sm

try:
    import common

    DATA = common.dataDirectory()
except ImportError:
    DATA = Path().resolve() / "test/data"

WEB_PAGE_DATA_CSV = DATA / "web_page_data.csv"

# 1. Чтение данных
session_times = pl.read_csv(WEB_PAGE_DATA_CSV)
print(session_times.head())

# 2. Группировка и вычисление средних
# Сортируем по "Page", чтобы порядок совпадал с поведением pandas
means_df = session_times.group_by("Page").agg(pl.col("Time").mean()).sort("Page")


# Выделяем данные в отдельные переменные (Series) для читаемости
time_A = session_times.filter(pl.col("Page") == "Page A").get_column("Time")
time_B = session_times.filter(pl.col("Page") == "Page B").get_column("Time")

# Вариант с использованием scipy
_tstat, pvalue = stats.ttest_ind(
    time_A,
    time_B,
    equal_var=False,
)
print(f"p-value for single sided test: {pvalue / 2:.4f}")

# Вариант с использованием statsmodels
_tstat, pvalue, _df = sm.stats.ttest_ind(
    time_A,
    time_B,
    usevar="unequal",
    alternative="smaller",
)
print(f"p-value: {pvalue:.4f}")

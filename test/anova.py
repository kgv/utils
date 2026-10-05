from pathlib import Path
import random

import pandas as pd
import numpy as np

from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats import power

import matplotlib.pylab as plt

try:
    import common

    DATA = common.dataDirectory()
except ImportError:
    DATA = Path().resolve() / "test/data"

WEB_PAGE_DATA_CSV = DATA / "web_page_data.csv"
FOUR_SESSIONS_CSV = DATA / "four_sessions.csv"

session_times = pd.read_csv(WEB_PAGE_DATA_CSV)
four_sessions = pd.read_csv(FOUR_SESSIONS_CSV)

# # Перестановочный тест для нескольких групп (стр. 137, 139)
# # Предполагается, что DataFrame four_sessions загружен
# observed_variance = four_sessions.groupby("Page").mean().var()[0]
# print("Наблюдаемые средние:", four_sessions.groupby("Page").mean().values.ravel())
# print("Дисперсия:", observed_variance)


# def perm_test(df):
#     df = df.copy()
#     df["Time"] = np.random.permutation(df["Time"].values)
#     return df.groupby("Page").mean().var()[0]


# perm_variance = [perm_test(four_sessions) for _ in range(3000)]
# print("Pr(Prob)", np.mean([var > observed_variance for var in perm_variance]))

# # F-статистика / ANOVA с помощью statsmodels (стр. 139)
# model = smf.ols("Time ~ Page", data=four_sessions).fit()
# aov_table = sm.stats.anova_lm(model)
# print(aov_table)


print(pd.read_csv(FOUR_SESSIONS_CSV).head())

# print("Observed means:", four_sessions.groupby("Page").mean().values.ravel())
# print("Variance:", four_sessions.groupby("Page").mean().var()[0])

# ax = four_sessions.boxplot(by="Page", column="Time", figsize=(4, 4))
# ax.set_xlabel("Page")
# ax.set_ylabel("Time (in seconds)")
# plt.suptitle("")
# plt.title("")

# plt.tight_layout()
# plt.show()

## t-Tests

res = stats.ttest_ind(
    session_times[session_times.Page == "Page A"].Time,
    session_times[session_times.Page == "Page B"].Time,
    equal_var=False,
)
print(f"p-value for single sided test: {res.pvalue / 2:.4f}")

tstat, pvalue, df = sm.stats.ttest_ind(
    session_times[session_times.Page == "Page A"].Time,
    session_times[session_times.Page == "Page B"].Time,
    usevar="unequal",
    alternative="smaller",
)
print(f"tstat: {tstat:.4f}")
print(f"p-value: {pvalue:.4f}")

#

model = smf.ols("Time ~ Page", data=four_sessions).fit()

aov_table = sm.stats.anova_lm(model)
print(aov_table)

res = stats.f_oneway(
    four_sessions[four_sessions.Page == "Page 1"].Time,
    four_sessions[four_sessions.Page == "Page 2"].Time,
    four_sessions[four_sessions.Page == "Page 3"].Time,
    four_sessions[four_sessions.Page == "Page 4"].Time,
)
print(f"res: {res}")
print(f"F-Statistic: {res.statistic / 2:.4f}")
print(f"p-value: {res.pvalue / 2:.4f}")

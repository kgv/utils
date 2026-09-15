from scipy.stats import ttest_ind_from_stats

# Функция для расчета статистики
def calc_stats(row):
    t_stat, p_val = ttest_ind_from_stats(
        mean1=row["Mean_Control"],
        std1=row["StandardDeviation_Control"],
        nobs1=N,
        mean2=row["Mean"],
        std2=row["StandardDeviation"],
        nobs2=N,
    )
    return {"p_value": p_val, "f_stat": t_stat**2}

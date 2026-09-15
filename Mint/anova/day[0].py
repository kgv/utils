import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. ЧТЕНИЕ CSV (ЖЕЛЕЗОБЕТОННЫЙ ВАРИАНТ)
# ==========================================
df = pd.read_csv('_py/anova/Table1.csv', 
                 sep=',', 
                 header=0, 
                 names=['Line', 'Day', 'Fatty acid', 'Value'], 
                 skipinitialspace=True, 
                 encoding='utf-8-sig')

# Вычищаем кавычки и пробелы
for col in df.columns:
    df[col] = df[col].astype(str).str.strip(' "')

# Разделяем "Mean±SD" на две числовые колонки
df[['Mean', 'SD']] = df['Value'].str.split('±', expand=True).astype(float)

# ==========================================
# 2. РАСЧЕТ СТАТИСТИКИ (ОТНОСИТЕЛЬНО 0 ДНЯ)
# ==========================================
N_SAMPLES = 3  # Укажите реальное количество повторностей (n)
BASE_DAY = '0' # Базовый день для сравнения

results = []
lines = df['Line'].unique()
fatty_acids = df['Fatty acid'].unique()
# Дни для сравнения (все, кроме базового 0-го)
target_days = [d for d in df['Day'].unique() if d != BASE_DAY]

for line in lines:
    for fa in fatty_acids:
        # КОНТРОЛЬ: 0-й день для ТЕКУЩЕЙ линии и ТЕКУЩЕЙ жирной кислоты
        ctrl = df[(df['Line'] == line) & (df['Day'] == BASE_DAY) & (df['Fatty acid'] == fa)]
        if ctrl.empty:
            continue
        mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
        
        # Сравниваем 2-й и 7-й день с 0-м днем
        for day in target_days:
            treat = df[(df['Line'] == line) & (df['Day'] == day) & (df['Fatty acid'] == fa)]
            if treat.empty:
                continue
            mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
            
            # t-тест
            t_stat, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                                 mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
            
            results.append({
                'Day': day,
                'Fatty acid': fa,
                'Line': line,
                'p_value': p_val
            })

res_df = pd.DataFrame(results)

# ==========================================
# 3. ВИЗУАЛИЗАЦИЯ
# ==========================================
def get_significance_stars(p):
    if pd.isna(p): return ''
    if p < 0.001: return '***'
    elif p < 0.01: return '**'
    elif p < 0.05: return '*'
    else: return 'ns'

res_df['Significance'] = res_df['p_value'].apply(get_significance_stars)
res_df['Log_P'] = -np.log10(res_df['p_value'])

# Создаем графики (по количеству target_days, обычно их 2: День 2 и День 7)
fig, axes = plt.subplots(1, len(target_days), figsize=(12, 6), sharey=True)
if len(target_days) == 1: axes = [axes] # Защита, если день только один

fig.suptitle(f'Динамика изменений: сравнение с 0-м днем внутри каждой линии\n'
             f'Тест Стьюдента (n={N_SAMPLES}). ns: p>0.05, *: p<0.05, **: p<0.01, ***: p<0.001', 
             fontsize=14, y=1.05)

for i, day in enumerate(target_days):
    day_data = res_df[res_df['Day'] == day]
    if day_data.empty: continue
        
    pivot_color = day_data.pivot(index='Fatty acid', columns='Line', values='Log_P')
    pivot_annot = day_data.pivot(index='Fatty acid', columns='Line', values='Significance')
    
    # Рисуем тепловую карту
    sns.heatmap(pivot_color, annot=pivot_annot, fmt='', cmap='Blues', 
                ax=axes[i], cbar=(i == len(target_days)-1), vmin=0, vmax=3, 
                cbar_kws={'label': '-log10(p-value)'} if i == len(target_days)-1 else None,
                linewidths=1, linecolor='white')
    
    axes[i].set_title(f'День {day} vs День 0', fontsize=12)
    axes[i].set_xlabel('Линия', fontsize=11)
    if i == 0: 
        axes[i].set_ylabel('Жирная кислота', fontsize=11)
    else: 
        axes[i].set_ylabel('')

plt.tight_layout()
plt.show()
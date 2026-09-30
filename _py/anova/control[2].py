import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. ЯДЕРНЫЙ ВАРИАНТ ЧТЕНИЯ CSV
# ==========================================
# header=0 - выкидывает первую строку файла с кривыми заголовками
# names=[...] - принудительно ставит наши чистые названия
df = pd.read_csv('_py/anova/Table1.csv', 
                 sep=',', 
                 header=0, 
                 names=['Line', 'Day', 'Fatty acid', 'Value'], 
                 skipinitialspace=True, 
                 encoding='utf-8-sig')

# 2. Вычищаем вообще все кавычки и лишние пробелы из самих данных
for col in df.columns:
    df[col] = df[col].astype(str).str.strip(' "')

# Проверяем, что теперь всё идеально:
print("Колонки, которые теперь видит Питон:", df.columns.tolist())

# 3. Разделяем "Mean±SD" на две числовые колонки
df[['Mean', 'SD']] = df['Value'].str.split('±', expand=True).astype(float)

# ==========================================
# ДАЛЬШЕ ИДЕТ КОД СО СТАТИСТИКОЙ
# ==========================================
N_SAMPLES = 3  # Укажите реальное количество повторностей (n)
CONTROL_LINE = '54WT'

results = []
exp_lines = [line for line in df['Line'].unique() if line != CONTROL_LINE]
days = sorted(df['Day'].unique(), key=int)
fatty_acids = df['Fatty acid'].unique()

for day in days:
    for fa in fatty_acids:
        ctrl = df[(df['Line'] == CONTROL_LINE) & (df['Day'] == str(day)) & (df['Fatty acid'] == fa)]
        if ctrl.empty:
            continue
        mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
        
        for exp in exp_lines:
            treat = df[(df['Line'] == exp) & (df['Day'] == str(day)) & (df['Fatty acid'] == fa)]
            if treat.empty:
                continue
            mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
            
            t_stat, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                                 mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
            
            results.append({
                'Day': day,
                'Fatty acid': fa,
                'Line': exp,
                'p_value': p_val
            })

res_df = pd.DataFrame(results)

# def get_significance_stars(p):
#     if pd.isna(p): return ''
#     if p < 0.001: return '***'
#     elif p < 0.01: return '**'
#     elif p < 0.05: return '*'
#     else: return 'ns'
def get_annotation(p):
    if pd.isna(p): return ''
    
    # Определяем звездочки
    if p < 0.001: stars = '***'
    elif p < 0.01: stars = '**'
    elif p < 0.05: stars = '*'
    else: stars = 'ns'
    
    # Форматируем p-value до 3 знаков после запятой
    if p < 0.001:
        p_text = '<0.001'
    else:
        p_text = f"{p:.3f}" # Округление до 3 знаков
        
    # Возвращаем p-value и звездочки на новой строке
    return f"{p_text}\n({stars})"

res_df['Significance'] = res_df['p_value'].apply(get_annotation)
res_df['Log_P'] = -np.log10(res_df['p_value'])

fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
# fig.suptitle(f'Статистическая значимость отличий от контроля ({CONTROL_LINE})\n'
#              f'Тест Стьюдента (n={N_SAMPLES}). ns: p>0.05, *: p<0.05, **: p<0.01, ***: p<0.001', 
#              fontsize=14, y=1.05)

for i, day in enumerate(days):
    day_data = res_df[res_df['Day'] == day]
    if day_data.empty: continue
        
    pivot_color = day_data.pivot(index='Fatty acid', columns='Line', values='Log_P')
    pivot_annot = day_data.pivot(index='Fatty acid', columns='Line', values='Significance')
    
    sns.heatmap(pivot_color, annot=pivot_annot, fmt='', cmap='Reds', 
                ax=axes[i], cbar=(i==2), vmin=0, vmax=3, 
                cbar_kws={'label': '-log(p-value)'} if i==2 else None,
                linewidths=1, linecolor='white')
    
    axes[i].set_title(f'Day {day}', fontsize=14)
    # axes[i].set_xlabel('Line', fontsize=14)
    if i == 0: axes[i].set_ylabel('Fatty acid', fontsize=14)
    else: axes[i].set_ylabel('')

plt.tight_layout()
plt.show()
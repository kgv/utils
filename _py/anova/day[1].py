import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. ЧТЕНИЕ CSV
# ==========================================
# df = pd.read_csv('_py/anova/Table1.csv', 
df = pd.read_csv('_py/anova/Table2.csv', 
                 sep=',', 
                 header=0, 
                 names=['Line', 'Day', 'Fatty acid', 'Value'], 
                 skipinitialspace=True, 
                 encoding='utf-8-sig')

for col in df.columns:
    df[col] = df[col].astype(str).str.strip(' "')

df[['Mean', 'SD']] = df['Value'].str.split('±', expand=True).astype(float)

# ==========================================
# 2. РАСЧЕТ СТАТИСТИКИ (ОТНОСИТЕЛЬНО 0 ДНЯ)
# ==========================================
N_SAMPLES = 3  
BASE_DAY = '0' 

results = []
lines = df['Line'].unique()
fatty_acids = df['Fatty acid'].unique()
target_days = [d for d in df['Day'].unique() if d != BASE_DAY]

for line in lines:
    for fa in fatty_acids:
        ctrl = df[(df['Line'] == line) & (df['Day'] == BASE_DAY) & (df['Fatty acid'] == fa)]
        if ctrl.empty: continue
        mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
        
        for day in target_days:
            treat = df[(df['Line'] == line) & (df['Day'] == day) & (df['Fatty acid'] == fa)]
            if treat.empty: continue
            mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
            
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
# 3. ВИЗУАЛИЗАЦИЯ (С P-VALUE В ЯЧЕЙКАХ)
# ==========================================
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

# Применяем новую функцию
res_df['Annotation'] = res_df['p_value'].apply(get_annotation)
res_df['Log_P'] = -np.log10(res_df['p_value'])

fig, axes = plt.subplots(1, len(target_days), figsize=(14, 7), sharey=True)
if len(target_days) == 1: axes = [axes]

# fig.suptitle(f'Динамика изменений: сравнение с 0-м днем внутри каждой линии\n'
#              f'Тест Стьюдента (n={N_SAMPLES}). ns: p>0.05, *: p<0.05, **: p<0.01, ***: p<0.001', 
#              fontsize=14, y=1.05)

for i, day in enumerate(target_days):
    day_data = res_df[res_df['Day'] == day]
    if day_data.empty: continue
        
    pivot_color = day_data.pivot(index='Fatty acid', columns='Line', values='Log_P')
    # Используем колонку Annotation для текста
    pivot_annot = day_data.pivot(index='Fatty acid', columns='Line', values='Annotation')
    
    # sns.heatmap(pivot_color, annot=pivot_annot, fmt='', cmap='Greens', 
    sns.heatmap(pivot_color, annot=pivot_annot, fmt='', cmap='Purples', 
                ax=axes[i], cbar=(i == len(target_days)-1), vmin=0, vmax=3, 
                cbar_kws={'label': '-log(p-value)'} if i == len(target_days)-1 else None,
                linewidths=1, linecolor='white',
                annot_kws={"size": 9}) # Уменьшили шрифт для цифр
    
    axes[i].set_title(f'Day {day}', fontsize=14)
    axes[i].set_xlabel('', fontsize=14)
    if i == 0: 
        # axes[i].set_ylabel('Fatty acid', fontsize=14)
        axes[i].set_ylabel('Compound', fontsize=14)
    else: 
        axes[i].set_ylabel('')

plt.tight_layout()
plt.show()
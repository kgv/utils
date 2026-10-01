import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. ЯДЕРНЫЙ ВАРИАНТ ЧТЕНИЯ CSV
# ==========================================
df = pd.read_csv('_py/anova/Table2.csv', 
                 sep=',', 
                 header=0, 
                 names=['Line', 'Day', 'Fatty acid', 'Value'], 
                 skipinitialspace=True, 
                 encoding='utf-8-sig')

# 2. Вычищаем вообще все кавычки и лишние пробелы из самих данных
for col in df.columns:
    df[col] = df[col].astype(str).str.strip(' "')

print("Колонки, которые теперь видит Питон:", df.columns.tolist())

# 3. Разделяем "Mean±SD" на две числовые колонки
df[['Mean', 'SD']] = df['Value'].str.split('±', expand=True).astype(float)

# ==========================================
# ДАЛЬШЕ ИДЕТ КОД СО СТАТИСТИКОЙ
# ==========================================
N_SAMPLES = 3  # Укажите реальное количество повторностей (n)
CONTROL_LINE = '54 WT'

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
            
            # Считаем t-статистику и p-value
            t_stat, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                                 mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
            
            # Для двух групп F-критерий (ANOVA) равен квадрату t-критерия
            f_stat = t_stat ** 2 
            
            results.append({
                'Day': day,
                'Fatty acid': fa,
                'Line': exp,
                'p_value': p_val,
                'f_stat': f_stat # Добавляем F-статистику в результаты
            })

res_df = pd.DataFrame(results)

# Обновленная функция теперь принимает всю строку датафрейма (row)
def get_annotation(row):
    p = row['p_value']
    f = row['f_stat']
    
    if pd.isna(p): return ''
    
    # Определяем звездочки
    if p < 0.001: stars = '***'
    elif p < 0.01: stars = '**'
    elif p < 0.05: stars = '*'
    else: stars = 'ns'
    
    # Форматируем p-value
    if p < 0.001:
        p_text = 'p<0.001'
    else:
        p_text = f"p={p:.3f}"
        
    # Форматируем F-статистику (округляем до 2 знаков)
    f_text = f"F={f:.2f}"
        
    # Возвращаем F, p-value и звездочки на разных строках
    return f"{f_text}\n{p_text}\n({stars})"

# Применяем функцию ко всем строкам (axis=1)
res_df['Significance'] = res_df.apply(get_annotation, axis=1)
res_df['Log_P'] = -np.log10(res_df['p_value'])

# Увеличил высоту графика (с 6 до 8), чтобы 3 строки текста влезли без наложения
fig, axes = plt.subplots(1, 3, figsize=(16, 8), sharey=True)

for i, day in enumerate(days):
    day_data = res_df[res_df['Day'] == day]
    if day_data.empty: continue
        
    pivot_color = day_data.pivot(index='Fatty acid', columns='Line', values='Log_P')
    pivot_annot = day_data.pivot(index='Fatty acid', columns='Line', values='Significance')
    
    sns.heatmap(pivot_color, annot=pivot_annot, fmt='', cmap='Greens', 
                ax=axes[i], cbar=(i==2), vmin=0, vmax=3, 
                cbar_kws={'label': '-log(p-value)'} if i==2 else None,
                linewidths=1, linecolor='white')
    
    axes[i].set_title(f'Day {day}', fontsize=14)
    axes[i].set_xlabel('', fontsize=14)
    if i == 0: axes[i].set_ylabel('Compound', fontsize=14)
    else: axes[i].set_ylabel('')

plt.tight_layout()
plt.show()
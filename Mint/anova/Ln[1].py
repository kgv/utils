import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plt
import seaborn as sns

# ==========================================
# 1. ЧТЕНИЕ И ПОДГОТОВКА ДАННЫХ
# ==========================================
df = pd.read_csv('_py/anova/Table1.csv', 
                 sep=',', 
                 header=0, 
                 names=['Line', 'Day', 'Fatty acid', 'Value'], 
                 skipinitialspace=True, 
                 encoding='utf-8-sig')

for col in df.columns:
    df[col] = df[col].astype(str).str.strip(' "')

df[['Mean', 'SD']] = df['Value'].str.split('±', expand=True).astype(float)

# ФИЛЬТРУЕМ ТОЛЬКО НУЖНУЮ ЖИРНУЮ КИСЛОТУ
TARGET_FA = '18:3n-3'
df = df[df['Fatty acid'] == TARGET_FA].copy()

# ==========================================
# 2. РАСЧЕТ СТАТИСТИКИ
# ==========================================
N_SAMPLES = 3  
CONTROL_LINE = '54 WT'
BASE_DAY = '0' 

days = sorted(df['Day'].unique(), key=int)
target_days = [d for d in days if d != BASE_DAY]
lines = df['Line'].unique()
exp_lines = [line for line in lines if line != CONTROL_LINE]

results_wt = []
results_day0 = []

# А) Сравнение с 54WT (для каждого дня)
for day in days:
    ctrl = df[(df['Line'] == CONTROL_LINE) & (df['Day'] == str(day))]
    if ctrl.empty: continue
    mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
    
    for exp in exp_lines:
        treat = df[(df['Line'] == exp) & (df['Day'] == str(day))]
        if treat.empty: continue
        mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
        
        t_stat, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                             mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
        
        f_stat = t_stat ** 2 # Вычисляем F-критерий
        results_wt.append({'Line': exp, 'Comparison': f'Day {day}', 'p_value': p_val, 'f_stat': f_stat})

# Б) Сравнение с Day 0 (для каждой линии, включая 54WT)
for line in lines:
    ctrl = df[(df['Line'] == line) & (df['Day'] == BASE_DAY)]
    if ctrl.empty: continue
    mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
    
    for day in target_days:
        treat = df[(df['Line'] == line) & (df['Day'] == day)]
        if treat.empty: continue
        mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
        
        t_stat, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                             mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
        
        f_stat = t_stat ** 2 # Вычисляем F-критерий
        results_day0.append({'Line': line, 'Comparison': f'Day {day}', 'p_value': p_val, 'f_stat': f_stat})

df_wt = pd.DataFrame(results_wt)
df_day0 = pd.DataFrame(results_day0)

# ==========================================
# 3. ФУНКЦИЯ АННОТАЦИИ И ПОДГОТОВКА МАТРИЦ
# ==========================================
# Функция теперь принимает строку датафрейма (row)
def get_annotation(row):
    p = row['p_value']
    f = row['f_stat']
    
    if pd.isna(p): return ''
    
    if p < 0.001: stars = '***'
    elif p < 0.01: stars = '**'
    elif p < 0.05: stars = '*'
    else: stars = 'ns'
    
    p_text = 'p<0.001' if p < 0.001 else f"p={p:.3f}"
    f_text = f"F={f:.2f}"
    
    return f"{f_text}\n{p_text}\n({stars})"

# Обработка датафрейма vs 54WT
if not df_wt.empty:
    df_wt['Annotation'] = df_wt.apply(get_annotation, axis=1) # Добавлен axis=1
    df_wt['Log_P'] = -np.log10(df_wt['p_value'])
    pivot_color_wt = df_wt.pivot(index='Line', columns='Comparison', values='Log_P')
    pivot_annot_wt = df_wt.pivot(index='Line', columns='Comparison', values='Annotation')
else:
    pivot_color_wt, pivot_annot_wt = pd.DataFrame(), pd.DataFrame()

# Обработка датафрейма vs Day 0
if not df_day0.empty:
    df_day0['Annotation'] = df_day0.apply(get_annotation, axis=1) # Добавлен axis=1
    df_day0['Log_P'] = -np.log10(df_day0['p_value'])
    pivot_color_day0 = df_day0.pivot(index='Line', columns='Comparison', values='Log_P')
    pivot_annot_day0 = df_day0.pivot(index='Line', columns='Comparison', values='Annotation')
else:
    pivot_color_day0, pivot_annot_day0 = pd.DataFrame(), pd.DataFrame()

# Синхронизируем порядок строк (Линий), чтобы 54WT был первым, а остальные по алфавиту
all_lines = [CONTROL_LINE] + sorted([l for l in lines if l != CONTROL_LINE])
pivot_color_wt = pivot_color_wt.reindex(index=all_lines).dropna(how='all', axis=1)
pivot_annot_wt = pivot_annot_wt.reindex(index=all_lines).dropna(how='all', axis=1)
pivot_color_day0 = pivot_color_day0.reindex(index=all_lines).dropna(how='all', axis=1)
pivot_annot_day0 = pivot_annot_day0.reindex(index=all_lines).dropna(how='all', axis=1)

# ==========================================
# 4. ВИЗУАЛИЗАЦИЯ
# ==========================================
# Увеличил высоту графика с 6 до 8, чтобы 3 строки текста помещались комфортно
fig, axes = plt.subplots(1, 2, figsize=(12, 6), sharey=True, gridspec_kw={'width_ratios': [len(days), len(target_days)]})

# Левый хитмап: Сравнение с 54WT (Красный)
if not pivot_color_wt.empty:
    sns.heatmap(pivot_color_wt, annot=pivot_annot_wt, fmt='', cmap='Reds', 
                ax=axes[0], cbar=True, vmin=0, vmax=3,
                linewidths=1, linecolor='white', annot_kws={"size": 9})
    axes[0].set_title(f'vs {CONTROL_LINE}', fontsize=14, pad=10)
    axes[0].set_xlabel('', fontsize=14)
    axes[0].set_ylabel('', fontsize=14)

# Правый хитмап: Сравнение с Day 0 (Синий)
if not pivot_color_day0.empty:
    sns.heatmap(pivot_color_day0, annot=pivot_annot_day0, fmt='', cmap='Blues', 
                ax=axes[1], cbar=True, vmin=0, vmax=3,
                cbar_kws={'label': '-log(p-value)'},
                linewidths=1, linecolor='white', annot_kws={"size": 9})
    axes[1].set_title('vs Day 0', fontsize=14, pad=10)
    axes[1].set_xlabel('', fontsize=14)
    axes[1].set_ylabel('') 

plt.tight_layout()
plt.show()
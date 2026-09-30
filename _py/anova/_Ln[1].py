import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import matplotlib.colors as mcolors

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
CONTROL_LINE = '54WT'
BASE_DAY = '0' 

days = sorted(df['Day'].unique(), key=int)
lines = df['Line'].unique()

# Словари для хранения p-value: ключи (Line, Day)
data_wt = {}
data_day0 = {}

# А) Сравнение с 54WT (для каждого дня)
for day in days:
    ctrl = df[(df['Line'] == CONTROL_LINE) & (df['Day'] == str(day))]
    if ctrl.empty: continue
    mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
    
    for line in lines:
        if line == CONTROL_LINE: continue
        treat = df[(df['Line'] == line) & (df['Day'] == str(day))]
        if treat.empty: continue
        mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
        
        _, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                        mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
        data_wt[(line, str(day))] = p_val

# Б) Сравнение с Day 0 (для каждой линии)
for line in lines:
    ctrl = df[(df['Line'] == line) & (df['Day'] == BASE_DAY)]
    if ctrl.empty: continue
    mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
    
    for day in days:
        if str(day) == BASE_DAY: continue
        treat = df[(df['Line'] == line) & (df['Day'] == str(day))]
        if treat.empty: continue
        mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
        
        _, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                        mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
        data_day0[(line, str(day))] = p_val

# ==========================================
# 3. ФУНКЦИЯ АННОТАЦИИ (в одну строку)
# ==========================================
def get_annotation(p):
    if pd.isna(p): return ''
    if p < 0.001: stars = '***'
    elif p < 0.01: stars = '**'
    elif p < 0.05: stars = '*'
    else: stars = 'ns'
    
    p_text = '<0.001' if p < 0.001 else f"{p:.3f}"
    return f"{p_text} ({stars})"

# ==========================================
# 4. ОТРИСОВКА ДИАГОНАЛЬНОГО ХИТМАПА
# ==========================================
all_lines = [CONTROL_LINE] + sorted([l for l in lines if l != CONTROL_LINE])
all_days = days

fig, ax = plt.subplots(figsize=(12, 8))

# Настройки цветовых шкал
cmap_wt = plt.cm.Reds
cmap_day0 = plt.cm.Blues
norm = mcolors.Normalize(vmin=0, vmax=3)

# Настраиваем оси (инвертируем Y, чтобы было как в таблице)
ax.set_xlim(0, len(all_days))
ax.set_ylim(len(all_lines), 0)

for i, line in enumerate(all_lines):
    for j, day in enumerate(all_days):
        day_str = str(day)
        
        # Получаем p-value (если нет сравнения, будет NaN)
        p_wt = data_wt.get((line, day_str), np.nan)
        p_d0 = data_day0.get((line, day_str), np.nan)
        
        # Вычисляем цвета (белый для пустых ячеек)
        color_wt = cmap_wt(norm(-np.log10(p_wt))) if not pd.isna(p_wt) else 'white'
        color_d0 = cmap_day0(norm(-np.log10(p_d0))) if not pd.isna(p_d0) else 'white'
        
        # Рисуем ВЕРХНИЙ ПРАВЫЙ треугольник (vs 54WT)
        poly_wt = Polygon([(j, i), (j+1, i), (j+1, i+1)], facecolor=color_wt, edgecolor='white', lw=1)
        ax.add_patch(poly_wt)
        
        # Рисуем НИЖНИЙ ЛЕВЫЙ треугольник (vs Day 0)
        poly_d0 = Polygon([(j, i), (j+1, i+1), (j, i+1)], facecolor=color_d0, edgecolor='white', lw=1)
        ax.add_patch(poly_d0)
        
        # Добавляем текст
        if not pd.isna(p_wt):
            text_color = 'white' if -np.log10(p_wt) > 1.5 else 'black'
            ax.text(j + 0.65, i + 0.35, get_annotation(p_wt), 
                    ha='center', va='center', fontsize=8, color=text_color, rotation=-45)
            
        if not pd.isna(p_d0):
            text_color = 'white' if -np.log10(p_d0) > 1.5 else 'black'
            ax.text(j + 0.35, i + 0.65, get_annotation(p_d0), 
                    ha='center', va='center', fontsize=8, color=text_color, rotation=-45)

        # Рисуем рамку вокруг всей ячейки
        rect = Rectangle((j, i), 1, 1, fill=False, edgecolor='white', lw=2)
        ax.add_patch(rect)

# Настройка подписей осей
ax.set_xticks(np.arange(len(all_days)) + 0.5)
ax.set_xticklabels([f"Day {d}" for d in all_days], fontsize=12)
ax.set_yticks(np.arange(len(all_lines)) + 0.5)
ax.set_yticklabels(all_lines, fontsize=12)

# Убираем стандартные рамки графика
for spine in ax.spines.values():
    spine.set_visible(False)
ax.tick_params(left=False, bottom=False)

# Добавляем ДВЕ цветовые шкалы (Colorbars)
sm_wt = plt.cm.ScalarMappable(cmap=cmap_wt, norm=norm)
sm_wt.set_array([])
cbar_wt = fig.colorbar(sm_wt, ax=ax, fraction=0.03, pad=0.02)
cbar_wt.set_label('-log(p-value) vs 54WT (Reds)', rotation=270, labelpad=15)

sm_d0 = plt.cm.ScalarMappable(cmap=cmap_day0, norm=norm)
sm_d0.set_array([])
cbar_d0 = fig.colorbar(sm_d0, ax=ax, fraction=0.03, pad=0.08)
cbar_d0.set_label('-log(p-value) vs Day 0 (Blues)', rotation=270, labelpad=15)

# Заголовок
plt.title(f'Statistical Analysis for {TARGET_FA}\n'
          f'Top-Right triangle: vs Control (54WT) | Bottom-Left triangle: vs Baseline (Day 0)', 
          fontsize=14, pad=20)

plt.tight_layout()
plt.show()
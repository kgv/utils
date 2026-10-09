import polars as pl
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
import seaborn as sns
import matplotlib.pyplot as plt

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
print(f"df: {df}")

# ==========================================
# 1. ПОДГОТОВКА ДАННЫХ В POLARS
# ==========================================

# 1. Исключаем внутренний стандарт и считаем log1p_ppm = ln(1 + ppm)
df_calc = df.filter(pl.col("FattyAcid") != "17:0").with_columns(
    log1p_ppm = pl.col("ppm").log1p()
)

# 2. Группируем данные: собираем все значения в списки
df_agg = df_calc.group_by(["Week", "FattyAcid", "Ni"]).agg(
    values = pl.col("log1p_ppm")
)

# 3. Разделяем на контроль (Ni = 0) и опыт (Ni > 0)
df_ctrl = df_agg.filter(pl.col("Ni") == 0).select(
    pl.col("Week"),
    pl.col("FattyAcid"),
    pl.col("values").alias("ctrl_values")
)

df_treat = df_agg.filter(pl.col("Ni") != 0).select(
    pl.col("Week"),
    pl.col("FattyAcid"),
    pl.col("Ni"),
    pl.col("values").alias("treat_values")
)

# 4. Соединяем опыт с контролем
df_joined = df_treat.join(df_ctrl, on=["Week", "FattyAcid"], how="left")

# ==========================================
# 2. СТАТИСТИКА (SCIPY)
# ==========================================

treat_lists = df_joined["treat_values"].to_list()
ctrl_lists = df_joined["ctrl_values"].to_list()

p_values = []
f_stats = []

# Прогоняем через стандартный t-test из scipy
for t_vals, c_vals in zip(treat_lists, ctrl_lists):
    # Очищаем от возможных None/NaN
    t_clean = [x for x in t_vals if x is not None and not np.isnan(x)]
    c_clean = [x for x in c_vals if x is not None and not np.isnan(x)]
    
    # t-test требует минимум 2 значения в каждой группе
    if len(t_clean) >= 2 and len(c_clean) >= 2:
        # Welch's t-test (equal_var=False)
        t_stat, p_val = ttest_ind(t_clean, c_clean, equal_var=False)
        
        p_values.append(p_val)
        # Вычисляем F-критерий (квадрат t-критерия для двух групп)
        f_stats.append(t_stat ** 2 if t_stat is not None else np.nan)
    else:
        p_values.append(np.nan)
        f_stats.append(np.nan)

# Возвращаем результаты обратно в Polars
df_joined = df_joined.with_columns(
    p_value = pl.Series(p_values),
    f_stat = pl.Series(f_stats)
)

# ==========================================
# 3. ВИЗУАЛИЗАЦИЯ (PANDAS + SEABORN)
# ==========================================

# Конвертируем в Pandas для удобного форматирования текста и отрисовки
df_plot = df_joined.select(["Week", "FattyAcid", "Ni", "p_value", "f_stat"]).to_pandas()

# Вычисляем -log10(p-value) для цветовой шкалы
df_plot['Log_P'] = -np.log10(df_plot['p_value'].astype(float))

# Функция аннотации из вашего примера
def get_annotation(row):
    p = row['p_value']
    f = row['f_stat']
    
    if pd.isna(p) or pd.isna(f): return ''
    
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
        
    # Форматируем F-статистику
    f_text = f"F={f:.2f}"
        
    # Возвращаем F, p-value и звездочки на новых строках
    return f"{f_text}\n{p_text}\n({stars})"

# Применяем функцию ко всем строкам
df_plot['Annotation'] = df_plot.apply(get_annotation, axis=1)

# Получаем список недель для графиков
weeks = sorted(df_plot['Week'].unique())

# Настраиваем холст (высота 8-10 отлично подходит для 3 строк текста в ячейке)
fig, axes = plt.subplots(1, len(weeks), figsize=(14, 10), sharey=True)
if len(weeks) == 1: axes = [axes]

for i, week in enumerate(weeks):
    week_data = df_plot[df_plot['Week'] == week]
    if week_data.empty: continue
        
    # Создаем сводные таблицы для цвета и текста
    pivot_color = week_data.pivot(index='FattyAcid', columns='Ni', values='Log_P')
    pivot_annot = week_data.pivot(index='FattyAcid', columns='Ni', values='Annotation')

    # Строим Heatmap в вашем стиле
    sns.heatmap(
        pivot_color, 
        annot=pivot_annot, 
        fmt='', 
        cmap='Blues', 
        ax=axes[i], 
        cbar=(i == len(weeks)-1), 
        vmin=0, vmax=3, 
        cbar_kws={'label': '-log(p-value)'} if i == len(weeks)-1 else None,
        linewidths=1, 
        linecolor='white',
        annot_kws={"size": 9} # Размер шрифта 9 отлично подходит для 3 строк
    )
    
    axes[i].set_title(f'Week {week}', fontsize=14)
    axes[i].set_xlabel('Ni (mM)', fontsize=14)
    if i == 0: 
        axes[i].set_ylabel('Fatty acid', fontsize=14)
    else: 
        axes[i].set_ylabel('')

plt.tight_layout()
plt.show()
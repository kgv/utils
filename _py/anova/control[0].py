import pandas as pd
import numpy as np
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plt
import seaborn as sns
import io

# 1. Загрузка данных (используем строку для удобства, но можно заменить на pd.read_csv('file.csv'))
# csv_data = """"Line","Day","Fatty acid","Value"
# "54WT","0","16:0","15.7±1.11"
# "54WT","2","16:0","16.7±0.91"
# "54WT","7","16:0","17.8±2.58"
# "54WT","0","16:1n-7","2.7±0.04"
# "54WT","2","16:1n-7","2.0±0.16"
# "54WT","7","16:1n-7","2.1±0.08"
# "54WT","0","18:1n-9","14.7±2.28"
# "54WT","2","18:1n-9","13.5±0.68"
# "54WT","7","18:1n-9","15.2±0.41"
# "54WT","0","18:2n-6","16.0±2.42"
# "54WT","2","18:2n-6","14.7±0.66"
# "54WT","7","18:2n-6","18.6±1.28"
# "54WT","0","18:3n-3","46.6±1.00"
# "54WT","2","18:3n-3","49.1±0.39"
# "54WT","7","18:3n-3","41.4±3.42"
# "54WT","0","Others**","1.914±0.007"
# "54WT","2","Others**","1.941±0.009"
# "54WT","7","Others**","1.810±0.083"
# "CodA25","0","16:0","16.8±0.93"
# "CodA25","2","16:0","13.5±1.20"
# "CodA25","7","16:0","18.2±1.34"
# "CodA25","0","18:1n-9","13.1±0.83"
# "CodA25","2","18:1n-9","17.8±5.45"
# "CodA25","7","18:1n-9","17.9±0.38"
# "CodA25","0","18:2n-6","15.3±0.45"
# "CodA25","2","18:2n-6","13.0±1.72"
# "CodA25","7","18:2n-6","18.6±0.54"
# "CodA25","0","18:3n-3","48.4±2.67"
# "CodA25","2","18:3n-3","50.3±2.91"
# "CodA25","7","18:3n-3","37.4±1.72"
# "CodA25","0","Others**","1.937±0.06"
# "CodA25","2","Others**","1.985±0.062"
# "CodA25","7","Others**","1.724±0.042"
# "Cod A8","0","16:0","15.2±1.16"
# "Cod A8","2","16:0","14.8±0.11"
# "Cod A8","7","16:0","18.1±0.01"
# "Cod A8","0","18:1n-9","17.1±2.67"
# "Cod A8","2","18:1n-9","17.2±3.64"
# "Cod A8","7","18:1n-9","17.6±0.11"
# "Cod A8","0","18:2n-6","15.7±1.03"
# "Cod A8","2","18:2n-6","14.4±0.69"
# "Cod A8","7","18:2n-6","18.4±0.40"
# "Cod A8","0","18:3n-3","45.1±0.54"
# "Cod A8","2","18:3n-3","47.9±5.47"
# "Cod A8","7","18:3n-3","38.3±0.80"
# "Cod A8","0","Others**","1.884±0.01"
# "Cod A8","2","Others**","1.935±0.104"
# "Cod A8","7","Others**","1.738±0.014"
# "FeSOD11","0","16:0","14.3±0.33"
# "FeSOD11","2","16:0","15.9±0.88"
# "FeSOD11","7","16:0","18.0±0.11"
# "FeSOD11","0","18:1n-9","20.6±0.72"
# "FeSOD11","2","18:1n-9","17.3±1.73"
# "FeSOD11","7","18:1n-9","21.4±1.99"
# "FeSOD11","0","18:2n-6","14.6±0.04"
# "FeSOD11","2","18:2n-6","15.2±0.30"
# "FeSOD11","7","18:2n-6","18.7±0.78"
# "FeSOD11","0","18:3n-3","43.2±0.52"
# "FeSOD11","2","18:3n-3","46.4±2.36"
# "FeSOD11","7","18:3n-3","33.8±2.47"
# "FeSOD11","0","Others**","1.846±0.009"
# "FeSOD11","2","Others**","1.906±0.058"
# "FeSOD11","7","Others**","1.653±0.061"
# "FeSOD20","0","16:0","14.7±0.35"
# "FeSOD20","2","16:0","16.3±2.00"
# "FeSOD20","7","16:0","16.0±0.76"
# "FeSOD20","0","18:1n-9","19.4±0.34"
# "FeSOD20","2","18:1n-9","18.5±3.41"
# "FeSOD20","7","18:1n-9","22.0±1.05"
# "FeSOD20","0","18:2n-6","16.9±0.01"
# "FeSOD20","2","18:2n-6","16.4±0.40"
# "FeSOD20","7","18:2n-6","16.6±0.75"
# "FeSOD20","0","18:3n-3","41.8±0.62"
# "FeSOD20","2","18:3n-3","42.8±1.64"
# "FeSOD20","7","18:3n-3","37.4±2.84"
# "FeSOD20","0","Others**","3.4±0.24"
# "FeSOD20","2","Others**","2.7±0.10"
# "FeSOD20","7","Others**","4.1±0.1" """

# df = pd.read_csv(io.StringIO(csv_data))
try:
    df = pd.read_csv('_py/anova/Table1.csv', skipinitialspace=True, encoding='utf-8-sig')
except FileNotFoundError:
    print("Файл не найден. Проверьте путь к файлу.")
    exit()

print(df['Line'])

# 2. Предобработка данных: разделяем "Mean±SD" на две числовые колонки
df[['Mean', 'SD']] = df['Value'].str.split('±', expand=True).astype(float)

# 3. Настройки статистики
N_SAMPLES = 3  # ВАЖНО: Укажите здесь реальное количество повторностей (n) в вашем эксперименте!
CONTROL_LINE = '54WT'

results = []
exp_lines = [line for line in df['Line'].unique() if line != CONTROL_LINE]
days = sorted(df['Day'].unique(), key=int)
fatty_acids = df['Fatty acid'].unique()

# 4. Расчет t-критерия Стьюдента (сравнение каждой линии с 54WT)
for day in days:
    for fa in fatty_acids:
        # Данные контроля
        ctrl = df[(df['Line'] == CONTROL_LINE) & (df['Day'] == day) & (df['Fatty acid'] == fa)]
        if ctrl.empty:
            continue
        mean_c, sd_c = ctrl.iloc[0]['Mean'], ctrl.iloc[0]['SD']
        
        for exp in exp_lines:
            # Данные экспериментальной линии
            treat = df[(df['Line'] == exp) & (df['Day'] == day) & (df['Fatty acid'] == fa)]
            if treat.empty:
                continue
            mean_e, sd_e = treat.iloc[0]['Mean'], treat.iloc[0]['SD']
            
            # Независимый t-тест из сводной статистики
            t_stat, p_val = ttest_ind_from_stats(mean1=mean_c, std1=sd_c, nobs1=N_SAMPLES,
                                                 mean2=mean_e, std2=sd_e, nobs2=N_SAMPLES)
            
            results.append({
                'Day': day,
                'Fatty acid': fa,
                'Line': exp,
                'p_value': p_val
            })

res_df = pd.DataFrame(results)

# 5. Функция для перевода p-value в "звездочки" значимости
def get_significance_stars(p):
    if pd.isna(p): return ''
    if p < 0.001: return '***'
    elif p < 0.01: return '**'
    elif p < 0.05: return '*'
    else: return 'ns'

res_df['Significance'] = res_df['p_value'].apply(get_significance_stars)
# Для цвета на графике используем -log10(p-value). Чем больше значение, тем ярче цвет (выше значимость)
res_df['Log_P'] = -np.log10(res_df['p_value'])

# 6. Визуализация (Тепловая карта)
fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True)
fig.suptitle(f'Статистическая значимость отличий от контроля ({CONTROL_LINE})\n'
             f'Тест Стьюдента (n={N_SAMPLES}). ns: p>0.05, *: p<0.05, **: p<0.01, ***: p<0.001', 
             fontsize=14, y=1.05)

for i, day in enumerate(days):
    day_data = res_df[res_df['Day'] == day]
    
    # Создаем сводные таблицы для значений цвета и текста
    pivot_color = day_data.pivot(index='Fatty acid', columns='Line', values='Log_P')
    pivot_annot = day_data.pivot(index='Fatty acid', columns='Line', values='Significance')
    
    # Рисуем heatmap
    sns.heatmap(pivot_color, annot=pivot_annot, fmt='', cmap='Reds', 
                ax=axes[i], cbar=(i==2), vmin=0, vmax=3, 
                cbar_kws={'label': '-log10(p-value)'} if i==2 else None,
                linewidths=1, linecolor='white')
    
    axes[i].set_title(f'Day {day}', fontsize=12)
    axes[i].set_xlabel('Линия', fontsize=11)
    if i == 0:
        axes[i].set_ylabel('Жирная кислота', fontsize=11)
    else:
        axes[i].set_ylabel('')

plt.tight_layout()
plt.show()
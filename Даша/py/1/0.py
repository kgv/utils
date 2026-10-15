import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import re
from matplotlib.ticker import MaxNLocator

# 1. Исходные данные
raw_data = """
## Comparison: 0.5_50.5

|              | average|     sd|  ratio|       ava|       avb| cumsum|     p|signif |
|:-------------|-------:|------:|------:|---------:|---------:|------:|-----:|:------|
|9,12,15-18:3  |  0.0415| 0.0285| 1.4548| 7860.6756| 6485.0107| 0.3143| 0.956|       |
|9,12-18:2     |  0.0249| 0.0181| 1.3745| 5453.8554| 5960.6109| 0.5031| 0.994|       |
|16:0          |  0.0201| 0.0151| 1.3303| 4434.6840| 4052.7435| 0.6551| 0.989|       |
|11-18:1       |  0.0092| 0.0064| 1.4283| 1500.4307| 1365.8994| 0.7248| 0.802|       |
|9-16:1        |  0.0084| 0.0060| 1.4018| 1724.6175| 1578.8770| 0.7886| 0.920|       |
|11-Me-12-18:1 |  0.0072| 0.0053| 1.3681| 1528.8927| 1463.6530| 0.8433| 0.990|       |
|18:0          |  0.0060| 0.0043| 1.4027|  876.7336|  610.9233| 0.8891| 0.401|       |
|9-18:1        |  0.0050| 0.0035| 1.4301|  379.6397|  498.8513| 0.9271| 1.000|       |
|20:0          |  0.0023| 0.0017| 1.3005|  450.4366|  396.1978| 0.9441| 0.959|       |
|7,10-16:2     |  0.0019| 0.0011| 1.6543|  240.8422|  165.0893| 0.9585| 0.564|       |
|22:0          |  0.0017| 0.0015| 1.1819|  289.1153|  272.1903| 0.9717| 0.986|       |
|24:0          |  0.0016| 0.0014| 1.1254|  315.7018|  288.8792| 0.9835| 1.000|       |
|12,15-18:2    |  0.0006| 0.0004| 1.3374|   94.0142|   98.4398| 0.9878| 0.965|       |
|15-24:1       |  0.0005| 0.0004| 1.4349|   78.8495|   71.5148| 0.9918| 0.962|       |
|di-16:0       |  0.0005| 0.0003| 1.3750|   32.2206|   49.0436| 0.9954| 0.881|       |
|14:0          |  0.0004| 0.0003| 1.4238|   52.3196|   56.5545| 0.9985| 0.409|       |
|23:0          |  0.0001| 0.0001| 1.2866|   12.3809|   11.7108| 0.9993| 0.851|       |
|26:0          |  0.0001| 0.0001| 1.3286|   11.8129|   12.7689| 1.0000| 1.000|       |

## Comparison: 0.5_250.5

|              | average|     sd|  ratio|       ava|       avb| cumsum|     p|signif |
|:-------------|-------:|------:|------:|---------:|---------:|------:|-----:|:------|
|9,12,15-18:3  |  0.0607| 0.0303| 2.0027| 7860.6756| 5058.9200| 0.3738| 0.427|       |
|16:0          |  0.0253| 0.0123| 2.0560| 4434.6840| 3370.8075| 0.5299| 0.914|       |
|9,12-18:2     |  0.0229| 0.0186| 1.2334| 5453.8554| 5794.6465| 0.6709| 0.998|       |
|9-18:1        |  0.0102| 0.0051| 1.9980|  379.6397|  836.2470| 0.7334| 0.990|       |
|9-16:1        |  0.0090| 0.0057| 1.5839| 1724.6175| 1620.2147| 0.7886| 0.892|       |
|11-Me-12-18:1 |  0.0075| 0.0052| 1.4350| 1528.8927| 1364.0366| 0.8349| 0.982|       |
|18:0          |  0.0072| 0.0044| 1.6502|  876.7336|  543.9066| 0.8791| 0.221|       |
|11-18:1       |  0.0064| 0.0046| 1.4103| 1500.4307| 1482.9568| 0.9187| 0.976|       |
|20:0          |  0.0034| 0.0023| 1.4624|  450.4366|  289.2727| 0.9396| 0.647|       |
|7,10-16:2     |  0.0029| 0.0013| 2.1720|  240.8422|  106.4979| 0.9574| 0.029|*      |
|22:0          |  0.0027| 0.0020| 1.3688|  289.1153|  170.2244| 0.9741| 0.611|       |
|24:0          |  0.0019| 0.0011| 1.8037|  315.7018|  236.3110| 0.9859| 0.999|       |
|12,15-18:2    |  0.0008| 0.0006| 1.3505|   94.0142|  115.4747| 0.9909| 0.661|       |
|15-24:1       |  0.0006| 0.0003| 1.8488|   78.8495|   56.1248| 0.9944| 0.945|       |
|14:0          |  0.0004| 0.0002| 1.8242|   52.3196|   35.3482| 0.9967| 0.486|       |
|di-16:0       |  0.0003| 0.0003| 1.2541|   32.2206|   30.0840| 0.9987| 0.997|       |
|26:0          |  0.0001| 0.0001| 1.3399|   11.8129|   17.2597| 0.9996| 0.989|       |
|23:0          |  0.0001| 0.0000| 1.3555|   12.3809|   12.4626| 1.0000| 0.988|       |
"""

# 2. Парсинг данных (Polars)
blocks = raw_data.strip().split("## Comparison: ")
all_data = []

for block in blocks[1:]:
    lines = block.strip().split('\n')
    comp_name = lines[0].strip()
    
    # Очистка markdown-таблицы от лишних символов для корректного чтения
    cleaned_lines = []
    for line in lines[1:]:
        line = line.strip()
        if not line or re.match(r'^\|[:\-]+', line):
            continue
        if line.startswith('|'): line = line[1:]
        if line.endswith('|'): line = line[:-1]
        cleaned_lines.append(line)
        
    table_str = "\n".join(cleaned_lines)
    
    # Читаем через Polars
    df = pl.read_csv(io.StringIO(table_str), separator='|', null_values=[""])
    df.columns = [c.strip() for c in df.columns]
    df = df.rename({df.columns[0]: "Feature"})
    
    # Убираем пробелы в строковых колонках
    df = df.with_columns([pl.col(pl.String).str.strip_chars()])
    df = df.with_columns(pl.lit(comp_name).alias("Comparison"))
    all_data.append(df)

full_df = pl.concat(all_data)
full_df = full_df.with_columns(pl.col("signif").fill_null(""))

# 3. Подготовка данных
# Оставляем только сравнения с контролем 0.5 и извлекаем дозу
df_control = full_df.filter(pl.col("Comparison").str.starts_with("0.5_"))
df_control = df_control.with_columns(
    pl.col("Comparison").str.split("_").list.get(1).str.replace(".5", "").cast(pl.Int32).alias("Dose")
)

# Вычисляем позицию (ранг) кислоты по её вкладу (average) ДО фильтрации
df_control = df_control.with_columns(
    pl.col("average").rank(method="min", descending=True).over("Dose").alias("Rank")
)

# Оставляем только те кислоты, у которых p <= 0.05 хотя бы раз
sig_features = (
    df_control.filter(pl.col("p") <= 0.05)
    .select("Feature")
    .unique()
    .to_series()
    .to_list()
)
df_control = df_control.filter(pl.col("Feature").is_in(sig_features))

# Сортируем оставшиеся значимые кислоты по их среднему вкладу (average)
feature_importance = (
    df_control.group_by("Feature")
    .agg(pl.col("average").mean().alias("mean_avg"))
    .sort("mean_avg", descending=True)
)
all_features = feature_importance.get_column("Feature").to_list()
n_features = len(all_features)

# 4. Построение единой сетки графиков
sns.set_theme(style="whitegrid")

# 4 колонки: Концентрация (ava/avb), Вклад (average+sd), Ранг, p-value
fig, axes = plt.subplots(nrows=n_features, ncols=4, figsize=(20, 3.5 * n_features))
axes = np.atleast_2d(axes) # Защита от ошибки, если n_features == 1

fig.suptitle(f'Профиль SIMPER: {n_features} статистически значимых жирных кислот (p ≤ 0.05)', 
             fontsize=22, weight='bold', y=0.99)

metric_titles = ['Концентрация (ava / avb)', 'Собственный вклад (Average ± SD)', 'Позиция (Ранг)', 'p-value (Значимость)']

for row_idx, feature in enumerate(all_features):
    # Фильтруем данные для конкретной кислоты и переводим в pandas для удобства отрисовки в matplotlib
    feat_df = df_control.filter(pl.col("Feature") == feature).sort("Dose").to_pandas()
    
    # --- 1. Концентрация (ava и avb на одном графике) ---
    ax0 = axes[row_idx, 0]
    ax0.plot(feat_df['Dose'], feat_df['ava'], color='#2b7bba', marker='o', markersize=8, linewidth=2, label='ava (Контроль)')
    ax0.plot(feat_df['Dose'], feat_df['avb'], color='#f0ad4e', marker='s', markersize=8, linewidth=2, label='avb (Опыт)')
    ax0.set_xticks([50, 250, 500, 750, 1000])
    ax0.set_ylabel(f"{feature}\n\nЗначение", fontsize=14, weight='bold')
    if row_idx == 0:
        ax0.legend(fontsize=11, loc='best')
    
    # --- 2. Собственный вклад (Average + SD) ---
    ax1 = axes[row_idx, 1]
    # Столбчатая диаграмма с усами (ширина 80 подобрана так, чтобы столбцы не слипались при шаге доз)
    ax1.bar(feat_df['Dose'], feat_df['average'], yerr=feat_df['sd'], 
            width=80, capsize=5, color='#d9534f', alpha=0.8, edgecolor='black')
    ax1.set_xticks([50, 250, 500, 750, 1000])
    ax1.set_ylabel('')
    
    # --- 3. Позиция (Ранг) ---
    ax2 = axes[row_idx, 2]
    ax2.plot(feat_df['Dose'], feat_df['Rank'], color='#5cb85c', marker='v', markersize=8, linewidth=2)
    ax2.set_xticks([50, 250, 500, 750, 1000])
    ax2.invert_yaxis() # Инвертируем ось Y, чтобы 1-е место было сверху
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True)) # Только целые числа на оси Y
    ax2.set_ylabel('')
    
    # --- 4. p-value ---
    ax3 = axes[row_idx, 3]
    ax3.plot(feat_df['Dose'], feat_df['p'], color='#9b59b6', marker='D', markersize=8, linewidth=2)
    ax3.axhline(0.05, ls="--", color="red", alpha=0.7)
    
    # Подписи значимости
    for _, row in feat_df.iterrows():
        if row['signif'] and str(row['signif']).strip() not in ['', '.']:
            ax3.text(row['Dose'], row['p'] + 0.02, row['signif'], color='red', fontsize=14, ha='center', va='bottom', weight='bold')
            
    ax3.set_xticks([50, 250, 500, 750, 1000])
    ax3.set_ylabel('')

    # Настройка заголовков колонок (только для самого верхнего ряда)
    if row_idx == 0:
        for col_idx in range(4):
            axes[row_idx, col_idx].set_title(metric_titles[col_idx], fontsize=14, weight='bold', pad=15)
            
    # Настройка подписей оси X (только для самого нижнего ряда)
    for col_idx in range(4):
        if row_idx == n_features - 1:
            axes[row_idx, col_idx].set_xlabel('Доза Ni', fontsize=12, weight='bold')
        else:
            axes[row_idx, col_idx].set_xlabel('')

# Финальная компоновка
plt.tight_layout(rect=[0, 0, 1, 0.98])
plt.show()

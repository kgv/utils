import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re

# 1. Исходные данные (вставьте сюда ВЕСЬ ваш текст с данными)
raw_data = """
## Comparison: 0.5_50.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0359| 0.0205| 1.7456| 16978.5387| 18583.5510| 0.4214| 0.945|       |
|9,12-18:2     |  0.0203| 0.0100| 2.0312|  7401.5605|  8914.1905| 0.6602| 0.648|       |
|16:0          |  0.0099| 0.0071| 1.3996|  5615.1719|  5831.3829| 0.7767| 0.918|       |
|9-18:1        |  0.0052| 0.0035| 1.4780|  1190.9974|  1242.0650| 0.8383| 0.647|       |
|11-18:1       |  0.0037| 0.0031| 1.2025|  1086.1698|   839.2239| 0.9315| 0.152|       |

## Comparison: 0.5_250.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0176| 0.0128| 1.3772| 16978.5387| 16953.4916| 0.3320| 1.000|       |
|16:0          |  0.0084| 0.0061| 1.3797|  5615.1719|  5227.6227| 0.4906| 0.978|       |
|9,12-18:2     |  0.0075| 0.0049| 1.5381|  7401.5605|  7349.3197| 0.6320| 1.000|       |
|11-18:1       |  0.0059| 0.0038| 1.5381|  1086.1698|   686.3901| 0.7433| 0.001|***    |
|9-18:1        |  0.0055| 0.0026| 2.0920|  1190.9974|  1193.6932| 0.8473| 0.536|       |

## Comparison: 0.5_500.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0465| 0.0177| 2.6276| 16978.5387| 13948.9169| 0.5339| 0.697|       |
|16:0          |  0.0105| 0.0070| 1.5022|  5615.1719|  4969.0048| 0.6550| 0.862|       |
|9,12-18:2     |  0.0085| 0.0060| 1.4151|  7401.5605|  7665.9470| 0.7527| 1.000|       |
|9-18:1        |  0.0059| 0.0041| 1.4464|  1190.9974|   973.9375| 0.8203| 0.406|       |
|11-18:1       |  0.0057| 0.0033| 1.7424|  1086.1698|   719.4310| 0.8862| 0.001|***    |

## Comparison: 0.5_750.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0564| 0.0250| 2.2588| 16978.5387| 13540.5617| 0.5003| 0.300|       |
|9,12-18:2     |  0.0166| 0.0060| 2.7483|  7401.5605|  6851.8410| 0.6478| 0.896|       |
|16:0          |  0.0161| 0.0090| 1.7794|  5615.1719|  4724.0218| 0.7906| 0.166|       |
|11-18:1       |  0.0066| 0.0036| 1.7982|  1086.1698|   671.6703| 0.8487| 0.001|***    |
|9-18:1        |  0.0059| 0.0030| 1.9682|  1190.9974|  1289.0113| 0.9013| 0.382|       |

## Comparison: 0.5_1000.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0722| 0.0270| 2.6693| 16978.5387| 12540.0819| 0.5203| 0.016|*      |
|16:0          |  0.0213| 0.0096| 2.2242|  5615.1719|  4302.5573| 0.6737| 0.004|**     |
|9,12-18:2     |  0.0197| 0.0115| 1.7076|  7401.5605|  6362.3532| 0.8156| 0.678|       |
|9-18:1        |  0.0074| 0.0045| 1.6374|  1190.9974|  1404.5302| 0.8688| 0.063|.      |
|11-18:1       |  0.0062| 0.0043| 1.4359|  1086.1698|   712.3420| 0.9134| 0.001|***    |
"""

# 2. Парсинг данных
blocks = raw_data.strip().split("## Comparison: ")
all_data = []

for block in blocks[1:]:
    lines = block.strip().split('\n')
    comp_name = lines[0].strip()
    table_str = "\n".join(lines[1:])
    table_str = re.sub(r'\|:--.*', '', table_str) 
    table_str = "\n".join([line for line in table_str.split('\n') if line.strip()])
    
    df = pd.read_csv(io.StringIO(table_str), sep='|', skipinitialspace=True)
    df = df.dropna(axis=1, how='all')
    df.columns = [col.strip() for col in df.columns]
    df = df.rename(columns={'Unnamed: 1': 'Feature'})
    df['Feature'] = df['Feature'].str.strip()
    df['Comparison'] = comp_name
    all_data.append(df)

full_df = pd.concat(all_data, ignore_index=True)
full_df['signif'] = full_df['signif'].fillna('').str.strip()

# 3. Подготовка данных (только сравнения с контролем 0.5)
df_control = full_df[full_df['Comparison'].str.startswith('0.5_')].copy()
df_control['Dose'] = df_control['Comparison'].apply(lambda x: int(float(x.split('_')[1].replace('.5', ''))))

# Топ-5 самых важных кислот
top_features = ['9,12,15-18:3', '16:0', '9,12-18:2', '9-18:1', '11-18:1']
df_top = df_control[df_control['Feature'].isin(top_features)].copy()

# Данные для графика концентрации (добавляем точку Dose=0)
control_vals = df_top[['Feature', 'ava']].drop_duplicates(subset=['Feature']).rename(columns={'ava': 'Value'})
control_vals['Dose'] = 0
treated_vals = df_top[['Feature', 'avb', 'Dose']].rename(columns={'avb': 'Value'})
trend_df = pd.concat([control_vals, treated_vals], ignore_index=True)

# 4. Построение единой сетки графиков (4 строки, 5 колонок)
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(nrows=4, ncols=5, figsize=(22, 16))
fig.suptitle('Комплексный анализ SIMPER: Влияние дозы Ni на профиль жирных кислот', fontsize=22, weight='bold', y=0.98)

# Цвета для разных метрик
colors = ['#2b7bba', '#d9534f', '#5cb85c', '#9b59b6']
markers = ['o', 's', '^', 'D']

for col_idx, feature in enumerate(top_features):
    # Фильтруем данные для конкретной кислоты
    feat_trend = trend_df[trend_df['Feature'] == feature].sort_values('Dose')
    feat_simper = df_top[df_top['Feature'] == feature].sort_values('Dose')
    
    # --- СТРОКА 1: Концентрация (ppm) ---
    ax0 = axes[0, col_idx]
    sns.lineplot(data=feat_trend, x='Dose', y='Value', ax=ax0, color=colors[0], marker=markers[0], markersize=8, linewidth=2)
    ax0.set_title(feature, fontsize=16, weight='bold', pad=15) # Название кислоты только сверху
    ax0.set_xticks([0, 50, 250, 500, 750, 1000])
    ax0.set_xlabel('')
    if col_idx == 0: ax0.set_ylabel('Концентрация (ppm)', fontsize=12, weight='bold')
    else: ax0.set_ylabel('')

    # --- СТРОКА 2: Ratio ---
    ax1 = axes[1, col_idx]
    sns.lineplot(data=feat_simper, x='Dose', y='ratio', ax=ax1, color=colors[1], marker=markers[1], markersize=8, linewidth=2)
    ax1.set_xticks([50, 250, 500, 750, 1000])
    ax1.set_xlabel('')
    if col_idx == 0: ax1.set_ylabel('Ratio (Вклад/SD)', fontsize=12, weight='bold')
    else: ax1.set_ylabel('')

    # --- СТРОКА 3: CumSum ---
    ax2 = axes[2, col_idx]
    sns.lineplot(data=feat_simper, x='Dose', y='cumsum', ax=ax2, color=colors[2], marker=markers[2], markersize=8, linewidth=2)
    ax2.set_xticks([50, 250, 500, 750, 1000])
    ax2.set_xlabel('')
    if col_idx == 0: ax2.set_ylabel('CumSum (Доля)', fontsize=12, weight='bold')
    else: ax2.set_ylabel('')

    # --- СТРОКА 4: p-value и значимость ---
    ax3 = axes[3, col_idx]
    sns.lineplot(data=feat_simper, x='Dose', y='p', ax=ax3, color=colors[3], marker=markers[3], markersize=8, linewidth=2)
    ax3.axhline(0.05, ls="--", color="red", alpha=0.7) # Линия порога значимости
    
    # Добавляем звездочки значимости
    for _, row in feat_simper.iterrows():
        if row['signif']:
            ax3.text(row['Dose'], row['p'] + 0.02, row['signif'], 
                     color='red', fontsize=14, ha='center', va='bottom', weight='bold')
            
    ax3.set_xticks([50, 250, 500, 750, 1000])
    ax3.set_xlabel('Доза Ni', fontsize=12, weight='bold') # Подпись оси X только в самом низу
    if col_idx == 0: ax3.set_ylabel('p-value', fontsize=12, weight='bold')
    else: ax3.set_ylabel('')

# Настройка отступов, чтобы графики не слипались
plt.tight_layout()
fig.subplots_adjust(top=0.92, hspace=0.3, wspace=0.25)
plt.show()
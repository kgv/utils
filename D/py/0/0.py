import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re

# 1. Вставляем ваши исходные данные (я сократил текст для удобства, 
# скрипт автоматически распарсит все таблицы)
raw_data = """
## Comparison: 0.5_50.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0359| 0.0205| 1.7456| 16978.5387| 18583.5510| 0.4214| 0.945|       |
|9,12-18:2     |  0.0203| 0.0100| 2.0312|  7401.5605|  8914.1905| 0.6602| 0.648|       |
|16:0          |  0.0099| 0.0071| 1.3996|  5615.1719|  5831.3829| 0.7767| 0.918|       |
|9-18:1        |  0.0052| 0.0035| 1.4780|  1190.9974|  1242.0650| 0.8383| 0.647|       |
|7,10,13-16:3  |  0.0042| 0.0036| 1.1711|  1228.4041|  1503.6457| 0.8876| 0.926|       |
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
    
    # Читаем таблицу
    table_str = "\n".join(lines[1:])
    # Убираем markdown разметку таблиц
    table_str = re.sub(r'\|:--.*', '', table_str) 
    table_str = "\n".join([line for line in table_str.split('\n') if line.strip()])
    
    df = pd.read_csv(io.StringIO(table_str), sep='|', skipinitialspace=True)
    df = df.dropna(axis=1, how='all') # Удаляем пустые колонки по краям
    df.columns = [col.strip() for col in df.columns]
    df = df.rename(columns={'Unnamed: 1': 'Feature'})
    df['Feature'] = df['Feature'].str.strip()
    df['Comparison'] = comp_name
    all_data.append(df)

full_df = pd.concat(all_data, ignore_index=True)

# Настройка стиля графиков
sns.set_theme(style="whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# ==========================================
# ГРАФИК 1: Тепловая карта вкладов (Control vs Ni)
# ==========================================
plt.figure(figsize=(10, 6))
# Фильтруем только сравнения с контролем (0.5)
control_comps = full_df[full_df['Comparison'].str.startswith('0.5_')]
pivot_df = control_comps.pivot(index='Feature', columns='Comparison', values='average').fillna(0)

# Оставляем топ-10 кислот по суммарному вкладу
top_features = pivot_df.sum(axis=1).nlargest(10).index
pivot_df = pivot_df.loc[top_features]

sns.heatmap(pivot_df, annot=True, cmap="YlOrRd", fmt=".4f", linewidths=.5)
plt.title("Тепловая карта: Вклад жирных кислот в различия (SIMPER Average)\nКонтроль (0.5) против разных доз Ni", fontsize=14)
plt.ylabel("Жирные кислоты")
plt.xlabel("Сравнение групп")
plt.tight_layout()
plt.show()

# ==========================================
# ГРАФИК 2: Изменение концентраций (0.5 vs 1000.5)
# ==========================================
plt.figure(figsize=(12, 6))
df_extreme = full_df[full_df['Comparison'] == '0.5_1000.5'].head(8) # Топ 8 кислот

# Подготовка данных для сгруппированного барплота
melted = df_extreme.melt(id_vars='Feature', value_vars=['ava', 'avb'], 
                         var_name='Group', value_name='Abundance')
melted['Group'] = melted['Group'].map({'ava': 'Контроль (Ni=0)', 'avb': 'Стресс (Ni=1000)'})

sns.barplot(data=melted, x='Feature', y='Abundance', hue='Group', palette=['#4C72B0', '#C44E52'])
plt.title("Изменение содержания топ-8 жирных кислот\nКонтроль (0.5) vs Максимальная доза (1000.5)", fontsize=14)
plt.ylabel("Концентрация (PartsPerMillion_DryWeight)")
plt.xlabel("Жирные кислоты")
plt.xticks(rotation=45)
plt.legend(title="Группа")
plt.tight_layout()
plt.show()

# ==========================================
# ГРАФИК 3: Кумулятивный вклад (Pareto) для 0.5 vs 250.5
# ==========================================
plt.figure(figsize=(10, 5))
df_pareto = full_df[full_df['Comparison'] == '0.5_250.5'].head(10)

ax1 = sns.barplot(data=df_pareto, x='Feature', y='average', color='skyblue', label='Вклад (average)')
ax2 = ax1.twinx()
sns.lineplot(data=df_pareto, x='Feature', y='cumsum', color='red', marker='o', ax=ax2, label='Кумулятивный вклад')

ax1.set_ylabel('Вклад в различия (Average)')
ax2.set_ylabel('Кумулятивная доля (CumSum)')
plt.title("SIMPER Профиль: Контроль (0.5) vs Ni=250.5", fontsize=14)
ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
plt.tight_layout()
plt.show()
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import re

# 1. Исходные данные (сокращены для примера, скрипт поймет структуру)
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
|7,10,13-16:3  |  0.0020| 0.0015| 1.3503|  1228.4041|  1220.3270| 0.8851| 1.000|       |

## Comparison: 0.5_500.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0465| 0.0177| 2.6276| 16978.5387| 13948.9169| 0.5339| 0.697|       |
|16:0          |  0.0105| 0.0070| 1.5022|  5615.1719|  4969.0048| 0.6550| 0.862|       |
|9,12-18:2     |  0.0085| 0.0060| 1.4151|  7401.5605|  7665.9470| 0.7527| 1.000|       |
|9-18:1        |  0.0059| 0.0041| 1.4464|  1190.9974|   973.9375| 0.8203| 0.406|       |
|11-18:1       |  0.0057| 0.0033| 1.7424|  1086.1698|   719.4310| 0.8862| 0.001|***    |
|7,10,13-16:3  |  0.0037| 0.0023| 1.6269|  1228.4041|  1028.9007| 0.9289| 0.978|       |

## Comparison: 0.5_750.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0564| 0.0250| 2.2588| 16978.5387| 13540.5617| 0.5003| 0.300|       |
|9,12-18:2     |  0.0166| 0.0060| 2.7483|  7401.5605|  6851.8410| 0.6478| 0.896|       |
|16:0          |  0.0161| 0.0090| 1.7794|  5615.1719|  4724.0218| 0.7906| 0.166|       |
|11-18:1       |  0.0066| 0.0036| 1.7982|  1086.1698|   671.6703| 0.8487| 0.001|***    |
|9-18:1        |  0.0059| 0.0030| 1.9682|  1190.9974|  1289.0113| 0.9013| 0.382|       |
|7,10,13-16:3  |  0.0032| 0.0023| 1.4174|  1228.4041|  1121.6290| 0.9298| 0.994|       |

## Comparison: 0.5_1000.5
|              | average|     sd|  ratio|        ava|        avb| cumsum|     p|signif |
|9,12,15-18:3  |  0.0722| 0.0270| 2.6693| 16978.5387| 12540.0819| 0.5203| 0.016|*      |
|16:0          |  0.0213| 0.0096| 2.2242|  5615.1719|  4302.5573| 0.6737| 0.004|**     |
|9,12-18:2     |  0.0197| 0.0115| 1.7076|  7401.5605|  6362.3532| 0.8156| 0.678|       |
|9-18:1        |  0.0074| 0.0045| 1.6374|  1190.9974|  1404.5302| 0.8688| 0.063|.      |
|11-18:1       |  0.0062| 0.0043| 1.4359|  1086.1698|   712.3420| 0.9134| 0.001|***    |
|7,10,13-16:3  |  0.0046| 0.0031| 1.4770|  1228.4041|  1040.0097| 0.9462| 0.863|       |
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

# 3. Подготовка данных для дозозависимых графиков
# Берем только сравнения с контролем (0.5_...)
df_control = full_df[full_df['Comparison'].str.startswith('0.5_')].copy()

# Извлекаем дозу Ni из названия сравнения (например, '0.5_50.5' -> 50)
df_control['Dose'] = df_control['Comparison'].apply(lambda x: int(float(x.split('_')[1].replace('.5', ''))))

# Извлекаем значения для Контроля (Dose = 0) из колонки 'ava'
control_vals = df_control[['Feature', 'ava']].drop_duplicates(subset=['Feature'])
control_vals = control_vals.rename(columns={'ava': 'Value'})
control_vals['Dose'] = 0

# Извлекаем значения для групп с никелем из колонки 'avb'
treated_vals = df_control[['Feature', 'avb', 'Dose']]
treated_vals = treated_vals.rename(columns={'avb': 'Value'})

# Объединяем в один датафрейм
trend_df = pd.concat([control_vals, treated_vals], ignore_index=True)

# Выбираем топ-6 самых значимых кислот для графиков
top_features = ['9,12,15-18:3', '16:0', '9,12-18:2', '9-18:1', '11-18:1', '7,10,13-16:3']
trend_df_top = trend_df[trend_df['Feature'].isin(top_features)]

# 4. Построение графиков
sns.set_theme(style="whitegrid")

# Создаем сетку графиков (FacetGrid), у каждого своя ось Y, так как концентрации сильно разные
g = sns.FacetGrid(trend_df_top, col="Feature", col_wrap=3, height=4, aspect=1.2, sharey=False)

# Рисуем линии и точки
g.map(sns.lineplot, "Dose", "Value", color="#2b7bba", linewidth=2.5)
g.map(sns.scatterplot, "Dose", "Value", color="#d9534f", s=80, zorder=10)

# Настраиваем оси
g.set_axis_labels("Концентрация Ni", "Содержание (ppm)")
g.set_titles(col_template="{col_name}", size=14, weight='bold')
g.set(xticks=[0, 50, 250, 500, 750, 1000]) # Жестко задаем ваши точки по оси X

plt.subplots_adjust(top=0.9)
g.fig.suptitle('Динамика содержания жирных кислот при росте концентрации Ni', fontsize=18, weight='bold')

plt.tight_layout()
plt.show()
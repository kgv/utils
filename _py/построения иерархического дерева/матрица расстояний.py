import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage
import seaborn as sns
from scipy.spatial.distance import pdist, squareform

# 1. Подготавливаем данные
data = {
    'Пик 1': [4.2, 3.68, 1.43],
    'Пик 2': [0.61, 1.47, 0.4],
    'Пик 3': [5.02, 0.89, 4.43],
    'Пик 4': [18.21, 9.35, 5.79],
    'Пик 5': [1.75, 2.05, 11.81],
    'Пик 6': [0.44, 0.0, 1.19],
    'Пик 7': [0.0, 0.0, 1.26],
    'Пик 8': [0.63, 0.0, 0.51],
    'Пик 9': [6.48, 12.17, 0.52],
    'Пик 10': [38.96, 33.22, 41.43],
    'Пик 11': [1.81, 0.36, 16.37],
    'Пик 12': [0.0, 0.42, 0.0],
    'Пик 13': [6.02, 33.96, 1.46],
    'Пик 14': [12.84, 1.53, 11.93],
    'Triolein': [6.79, 5.28, 4.71],
    'Пик 15': [0.0, 0.54, 0.0],
    'Пик 16': [0.54, 0.0, 0.0]
}

# Названия образцов (строки)
index = ['B', 'C-70', 'H-150']

# Создаем DataFrame
df = pd.DataFrame(data, index=index)

# 1. Вычисляем те самые коэффициенты отличия (евклидовы расстояния между образцами)
distances = pdist(df, metric='euclidean')

# 2. Превращаем их в удобную квадратную таблицу
dist_matrix = pd.DataFrame(
    squareform(distances), 
    index=df.index, 
    columns=df.index
)

# 3. Рисуем тепловую карту отличий
plt.figure(figsize=(6, 5))
sns.heatmap(
    dist_matrix, 
    annot=True, 
    cmap='Reds', # Чем краснее, тем сильнее отличаются образцы
    fmt=".1f",
    linewidths=1,
    linecolor='black'
)
plt.title('Коэффициенты отличия (расстояния) между образцами')
plt.show()

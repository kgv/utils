import pandas as pd
import io
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

df = pd.read_csv('Cypresses/Cypresses.csv', index_col=0)

# 2. Предобработка данных
# Убираем случайные пробелы в названиях колонок (например, ' 10' -> '10')
df.columns = df.columns.str.strip()
print(df)

# Заполняем пустые значения (NaN) нулями, так как вещество не найдено
df = df.fillna(0)

# Транспонируем таблицу, чтобы образцы (10, 11, 12) стали строками, а вещества - колонками
df_samples = df.T

# 3. Кластеризация
# Вычисляем расстояния и строим связи. 
# method='ward' минимизирует дисперсию внутри кластеров (один из самых популярных методов)
Z = linkage(df_samples, method='ward', metric='euclidean')

# 4. Визуализация
plt.figure(figsize=(8, 6))
dendrogram(
    Z, 
    labels=df_samples.index,  # Подписи осей (10, 11, 12)
    leaf_rotation=0,          # Поворот подписей
    leaf_font_size=14,        # Размер шрифта
    color_threshold=0         # Цвет веток (0 - стандартный синий)
)

plt.title('Кластерное дерево (Дендрограмма) образцов', fontsize=16)
plt.xlabel('ID образца', fontsize=14)
plt.ylabel('Евклидово расстояние', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Показываем график
plt.tight_layout()
plt.show()
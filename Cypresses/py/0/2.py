import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

# 1. Загрузка данных
df = pd.read_csv('Cypresses/CypressesPercent.csv', index_col=0)
# df = pd.read_csv('Cypresses/CypressesPercent.csv', index_col=0)

# 2. Предобработка данных
# Убираем случайные пробелы в названиях колонок
df.columns = df.columns.str.strip()

# ПРИНУДИТЕЛЬНО конвертируем все колонки в числовой формат.
# errors='coerce' превратит все строки, которые не являются числами (например, '     '), в NaN
df = df.apply(pd.to_numeric, errors='coerce')

# Теперь безопасно заполняем все пустые значения (NaN) нулями
df = df.fillna(0)
print(df)

# 3. Кластеризация
# Вычисляем расстояния и строим связи. 
Z = linkage(df, method='ward', metric='euclidean')

# 4. Визуализация
plt.figure(figsize=(8, 6))
dendrogram(
    Z, 
    labels=df.index,
    orientation='right',
    leaf_rotation=0,
    leaf_font_size=9,
    color_threshold=0
)

# plt.title('Кластерное дерево (Дендрограмма) образцов', fontsize=16)
plt.xlabel('Ward/Euclidean', fontsize=14)
# plt.ylabel('ID образца', fontsize=14)
plt.grid(axis='x', linestyle='--', alpha=0.7) 
# plt.margins(x=0) 

# Показываем график
# plt.tight_layout()
# plt.tight_layout(pad=1.0)
plt.subplots_adjust(left=0.2, right=0.9, top=0.9, bottom=0.1)
plt.show()
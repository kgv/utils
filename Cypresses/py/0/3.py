import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt

# 1. Загрузка данных
# Указываем, что первые три колонки (индексы 0, 1 и 2) — это составной индекс
df = pd.read_csv('Cypresses/csv/Absoute.csv', index_col=[0, 1, 2])
# df = pd.read_csv('Cypresses/csv/Percent.csv', index_col=[0, 1, 2])

# 2. Предобработка данных
# Убираем случайные пробелы в названиях колонок (веществ)
df.columns = df.columns.str.strip()

# Принудительно конвертируем все данные в числа, нечитаемое (пробелы) станет NaN
df = df.apply(pd.to_numeric, errors='coerce')

# Заполняем пустые значения (NaN) нулями
df = df.fillna(0)

# Так как строки теперь — это образцы, транспонирование (df.T) НЕ нужно.
df_samples = df 

# Если вдруг ваша таблица устроена иначе (строки — это всё ещё вещества), 
# раскомментируйте следующую строку:
# df_samples = df.T

# 3. Подготовка подписей для графика
# Так как индекс теперь состоит из 3 частей (Вид, Образец, Проба), 
# объединим их через подчеркивание, чтобы на графике это выглядело красиво.
# Пример: ('Кипарис', 10, 1) превратится в 'Кипарис_10_1'

# Находим максимальную длину текста для Вида, Образца и Пробы
max_len_0 = max(len(str(idx[0])) for idx in df_samples.index)
max_len_1 = max(len(str(idx[1])) for idx in df_samples.index)
max_len_2 = max(len(str(idx[2])) for idx in df_samples.index)

# Формируем строки. Метод ljust() добавляет пробелы справа до нужной длины
labels = [
    f"{str(idx[0]).ljust(max_len_0)} {str(idx[1]).ljust(max_len_1)} {str(idx[2]).ljust(max_len_2)}"
    for idx in df_samples.index
]

# 4. Кластеризация
# Z = linkage(df_samples, method='ward', metric='euclidean')
Z = linkage(df_samples, method='average', metric='braycurtis')

# 5. Визуализация
plt.figure(figsize=(10, 6)) # Сделаем график чуть шире
dendrogram(
    Z, 
    labels=labels,            # Передаем подписи
    orientation='right',
    leaf_rotation=0,
    leaf_font_size=10,
    color_threshold=0
)

# plt.title('Ward/Euclidean (mg/kg)', fontsize=16)
plt.title('Average & Cosine (mg per kg)', fontsize=16)
# plt.xlabel('Вид _ Образец _ Проба', fontsize=14)
# plt.xlabel('Ward/Euclidean', fontsize=14)
plt.grid(axis='x', linestyle='--', alpha=0.7) 

# Показываем график
# plt.tight_layout()
plt.subplots_adjust(left=0.2, right=0.95, top=0.9, bottom=0.1)
plt.show()

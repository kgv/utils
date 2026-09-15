import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
import tkinter as tk
from tkinter import filedialog
import os

# ==========================================
# 1. ВЫБОР ФАЙЛОВ
# ==========================================
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True)

print("Пожалуйста, выберите CSV файлы в появившемся окне...")
file_paths = filedialog.askopenfilenames(
    title="Выберите CSV файлы для анализа (минимум 2)",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)

if len(file_paths) < 2:
    print("Для сравнения DTW необходимо выбрать как минимум ДВА файла!")
    exit()

# ==========================================
# 2. ЗАГРУЗКА И ПРОРЕЖИВАНИЕ ЧЕРЕЗ POLARS
# ==========================================
series_list = []
names = []

# ШАГ ПРОРЕЖИВАНИЯ: берем каждую 1000-ю строку, чтобы не переполнить память!
# Если график будет слишком грубым, уменьшите это число (например, до 500 или 100).
# Если компьютер зависает - увеличьте (например, до 2000).
STEP = 10 

for file in file_paths:
     # Читаем файл, указываем разделитель и отсутствие заголовков
    df = pl.read_csv(file, separator=";", has_header=False)
    
    # ИСПРАВЛЕНИЕ 2: Прореживаем огромный датасет
    df_sampled = df.gather_every(STEP)
    
    # Судя по вашим данным ("0.0166667 ; 2.10702"), 
    # первый столбец (индекс 0) - это время, а второй (индекс 1) - само значение.
    # Нам для DTW нужны именно значения, поэтому берем столбец с индексом 1.
    target_column_name = df_sampled.columns[1]
    
    # Очищаем от пробелов и безопасно конвертируем
    ts_array = (
        df_sampled.get_column(target_column_name)
        .str.strip_chars()               # 1. Удаляем пробелы в начале и конце
        .cast(pl.Float64, strict=False)  # 2. Конвертируем в числа (ошибки станут null)
        .drop_nulls()                    # 3. Удаляем битые строки (null), если они есть
        .to_numpy()                      # 4. Переводим в формат numpy для DTW
    )
    
    series_list.append(ts_array)
    names.append(os.path.basename(file))

print(f"Успешно загружено файлов: {len(series_list)}")
print(f"Точек в каждом ряду после прореживания: {len(series_list[0])}")

# ==========================================
# 3. АНАЛИЗ (DTW) С ОГРАНИЧЕНИЕМ ПО ВРЕМЕНИ
# ==========================================
print("\nВычисление матрицы расстояний...")

# ЗАДАЕМ ОКНО (Window)
# Так как мы проредили данные (осталось около 400 точек), 
# окно в 20-40 точек будет означать отклонение примерно на 5-10% по оси X.
# Попробуйте поменять это число (например, 10, 20, 50), чтобы найти идеальный вид графика.
WINDOW_SIZE = 10 

# Добавляем параметр window
distance_matrix = dtw.distance_matrix_fast(series_list, window=WINDOW_SIZE)

print("Матрица расстояний DTW:")
print(distance_matrix)

# ==========================================
# 4. ВИЗУАЛИЗАЦИЯ (ГРАФИК)
# ==========================================
s1 = series_list[0]
s2 = series_list[1]

print("Вычисление пути трансформации (Warping Path)...")
path = dtw.warping_path(s1, s2, window=WINDOW_SIZE)

# ТОП-100 ВЫСОКИХ С РАЗРЯДКОЙ
LINES_TO_DRAW = 100
MIN_DISTANCE = 100  # Минимальное расстояние между линиями (не чаще чем каждые 10 шагов)

# 1. Запоминаем исходный порядковый номер каждой связи и считаем её высоту
# Создаем список вида: [(индекс_в_пути, (x, y), высота), ...]
path_enriched = [
    (idx, pair, s1[pair[0]] + s2[pair[1]]) 
    for idx, pair in enumerate(path)
]

# 2. Сортируем все связи по высоте (от самых высоких к низким)
path_sorted_by_height = sorted(path_enriched, key=lambda item: item[2], reverse=True)

# 3. Жадный алгоритм выбора (отсеиваем те, что слишком близко друг к другу)
selected_pairs = []
selected_indices = []

for idx, pair, height in path_sorted_by_height:
    # Проверяем, нет ли уже выбранной линии слишком близко к текущей
    is_too_close = False
    for sel_idx in selected_indices:
        if abs(idx - sel_idx) < MIN_DISTANCE:
            is_too_close = True
            break
    
    # Если рядом (в радиусе 10 шагов) нет других линий, берем эту!
    if not is_too_close:
        selected_pairs.append(pair)
        selected_indices.append(idx)
        
    # Как только набрали 100 штук — останавливаемся
    if len(selected_pairs) == LINES_TO_DRAW:
        break

# 4. Сортируем выбранные линии обратно по времени (слева направо), 
# чтобы библиотека смогла их правильно нарисовать
path_final = sorted(selected_pairs, key=lambda pair: pair[0])

# Строим график
fig, ax = dtwvis.plot_warping(s1, s2, path_final)

# В заголовке указываем, сколько реально линий удалось найти 
# (их может быть меньше 100, если график короткий)
fig.suptitle(f"DTW: {names[0]} и {names[1]}\n(Топ-{len(path_final)} высоких пиков, шаг >= {MIN_DISTANCE})", fontsize=14)

plt.show()
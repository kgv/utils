import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import polars as pl
import tkinter as tk
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
from tkinter import filedialog

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
STEP = 10 

for file in file_paths:
    # Читаем файл, указываем разделитель и отсутствие заголовков
    df = pl.read_csv(file, separator=";", has_header=False)
    
    # Прореживаем огромный датасет
    df_sampled = df.gather_every(STEP)
    
    # Берем столбец с индексом 1 (значения)
    target_column_name = df_sampled.columns[1]
    
    # Очищаем от пробелов и безопасно конвертируем
    ts_array = (
        df_sampled.get_column(target_column_name)
        # .str.strip_chars()               # 1. Удаляем пробелы в начале и конце
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

WINDOW_SIZE = 10 

# Вычисляем матрицу
distance_matrix = dtw.distance_matrix_fast(series_list, window=WINDOW_SIZE)

# --- ВЫВОД МАТРИЦЫ В ФОРМАТЕ MARKDOWN ---
print("\nМатрица расстояний DTW (Markdown):\n")

# Формируем заголовок таблицы
header = "| Файл | " + " | ".join(names) + " |"
separator = "|" + "---|" * (len(names) + 1)
print(header)
print(separator)

# Формируем строки таблицы
for i in range(len(names)):
    row_str = f"| **{names[i]}** |"
    for j in range(len(names)):
        val = distance_matrix[i, j]
        
        # dtaidistance возвращает верхнетреугольную матрицу (нижняя часть = inf)
        # Для красивого вывода отзеркалим значения
        if np.isinf(val) and i > j:
            val = distance_matrix[j, i]
        
        # Форматируем вывод (4 знака после запятой)
        if np.isinf(val):
            row_str += " ∞ |"
        else:
            row_str += f" {val:.4f} |"
    print(row_str)
print("\n")
# ----------------------------------------

# ==========================================
# 4. ВИЗУАЛИЗАЦИЯ (ГРАФИКИ ДЛЯ ВСЕХ ПАР)
# ==========================================
print("Вычисление путей трансформации и построение графиков для всех пар...")

# ТОП-100 ВЫСОКИХ С РАЗРЯДКОЙ
LINES_TO_DRAW = 100
MIN_DISTANCE = 100  # Минимальное расстояние между линиями

for i, j in itertools.combinations(range(len(series_list)), 2):
    s1 = series_list[i]
    s2 = series_list[j]
    name1 = names[i]
    name2 = names[j]
    
    print(f"Обработка пары: {name1} и {name2}...")
    
    # Вычисляем путь для конкретной пары
    path = dtw.warping_path(s1, s2, window=WINDOW_SIZE)

    # 1. Запоминаем исходный порядковый номер каждой связи и считаем её высоту
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
        is_too_close = False
        for sel_idx in selected_indices:
            if abs(idx - sel_idx) < MIN_DISTANCE:
                is_too_close = True
                break
        
        if not is_too_close:
            selected_pairs.append(pair)
            selected_indices.append(idx)
            
        if len(selected_pairs) == LINES_TO_DRAW:
            break

    # 4. Сортируем выбранные линии обратно по времени (слева направо)
    path_final = sorted(selected_pairs, key=lambda pair: pair[0])

    # Строим график для текущей пары
    fig, ax = dtwvis.plot_warping(s1, s2, path_final)

    # В заголовке указываем имена сравниваемых файлов
    fig.suptitle(f"DTW: {name1} и {name2}\n(Топ-{len(path_final)} высоких пиков, шаг >= {MIN_DISTANCE})", fontsize=14)

# Показываем ВСЕ созданные графики одновременно
print("Отрисовка графиков...")
plt.show()
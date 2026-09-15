import itertools
import matplotlib.pyplot as plt
import numpy as np
import os
import polars as pl
import tkinter as tk
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
from tkinter import filedialog

# НОВЫЕ ИМПОРТЫ ДЛЯ КЛАСТЕРИЗАЦИИ
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import squareform

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

# ШАГ ПРОРЕЖИВАНИЯ
STEP = 10 

for file in file_paths:
    df = pl.read_csv(file, separator=";", has_header=False)
    df_sampled = df.gather_every(STEP)
    target_column_name = df_sampled.columns[1]
    
    # Получаем колонку
    col = df_sampled.get_column(target_column_name)
    
    # Проверяем: если это текст (String), то очищаем от пробелов и переводим в числа
    if col.dtype in [pl.String, getattr(pl, 'Utf8', None)]:
        col = col.str.strip_chars().cast(pl.Float64, strict=False)
    else:
        # Если это УЖЕ числа, просто гарантируем формат Float64
        col = col.cast(pl.Float64, strict=False)
        
    # Удаляем пустоты и переводим в numpy массив
    ts_array = col.drop_nulls().to_numpy()
    
    series_list.append(ts_array)
    
    # 1. Получаем имя файла с расширением (например, "data{Normalized}.csv")
    base_name = os.path.basename(file)
    
    # 2. Отделяем имя от расширения (получаем "data{Normalized}")
    name_without_ext = os.path.splitext(base_name)[0]
    
    # 3. Удаляем суффикс "{Normalized}" и убираем лишние пробелы по краям, если они останутся
    clean_name = name_without_ext.replace("{Normalized}", "").strip()
    
    names.append(clean_name)

print(f"Успешно загружено файлов: {len(series_list)}")
print(f"Точек в каждом ряду после прореживания: {len(series_list[0])}")

# ==========================================
# 3. АНАЛИЗ (DTW) С ОГРАНИЧЕНИЕМ ПО ВРЕМЕНИ
# ==========================================
print("\nВычисление матрицы расстояний...")

WINDOW_SIZE = 10 
distance_matrix = dtw.distance_matrix_fast(series_list, window=WINDOW_SIZE)

# --- ВЫВОД МАТРИЦЫ В ФОРМАТЕ MARKDOWN ---
print("\nМатрица расстояний DTW (Markdown):\n")
header = "| Файл | " + " | ".join(names) + " |"
separator = "|" + "---|" * (len(names) + 1)
print(header)
print(separator)

for i in range(len(names)):
    row_str = f"| **{names[i]}** |"
    for j in range(len(names)):
        val = distance_matrix[i, j]
        if np.isinf(val) and i > j:
            val = distance_matrix[j, i]
        
        if np.isinf(val):
            row_str += " ∞ |"
        else:
            row_str += f" {val:.4f} |"
    print(row_str)
print("\n")

# ==========================================
# 4. ИЕРАРХИЧЕСКАЯ КЛАСТЕРИЗАЦИЯ (ДЕНДРОГРАММА)
# ==========================================
print("Построение иерархической кластеризации...")

# 1. Создаем полную симметричную матрицу (заполняем нижний треугольник)
sym_dist_matrix = distance_matrix.copy()
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        sym_dist_matrix[j, i] = sym_dist_matrix[i, j]
np.fill_diagonal(sym_dist_matrix, 0) # На диагонали должны быть нули

# 2. Преобразуем матрицу в сжатый 1D-формат, который требует SciPy
condensed_dist = squareform(sym_dist_matrix)

# 3. Выполняем кластеризацию (метод 'average' хорошо подходит для DTW)
Z = linkage(condensed_dist, method='average')

# 4. Строим график (дендрограмму)
fig_cluster = plt.figure(figsize=(10, 6))
dendrogram(
    Z, 
    labels=names, 
    # leaf_rotation=45,  # Поворот подписей для читаемости
    leaf_font_size=10
)
plt.title("Иерархическая кластеризация временных рядов (DTW)", fontsize=14)
plt.ylabel("Расстояние (DTW Distance)")
plt.tight_layout()

# Показываем ВСЕ созданные графики (включая дендрограмму) одновременно
print("Отрисовка графиков...")
plt.show()
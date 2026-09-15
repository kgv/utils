import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from dtaidistance import dtw
from dtaidistance import dtw_visualisation as dtwvis
import tkinter as tk
from tkinter import filedialog
import os

# ==========================================
# 1. ВЫБОР ФАЙЛОВ ЧЕРЕЗ ДИАЛОГОВОЕ ОКНО
# ==========================================
# Инициализируем tkinter и скрываем главное окно
root = tk.Tk()
root.withdraw()
root.attributes('-topmost', True) # Окно появится поверх других программ

print("Пожалуйста, выберите CSV файлы в появившемся окне...")
# Открываем окно выбора нескольких файлов
file_paths = filedialog.askopenfilenames(
    title="Выберите CSV файлы для анализа (минимум 2)",
    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
)

if not file_paths:
    print("Файлы не выбраны. Программа завершена.")
    exit()

if len(file_paths) < 2:
    print("Для сравнения DTW необходимо выбрать как минимум ДВА файла!")
    exit()

# ==========================================
# 2. ЗАГРУЗКА CSV ЧЕРЕЗ POLARS
# ==========================================
series_list = []
names = []

for file in file_paths:
    # Читаем CSV
    df = pl.read_csv(file, separator=";")
    
    # Берем ПЕРВЫЙ столбец из файла (df.columns[0])
    # Приводим к Float64 и конвертируем в numpy массив
    first_column_name = df.columns[0]
    ts_array = df.get_column(first_column_name).cast(pl.Float64).to_numpy()
    
    series_list.append(ts_array)
    names.append(os.path.basename(file))

print(f"Успешно загружено файлов: {len(series_list)} {names}")

# ==========================================
# 3. АНАЛИЗ (DTW)
# ==========================================
print("\nВычисление матрицы расстояний...")
distance_matrix = dtw.distance_matrix_fast(series_list)

print("Матрица расстояний DTW:")
print(distance_matrix)

# ==========================================
# 4. ВИЗУАЛИЗАЦИЯ (ГРАФИК)
# ==========================================
# Для графика берем первые два выбранных файла
s1 = series_list[0]
s2 = series_list[1]

# Вычисляем оптимальный путь (Warping Path)
path = dtw.warping_path(s1, s2)

# Строим график
fig, ax = dtwvis.plot_warping(s1, s2, path)

# ИСПРАВЛЕНИЕ: Используем fig.suptitle вместо ax.set_title
# Это установит заголовок для всего окна графика
fig.suptitle(f"DTW сопоставление:\n{names[0]} и {names[1]}", fontsize=14)

# Показываем график
plt.show()
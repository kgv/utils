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
# Сюда тоже ОБЯЗАТЕЛЬНО добавляем параметр window, иначе график нарисуется по-старому
path = dtw.warping_path(s1, s2, window=WINDOW_SIZE)

# ВЫБИРАЕМ 100 САМЫХ ВЫСОКИХ СВЯЗЕЙ ---
LINES_TO_DRAW = 100

# 1. Сортируем все найденные связи по высоте (сумма значений Y на обоих графиках)
# reverse=True означает, что самые высокие значения будут в начале списка
path_sorted_by_height = sorted(
    path, 
    key=lambda pair: s1[pair[0]] + s2[pair[1]], 
    reverse=True
)

# 2. Берем топ-100 самых высоких связей
path_top = path_sorted_by_height[:LINES_TO_DRAW]

# 3. Сортируем их обратно по времени (по индексу X), 
# чтобы библиотека dtaidistance нарисовала их без ошибок
path_final = sorted(path_top, key=lambda pair: pair[0])

# Строим график, передавая отфильтрованный путь (path_final)
fig, ax = dtwvis.plot_warping(s1, s2, path_final)

fig.suptitle(f"DTW: {names[0]} и {names[1]}\n(Показаны {LINES_TO_DRAW} самых высоких связей)", fontsize=14)

plt.show()
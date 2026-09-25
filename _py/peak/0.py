import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import tkinter as tk
from tkinter import filedialog
import sys
import os

# 1. Создаем скрытое базовое окно для интерфейса
root = tk.Tk()
root.withdraw() # Прячем пустое серое окно на фоне

# 2. Открываем диалоговое окно выбора файла
file_path = filedialog.askopenfilename(
    title="Выберите CSV файл со спектром",
    filetypes=[("CSV файлы", "*.csv"), ("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
)

# Если пользователь нажал "Отмена" или закрыл окно
if not file_path:
    print("Файл не выбран. Программа завершена.")
    sys.exit()

print(f"Загрузка файла: {file_path} ...")

# 3. Загружаем данные
try:
    # Указываем, что разделитель - точка с запятой, а десятичный - точка
    df = pd.read_csv(file_path, sep=';', decimal='.', header=None, names=['X', 'Y'])
except Exception as e:
    print(f"Ошибка при чтении файла: {e}")
    sys.exit()

# 4. Ищем пики. 
# prominence - это "выраженность" пика над фоном. 
# Если программа находит слишком много мелких пиков (шум) - увеличьте это число.
# Если пропускает нужные пики - уменьшите.
peaks, properties = find_peaks(df['Y'], prominence=50)

# 5. Выводим координаты пиков в консоль
print("\nКоординаты найденных пиков:")
print("X\t\tY (Интенсивность)")
print("-" * 35)
for idx in peaks:
    print(f"{df['X'].iloc[idx]:.5f}\t{df['Y'].iloc[idx]:.2f}")

# 6. Строим график
plt.figure(figsize=(12, 6))
plt.plot(df['X'], df['Y'], label='Спектр', color='blue', linewidth=0.5)
plt.plot(df['X'].iloc[peaks], df['Y'].iloc[peaks], "x", color='red', label='Пики')

# Для ЯМР ось X обычно инвертируют (от большего к меньшему)
plt.gca().invert_xaxis() 

plt.xlabel('X')
plt.ylabel('Y')
filename = os.path.basename(file_path)
plt.title(f'Спектр и пики: {filename}')
plt.legend()
plt.grid(True, alpha=0.3)

# Показываем интерактивное окно с графиком
plt.show()
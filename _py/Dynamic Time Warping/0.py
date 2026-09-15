import polars as pl
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from fastdtw import fastdtw

def load_signal(file_path):
    """Загружает Y-значения из подготовленного CSV файла"""
    df = pl.read_csv(file_path, separator=';', has_header=False)
    # Берем второй столбец (индекс 1) и превращаем в numpy массив
    return df[df.columns[1]].to_numpy()

def main():
    # Укажите пути к двум файлам, которые вы обработали первым скриптом
    file1 = "chromatogram_1{Z-scored}.csv"
    file2 = "chromatogram_2{Z-scored}.csv"
    
    print("Загрузка данных...")
    y1 = load_signal(file1)
    y2 = load_signal(file2)
    
    print("Запуск DTW (это может занять несколько секунд)...")
    # fastdtw возвращает дистанцию и путь выравнивания (массив индексов)
    distance, path = fastdtw(y1, y2, dist=euclidean)
    
    print(f"DTW Дистанция между хроматограммами: {distance:.4f}")
    
    # Распаковываем путь выравнивания
    path_x = [p[0] for p in path]
    path_y = [p[1] for p in path]
    
    # Создаем выровненные массивы
    y1_aligned = y1[path_x]
    y2_aligned = y2[path_y]
    
    # --- Визуализация результатов ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # График 1: До выравнивания (но после Z-score)
    ax1.plot(y1, label='Хроматограмма 1', color='blue', alpha=0.7)
    ax1.plot(y2, label='Хроматограмма 2', color='red', alpha=0.7)
    ax1.set_title("До DTW (Смещенные пики, Z-score применен)")
    ax1.legend()
    
    # График 2: После выравнивания DTW
    ax2.plot(y1_aligned, label='Хроматограмма 1 (выровненная)', color='blue', alpha=0.7)
    ax2.plot(y2_aligned, label='Хроматограмма 2 (выровненная)', color='red', alpha=0.7)
    ax2.set_title("После DTW (Пики идеально совпадают по времени)")
    ax2.legend()
    
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
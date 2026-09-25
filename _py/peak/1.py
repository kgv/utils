import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.signal import find_peaks
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import os

def main():
    # 1. Инициализация скрытого окна для выбора файла
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Выберите CSV файл со спектром",
        filetypes=[("CSV файлы", "*.csv"), ("Текстовые файлы", "*.txt"), ("Все файлы", "*.*")]
    )
    
    if not file_path:
        print("Файл не выбран. Программа завершена.")
        sys.exit()

    # 2. Чтение данных
    try:
        df = pd.read_csv(file_path, sep=';', decimal='.', header=None, names=['X', 'Y'])
    except Exception as e:
        messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {e}")
        sys.exit()

    # 3. Настройка главного окна
    root.deiconify() # Показываем окно
    root.title(f"Анализ спектра ЯМР - {os.path.basename(file_path)}")
    root.geometry("1200x700") # Размер окна по умолчанию

    # Разделяем окно на левую панель (настройки) и правую (график)
    left_frame = tk.Frame(root, width=300, padx=10, pady=10)
    left_frame.pack(side=tk.LEFT, fill=tk.Y)
    
    right_frame = tk.Frame(root)
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # --- ЛЕВАЯ ПАНЕЛЬ (НАСТРОЙКИ) ---
    tk.Label(left_frame, text="Настройки поиска", font=("Arial", 12, "bold")).pack(pady=(0, 10))

    # Поля ввода
    frame_inputs = tk.Frame(left_frame)
    frame_inputs.pack(fill=tk.X)

    tk.Label(frame_inputs, text="Начало X:").grid(row=0, column=0, sticky="e", pady=2)
    ent_xmin = tk.Entry(frame_inputs, width=15)
    ent_xmin.insert(0, f"{df['X'].min():.3f}")
    ent_xmin.grid(row=0, column=1, pady=2, padx=5)

    tk.Label(frame_inputs, text="Конец X:").grid(row=1, column=0, sticky="e", pady=2)
    ent_xmax = tk.Entry(frame_inputs, width=15)
    ent_xmax.insert(0, f"{df['X'].max():.3f}")
    ent_xmax.grid(row=1, column=1, pady=2, padx=5)

    tk.Label(frame_inputs, text="Чувствительность:").grid(row=2, column=0, sticky="e", pady=2)
    ent_prom = tk.Entry(frame_inputs, width=15)
    ent_prom.insert(0, "50")
    ent_prom.grid(row=2, column=1, pady=2, padx=5)

    tk.Label(frame_inputs, text="Мин. дистанция:").grid(row=3, column=0, sticky="e", pady=2)
    ent_dist = tk.Entry(frame_inputs, width=15)
    ent_dist.insert(0, "1")
    ent_dist.grid(row=3, column=1, pady=2, padx=5)

    # Текстовое поле для вывода координат пиков
    tk.Label(left_frame, text="Найденные пики:", font=("Arial", 10, "bold")).pack(pady=(15, 5))
    
    # Добавляем скроллбар для текста
    text_frame = tk.Frame(left_frame)
    text_frame.pack(fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(text_frame)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    text_peaks = tk.Text(text_frame, width=30, height=20, yscrollcommand=scrollbar.set)
    text_peaks.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=text_peaks.yview)

    # --- ПРАВАЯ ПАНЕЛЬ (ГРАФИК) ---
    fig, ax = plt.subplots(figsize=(8, 6))
    canvas = FigureCanvasTkAgg(fig, master=right_frame)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    
    # Добавляем стандартную панель инструментов matplotlib (лупа, сохранение и т.д.)
    toolbar = NavigationToolbar2Tk(canvas, right_frame)
    toolbar.update()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # --- ФУНКЦИЯ ОБНОВЛЕНИЯ ---
    def update_plot(event=None):
        try:
            xmin_val = float(ent_xmin.get())
            xmax_val = float(ent_xmax.get())
            prom_val = float(ent_prom.get())
            dist_val = int(ent_dist.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите корректные числа (используйте точку).")
            return

        real_xmin = min(xmin_val, xmax_val)
        real_xmax = max(xmin_val, xmax_val)

        # Вырезаем данные по X
        mask = (df['X'] >= real_xmin) & (df['X'] <= real_xmax)
        df_search = df[mask]

        # Ищем пики
        if not df_search.empty:
            peaks, _ = find_peaks(df_search['Y'], prominence=prom_val, distance=dist_val)
            peak_x = df_search['X'].iloc[peaks]
            peak_y = df_search['Y'].iloc[peaks]
        else:
            peaks, peak_x, peak_y = [], [], []

        # Очищаем и перерисовываем график
        ax.clear()
        ax.plot(df['X'], df['Y'], label='Спектр', color='blue', linewidth=0.5)
        
        if len(peaks) > 0:
            ax.plot(peak_x, peak_y, "x", color='red', markersize=8, label='Пики')

        # Инвертируем ось X и ставим лимиты (от большего к меньшему)
        ax.set_xlim(real_xmax, real_xmin)
        
        ax.set_xlabel('X (ppm)')
        ax.set_ylabel('Интенсивность')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Обновляем холст
        canvas.draw()

        # Обновляем текстовое поле с координатами
        text_peaks.delete(1.0, tk.END)
        text_peaks.insert(tk.END, f"Всего найдено: {len(peaks)}\n")
        text_peaks.insert(tk.END, "X\t\tY\n")
        text_peaks.insert(tk.END, "-"*25 + "\n")
        for x, y in zip(peak_x, peak_y):
            text_peaks.insert(tk.END, f"{x:.5f}\t{y:.2f}\n")

    # Кнопка обновления
    btn_update = tk.Button(left_frame, text="Обновить график", command=update_plot, bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
    btn_update.pack(pady=10, fill=tk.X)

    # Привязываем нажатие клавиши Enter в полях ввода к обновлению графика
    ent_xmin.bind('<Return>', update_plot)
    ent_xmax.bind('<Return>', update_plot)
    ent_prom.bind('<Return>', update_plot)
    ent_dist.bind('<Return>', update_plot)

    # Строим график первый раз при запуске
    update_plot()

    # Обработка закрытия окна
    def on_closing():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()
import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# 1. Загрузка и подготовка данных
file = 'Vial,Component,CAS,RI,RT,Percent,PartsPerMillion'
path = f"Cypresses/csv/{file}.txt"
df = pd.read_csv(path, index_col=[0, 1, 2])
# df = pd.read_csv(path, index_col=[0, 1, 2])
df.columns = df.columns.str.strip()
df = df.apply(pd.to_numeric, errors='coerce').fillna(0)
print(f"df: {df}")

# Убираем пустые строки (нули), чтобы работали метрики вроде cosine
df_samples = df.loc[(df != 0).any(axis=1)]
labels = [f"{idx[0]} {idx[1]} {idx[2]}" for idx in df_samples.index]

# 2. Создание главного окна Tkinter
root = tk.Tk()
root.title("Кластеризация образцов")
root.geometry("1100x700") # Размер окна

# 3. Панель управления (сверху) для ComboBox
control_frame = ttk.Frame(root, padding=10)
control_frame.pack(side=tk.TOP, fill=tk.X)

# ComboBox для выбора МЕТОДА
ttk.Label(control_frame, text="Метод (method):", font=('', 12)).pack(side=tk.LEFT, padx=5)
method_var = tk.StringVar(value='ward')
method_cb = ttk.Combobox(control_frame, textvariable=method_var, state="readonly", font=('', 11),
                         values=['ward', 'average', 'single', 'complete', 'weighted', 'centroid'])
method_cb.pack(side=tk.LEFT, padx=5)

# ComboBox для выбора МЕТРИКИ
ttk.Label(control_frame, text="Метрика (metric):", font=('', 12)).pack(side=tk.LEFT, padx=(20, 5))
metric_var = tk.StringVar(value='euclidean')
metric_cb = ttk.Combobox(control_frame, textvariable=metric_var, state="readonly", font=('', 11),
                         values=['euclidean', 'cosine', 'cityblock', 'correlation', 'braycurtis'])
metric_cb.pack(side=tk.LEFT, padx=5)

# 4. Настройка области для графика Matplotlib
fig = Figure(figsize=(10, 6))
ax = fig.add_subplot(111)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Добавляем стандартную панель инструментов Matplotlib (сохранение, зум)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()

# 5. Функция обновления графика
def update_plot(event=None):
    ax.clear() # Очищаем старый график
    method = method_var.get()
    metric = metric_var.get()
    
    # Защита от несовместимых параметров
    if method in ['ward', 'centroid', 'median'] and metric != 'euclidean':
        ax.text(0.5, 0.5, f"⚠️ ОШИБКА:\nМетод '{method}' работает ТОЛЬКО с метрикой 'euclidean'.\nВыберите другую метрику.", 
                ha='center', va='center', fontsize=14, color='red')
        canvas.draw()
        return
        
    # Вычисляем и рисуем
    Z = linkage(df_samples, method=method, metric=metric)
    dendrogram(Z, labels=labels, orientation='right', leaf_rotation=0, leaf_font_size=10, color_threshold=0, ax=ax)
    
    ax.set_title(f"{method.capitalize()} & {metric.capitalize()} & {file}", fontsize=16)
    # ax.set_ylabel('Расстояние', fontsize=14)
    ax.grid(axis='x', linestyle='--', alpha=0.7) 
    
    fig.tight_layout()
    canvas.draw() # Перерисовываем холст

# 6. Привязываем обновление графика к выбору в ComboBox
method_cb.bind('<<ComboboxSelected>>', update_plot)
metric_cb.bind('<<ComboboxSelected>>', update_plot)

# Рисуем график при запуске и открываем окно
update_plot()
root.mainloop()
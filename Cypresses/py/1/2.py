import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# 1. Загрузка и подготовка данных
file = "TreeComponent"
path = f"Cypresses/csv/{file}.txt"

df = pd.read_csv(path, index_col=[0, 1, 2])
df.columns = df.columns.str.strip()
df = df.apply(pd.to_numeric, errors="coerce").fillna(0)

df_samples = df.loc[(df != 0).any(axis=1)]
labels = [f"{idx[0]} {idx[1]} {idx[2]}" for idx in df_samples.index]

# 2. Создание главного окна Tkinter
root = tk.Tk()
root.title("Кластеризация образцов")
root.geometry("1100x700")

# Глобальный словарь для хранения пользовательских настроек осей
axes_settings = {
    "xlabel": "Расстояние",
    "xmin": "",
    "xmax": ""
}

# 3. Панель управления
control_frame = ttk.Frame(root, padding=10)
control_frame.pack(side=tk.TOP, fill=tk.X)

# ComboBox: Метод
ttk.Label(control_frame, text="Метод:", font=("", 12)).pack(side=tk.LEFT, padx=5)
method_var = tk.StringVar(value="ward")
method_cb = ttk.Combobox(control_frame, textvariable=method_var, state="readonly", width=10,
                         values=["ward", "average", "single", "complete", "weighted", "centroid"])
method_cb.pack(side=tk.LEFT, padx=5)

# ComboBox: Метрика
ttk.Label(control_frame, text="Метрика:", font=("", 12)).pack(side=tk.LEFT, padx=(15, 5))
metric_var = tk.StringVar(value="euclidean")
metric_cb = ttk.Combobox(control_frame, textvariable=metric_var, state="readonly", width=10,
                         values=["euclidean", "cosine", "cityblock", "correlation", "braycurtis"])
metric_cb.pack(side=tk.LEFT, padx=5)

# 4. Настройка области для графика Matplotlib
fig = Figure(figsize=(10, 6))
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()

# 5. Функция обновления графика
def update_plot(event=None):
    ax.clear()
    ax.set_axis_on()
    
    method = method_var.get()
    metric = metric_var.get()

    if method in ["centroid", "median", "ward"] and metric != "euclidean":
        ax.text(0.5, 0.5, f"⚠️ ОШИБКА:\nМетод '{method}' работает ТОЛЬКО с 'euclidean'.",
                ha="center", va="center", fontsize=14, color="red")
        ax.set_axis_off()
        canvas.draw()
        return

    # Рисуем дендрограмму
    Z = linkage(df_samples, method=method, metric=metric)
    dendrogram(Z, labels=labels, orientation="right", leaf_rotation=0, leaf_font_size=10, ax=ax)

    # --- ПРИМЕНЕНИЕ НАСТРОЕК ОСЕЙ ---
    ax.set_title(f"{method.capitalize()} & {metric.capitalize()} & {file}", fontsize=14)
    ax.set_xlabel(axes_settings["xlabel"], fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    
    # Применяем пользовательские лимиты, если они заданы
    current_xlim = ax.get_xlim()
    new_xmin, new_xmax = current_xlim[0], current_xlim[1]
    
    if axes_settings["xmin"].strip():
        try: new_xmin = float(axes_settings["xmin"])
        except ValueError: pass
        
    if axes_settings["xmax"].strip():
        try: new_xmax = float(axes_settings["xmax"])
        except ValueError: pass
        
    ax.set_xlim(new_xmin, new_xmax)

    fig.tight_layout()
    canvas.draw()

# 6. ФУНКЦИЯ И ОКНО ДЛЯ РЕДАКТИРОВАНИЯ ОСЕЙ
def open_axes_settings():
    # Создаем всплывающее окно
    dialog = tk.Toplevel(root)
    dialog.title("Настройки осей")
    dialog.geometry("320x250")
    dialog.transient(root) # Окно поверх главного
    dialog.grab_set()      # Блокируем главное окно, пока открыты настройки

    # Поле: Подпись оси X
    ttk.Label(dialog, text="Подпись оси X:").pack(pady=(10, 2))
    xlabel_var = tk.StringVar(value=axes_settings["xlabel"])
    ttk.Entry(dialog, textvariable=xlabel_var).pack(fill=tk.X, padx=20)

    # Поле: Минимум X
    ttk.Label(dialog, text="Минимум X (пусто = авто):").pack(pady=(10, 2))
    xmin_var = tk.StringVar(value=axes_settings["xmin"])
    ttk.Entry(dialog, textvariable=xmin_var).pack(fill=tk.X, padx=20)

    # Поле: Максимум X
    ttk.Label(dialog, text="Максимум X (пусто = авто):").pack(pady=(10, 2))
    xmax_var = tk.StringVar(value=axes_settings["xmax"])
    ttk.Entry(dialog, textvariable=xmax_var).pack(fill=tk.X, padx=20)

    # Функция применения настроек
    def apply_settings():
        axes_settings["xlabel"] = xlabel_var.get()
        axes_settings["xmin"] = xmin_var.get()
        axes_settings["xmax"] = xmax_var.get()
        update_plot() # Перерисовываем график с новыми осями
        dialog.destroy() # Закрываем окно

    ttk.Button(dialog, text="Применить", command=apply_settings).pack(pady=20)

# КНОПКА ВЫЗОВА НАСТРОЕК (добавляем на верхнюю панель)
btn_settings = ttk.Button(control_frame, text="⚙ Настройки осей", command=open_axes_settings)
btn_settings.pack(side=tk.RIGHT, padx=10)

# Привязки и запуск
method_cb.bind("<<ComboboxSelected>>", update_plot)
metric_cb.bind("<<ComboboxSelected>>", update_plot)

update_plot()
root.mainloop()
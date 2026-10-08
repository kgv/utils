import pandas as pd
from scipy.cluster.hierarchy import dendrogram, linkage
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

# 1. Загрузка и подготовка данных
file = "TreeComponent"
path = f"Cypresses/csv/{file}.txt"

try:
    df = pd.read_csv(path, index_col=[0, 1, 2])
    df.columns = df.columns.str.strip()
    df = df.apply(pd.to_numeric, errors="coerce").fillna(0)
except FileNotFoundError:
    print(f"Файл {path} не найден. Используются тестовые данные.")

df_samples = df.loc[(df != 0).any(axis=1)]
labels = [f"{idx[0]} {idx[1]} {idx[2]}" for idx in df_samples.index]

# 2. Создание главного окна Tkinter
root = tk.Tk()
root.title("Кластеризация образцов")
root.geometry("1100x700")

# ГЛОБАЛЬНЫЙ СЛОВАРЬ СО ВСЕМИ НАСТРОЙКАМИ
app_settings = {
    "method": "ward",
    "metric": "euclidean",
    "xlabel": "Расстояние",
    "xmin": "",
    "xmax": "",
}

# 3. Панель управления (теперь тут только кнопка настроек)
control_frame = ttk.Frame(root, padding=10)
control_frame.pack(side=tk.TOP, fill=tk.X)

# 4. Настройка области для графика Matplotlib
fig = Figure(figsize=(10, 6))
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()


# 5. Функция обновления графика
def update_plot():
    ax.clear()
    ax.set_axis_on()

    # Берем параметры из словаря настроек
    method = app_settings["method"]
    metric = app_settings["metric"]

    # Защита от несовместимых параметров
    if method in ["ward", "centroid", "median"] and metric != "euclidean":
        ax.text(
            0.5,
            0.5,
            f"⚠️ ОШИБКА:\nМетод '{method}' работает ТОЛЬКО с 'euclidean'.",
            ha="center",
            va="center",
            fontsize=14,
            color="red",
        )
        ax.set_axis_off()
        canvas.draw()
        return

    # Рисуем дендрограмму
    Z = linkage(df_samples, method=method, metric=metric)
    dendrogram(
        Z, labels=labels, orientation="right", leaf_rotation=0, leaf_font_size=10, ax=ax
    )

    # Применение настроек осей
    ax.set_title(f"{method.capitalize()} & {metric.capitalize()} & {file}", fontsize=14)
    ax.set_xlabel(app_settings["xlabel"], fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Применяем пользовательские лимиты, если они заданы
    current_xlim = ax.get_xlim()
    new_xmin, new_xmax = current_xlim[0], current_xlim[1]

    if app_settings["xmin"].strip():
        try:
            new_xmin = float(app_settings["xmin"])
        except ValueError:
            pass

    if app_settings["xmax"].strip():
        try:
            new_xmax = float(app_settings["xmax"])
        except ValueError:
            pass

    ax.set_xlim(new_xmin, new_xmax)

    fig.tight_layout()
    canvas.draw()


# 6. ФУНКЦИЯ И ОКНО ДЛЯ ВСЕХ НАСТРОЕК
def open_settings():
    dialog = tk.Toplevel(root)
    dialog.title("Настройки графика")
    dialog.geometry("350x400")
    dialog.transient(root)
    dialog.grab_set()

    # Локальные переменные для окна (чтобы не применять, если нажали крестик)
    method_var = tk.StringVar(value=app_settings["method"])
    metric_var = tk.StringVar(value=app_settings["metric"])
    xlabel_var = tk.StringVar(value=app_settings["xlabel"])
    xmin_var = tk.StringVar(value=app_settings["xmin"])
    xmax_var = tk.StringVar(value=app_settings["xmax"])

    # Кластеризация
    ttk.Label(dialog, text="--- Кластеризация ---", font=("", 10, "bold")).pack(
        pady=(10, 5)
    )

    ttk.Label(dialog, text="Метод:").pack()
    ttk.Combobox(
        dialog,
        textvariable=method_var,
        state="readonly",
        values=[
            "average",
            "ward",
            "centroid",
            "median",
            "single",
            "complete",
            "weighted",
        ],
    ).pack(fill=tk.X, padx=40)

    ttk.Label(dialog, text="Метрика:").pack(pady=(5, 0))
    ttk.Combobox(
        dialog,
        textvariable=metric_var,
        state="readonly",
        values=["euclidean", "cosine", "cityblock", "correlation", "braycurtis"],
    ).pack(fill=tk.X, padx=40)

    # Оси
    ttk.Label(dialog, text="Оси", font=("", 10, "bold")).pack(pady=(15, 5))

    ttk.Label(dialog, text="Подпись оси X:").pack()
    ttk.Entry(dialog, textvariable=xlabel_var).pack(fill=tk.X, padx=40)

    ttk.Label(dialog, text="Минимум X (пусто = авто):").pack(pady=(5, 0))
    ttk.Entry(dialog, textvariable=xmin_var).pack(fill=tk.X, padx=40)

    ttk.Label(dialog, text="Максимум X (пусто = авто):").pack(pady=(5, 0))
    ttk.Entry(dialog, textvariable=xmax_var).pack(fill=tk.X, padx=40)

    # Функция сохранения и применения
    def apply_settings():
        app_settings["method"] = method_var.get()
        app_settings["metric"] = metric_var.get()
        app_settings["xlabel"] = xlabel_var.get()
        app_settings["xmin"] = xmin_var.get()
        app_settings["xmax"] = xmax_var.get()

        update_plot()
        # dialog.destroy()

    ttk.Button(dialog, text="Применить", command=apply_settings).pack(pady=20)


# КНОПКА ВЫЗОВА НАСТРОЕК
btn_settings = ttk.Button(control_frame, text="⚙ Настройки", command=open_settings)
btn_settings.pack(side=tk.LEFT, padx=10)

# Рисуем график при запуске и открываем окно
update_plot()
root.mainloop()

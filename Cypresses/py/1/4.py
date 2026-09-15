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
    # Тестовый MultiIndex DataFrame
    arrays = [
        ["Кипарис А", "Кипарис А", "Кипарис Б", "Кипарис Б", "Сосна"],
        ["Подвид 1", "Подвид 2", "Подвид 1", "Подвид 2", "Обыкновенная"],
        ["ID_01", "ID_02", "ID_03", "ID_04", "ID_05"],
    ]
    df = pd.DataFrame([[1, 2], [3, 4], [10, 12], [11, 13], [20, 25]], index=arrays)

# Убираем пустые строки
df_samples = df.loc[(df != 0).any(axis=1)]

# Получаем список всех уникальных "видов" (Уровень 0 из индекса)
unique_species = df_samples.index.get_level_values(0).unique().tolist()

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
    "selected_species": unique_species.copy(),  # По умолчанию выбраны все виды
    "show_l0": True,  # Показывать 1-й столбец индекса
    "show_l1": True,  # Показывать 2-й столбец индекса
    "show_l2": True,  # Показывать 3-й столбец индекса
}

# 3. Панель управления
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

    method = app_settings["method"]
    metric = app_settings["metric"]
    selected_sp = app_settings["selected_species"]

    # Проверка: выбран ли хотя бы один вид
    if not selected_sp:
        ax.text(
            0.5,
            0.5,
            "⚠️ ОШИБКА:\nНе выбран ни один вид для отображения.\nЗайдите в настройки.",
            ha="center",
            va="center",
            fontsize=14,
            color="red",
        )
        ax.set_axis_off()
        canvas.draw()
        return

    # ФИЛЬТРАЦИЯ ДАННЫХ ПО ВЫБРАННЫМ ВИДАМ
    mask = df_samples.index.get_level_values(0).isin(selected_sp)
    filtered_df = df_samples[mask]

    # Проверка: достаточно ли данных для кластеризации
    if len(filtered_df) < 2:
        ax.text(
            0.5,
            0.5,
            "⚠️ ОШИБКА:\nСлишком мало данных для кластеризации.\nВыберите больше видов.",
            ha="center",
            va="center",
            fontsize=14,
            color="red",
        )
        ax.set_axis_off()
        canvas.draw()
        return

    if method in ["centroid", "median", "ward"] and metric != "euclidean":
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

    # ФОРМИРОВАНИЕ ПОДПИСЕЙ ОСИ Y (на основе настроек)
    labels = []
    for idx in filtered_df.index:
        parts = []
        if app_settings["show_l0"]:
            parts.append(str(idx[0]))
        if app_settings["show_l1"]:
            parts.append(str(idx[1]))
        if app_settings["show_l2"]:
            parts.append(str(idx[2]))
        labels.append(" ".join(parts) if parts else "-")

    # Рисуем дендрограмму
    Z = linkage(filtered_df, method=method, metric=metric)
    dendrogram(
        Z, labels=labels, orientation="right", leaf_rotation=0, leaf_font_size=10, ax=ax
    )

    # Применение настроек осей
    ax.set_title(f"{method.capitalize()} & {metric.capitalize()} & {file}", fontsize=14)
    ax.set_xlabel(app_settings["xlabel"], fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.7)

    # Лимиты оси X
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


# 6. ФУНКЦИЯ И ОКНО ДЛЯ ВСЕХ НАСТРОЕК (С ВКЛАДКАМИ)
def open_settings():
    dialog = tk.Toplevel(root)
    dialog.title("Настройки графика")
    dialog.geometry("420x450")
    dialog.transient(root)
    dialog.grab_set()

    # Создаем панель с вкладками
    notebook = ttk.Notebook(dialog)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- ВКЛАДКА 1: ДАННЫЕ И МЕТОДЫ ---
    tab_data = ttk.Frame(notebook)
    notebook.add(tab_data, text="Данные и Метод")

    method_var = tk.StringVar(value=app_settings["method"])
    metric_var = tk.StringVar(value=app_settings["metric"])

    ttk.Label(tab_data, text="Метод кластеризации:").pack(pady=(10, 2))
    ttk.Combobox(
        tab_data,
        textvariable=method_var,
        state="readonly",
        values=[
            "ward",
            "median",
            "centroid",
            "average",
            "single",
            "complete",
            "weighted",
        ],
    ).pack(fill=tk.X, padx=20)

    ttk.Label(tab_data, text="Метрика:").pack(pady=(10, 2))
    ttk.Combobox(
        tab_data,
        textvariable=metric_var,
        state="readonly",
        values=["euclidean", "cityblock", "cosine", "correlation", "braycurtis"],
    ).pack(fill=tk.X, padx=20)

    ttk.Label(tab_data, text="Какие виды участвуют (Уровень 0):").pack(pady=(15, 2))

    # Список видов с прокруткой
    list_frame = ttk.Frame(tab_data)
    list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
    species_listbox = tk.Listbox(
        list_frame, selectmode=tk.EXTENDED, yscrollcommand=scrollbar.set, height=6
    )
    scrollbar.config(command=species_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    species_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Заполняем список видов и выделяем те, что были выбраны ранее
    for i, sp in enumerate(unique_species):
        species_listbox.insert(tk.END, sp)
        if sp in app_settings["selected_species"]:
            species_listbox.selection_set(i)

    # --- ВКЛАДКА 2: ОСИ И ПОДПИСИ ---
    tab_axes = ttk.Frame(notebook)
    notebook.add(tab_axes, text="Оси и Подписи")

    xlabel_var = tk.StringVar(value=app_settings["xlabel"])
    xmin_var = tk.StringVar(value=app_settings["xmin"])
    xmax_var = tk.StringVar(value=app_settings["xmax"])
    l0_var = tk.BooleanVar(value=app_settings["show_l0"])
    l1_var = tk.BooleanVar(value=app_settings["show_l1"])
    l2_var = tk.BooleanVar(value=app_settings["show_l2"])

    ttk.Label(
        tab_axes, text="Что отображать в подписях (Ось Y):", font=("", 10, "bold")
    ).pack(pady=(10, 5))
    ttk.Checkbutton(tab_axes, text="Уровень 0 (Вид)", variable=l0_var).pack(
        anchor=tk.W, padx=20
    )
    ttk.Checkbutton(tab_axes, text="Уровень 1 (Подвид/Группа)", variable=l1_var).pack(
        anchor=tk.W, padx=20
    )
    ttk.Checkbutton(tab_axes, text="Уровень 2 (ID образца)", variable=l2_var).pack(
        anchor=tk.W, padx=20
    )

    ttk.Label(tab_axes, text="Настройки оси X:", font=("", 10, "bold")).pack(
        pady=(15, 5)
    )
    ttk.Label(tab_axes, text="Подпись оси X:").pack()
    ttk.Entry(tab_axes, textvariable=xlabel_var).pack(fill=tk.X, padx=20)

    ttk.Label(tab_axes, text="Минимум X (пусто = авто):").pack(pady=(5, 0))
    ttk.Entry(tab_axes, textvariable=xmin_var).pack(fill=tk.X, padx=20)

    ttk.Label(tab_axes, text="Максимум X (пусто = авто):").pack(pady=(5, 0))
    ttk.Entry(tab_axes, textvariable=xmax_var).pack(fill=tk.X, padx=20)

    # --- КНОПКА ПРИМЕНИТЬ ---
    def apply_settings():
        # Сохраняем выбранные виды
        selected_indices = species_listbox.curselection()
        app_settings["selected_species"] = [
            species_listbox.get(i) for i in selected_indices
        ]

        # Сохраняем остальные настройки
        app_settings["method"] = method_var.get()
        app_settings["metric"] = metric_var.get()
        app_settings["xlabel"] = xlabel_var.get()
        app_settings["xmin"] = xmin_var.get()
        app_settings["xmax"] = xmax_var.get()
        app_settings["show_l0"] = l0_var.get()
        app_settings["show_l1"] = l1_var.get()
        app_settings["show_l2"] = l2_var.get()

        update_plot()
        dialog.destroy()

    ttk.Button(dialog, text="Применить настройки", command=apply_settings).pack(
        pady=(0, 10)
    )


# КНОПКА ВЫЗОВА НАСТРОЕК
btn_settings = ttk.Button(control_frame, text="⚙ Настройки", command=open_settings)
btn_settings.pack(side=tk.LEFT, padx=10)

# Рисуем график при запуске
update_plot()
root.mainloop()

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
        ["Объект 1", "Объект 2", "Объект 1", "Объект 2", "Объект 3"],
        ["Дерево_01", "Дерево_02", "Дерево_03", "Дерево_04", "Дерево_05"]
    ]
    df = pd.DataFrame([[1, 2], [3, 4], [10, 12], [11, 13], [20, 25]], index=arrays)

# Убираем пустые строки
df_samples = df.loc[(df != 0).any(axis=1)]

# Получаем уникальные значения для каждого уровня индекса
unique_l0 = df_samples.index.get_level_values(0).unique().tolist()
unique_l1 = df_samples.index.get_level_values(1).unique().tolist()
unique_l2 = df_samples.index.get_level_values(2).unique().tolist()

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
    "selected_l0": unique_l0.copy(),
    "selected_l1": unique_l1.copy(),
    "selected_l2": unique_l2.copy(),
    "show_l0": True,
    "show_l1": True,
    "show_l2": True
}

# Глобальная переменная для хранения ID события мыши (чтобы не дублировать)
hover_cid = None

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
    global hover_cid
    
    # Отключаем старый обработчик мыши, если он был
    if hover_cid is not None:
        canvas.mpl_disconnect(hover_cid)
        hover_cid = None

    ax.clear()
    ax.set_axis_on()
    
    method = app_settings["method"]
    metric = app_settings["metric"]

    # ФИЛЬТРАЦИЯ ДАННЫХ ПО ВСЕМ ТРЕМ УРОВНЯМ
    mask = (
        df_samples.index.get_level_values(0).isin(app_settings["selected_l0"]) &
        df_samples.index.get_level_values(1).isin(app_settings["selected_l1"]) &
        df_samples.index.get_level_values(2).isin(app_settings["selected_l2"])
    )
    filtered_df = df_samples[mask]

    # Проверки на ошибки
    if len(filtered_df) < 2:
        ax.text(0.5, 0.5, "⚠️ ОШИБКА:\nСлишком мало данных для кластеризации.\nПроверьте фильтры в настройках.",
                ha="center", va="center", fontsize=14, color="red")
        ax.set_axis_off()
        canvas.draw()
        return

    if method in ["ward", "centroid", "median"] and metric != "euclidean":
        ax.text(0.5, 0.5, f"⚠️ ОШИБКА:\nМетод '{method}' работает ТОЛЬКО с 'euclidean'.",
                ha="center", va="center", fontsize=14, color="red")
        ax.set_axis_off()
        canvas.draw()
        return

    # ФОРМИРОВАНИЕ ПОДПИСЕЙ ОСИ Y
    labels = []
    for idx in filtered_df.index:
        parts = []
        if app_settings["show_l0"]: parts.append(str(idx[0]))
        if app_settings["show_l1"]: parts.append(str(idx[1]))
        if app_settings["show_l2"]: parts.append(str(idx[2]))
        labels.append(" | ".join(parts) if parts else "-")

    # Рисуем дендрограмму и сохраняем результат (R) для координат
    Z = linkage(filtered_df, method=method, metric=metric)
    R = dendrogram(Z, labels=labels, orientation="right", leaf_rotation=0, leaf_font_size=10, ax=ax)

    # --- НАСТРОЙКА ВСПЛЫВАЮЩИХ ПОДСКАЗОК (HOVER) ---
    # Собираем координаты вертикальных линий слияния кластеров
    merge_lines = []
    for i, d in zip(R['icoord'], R['dcoord']):
        # dcoord - это X (расстояние), icoord - это Y (позиция узлов)
        x_val = d[1] # Координата X линии слияния
        y_min = min(i[1], i[2])
        y_max = max(i[1], i[2])
        merge_lines.append((x_val, y_min, y_max))

    # Создаем объект аннотации (изначально скрыт)
    annot = ax.annotate("", xy=(0,0), xytext=(10, 10), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.4", fc="lightyellow", ec="black", lw=1),
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3"), zorder=10)
    annot.set_visible(False)

    def on_hover(event):
        if event.inaxes == ax and event.xdata is not None and event.ydata is not None:
            x, y = event.xdata, event.ydata
            
            # Порог срабатывания (3% от ширины графика)
            x_range = ax.get_xlim()[1] - ax.get_xlim()[0]
            x_thresh = x_range * 0.03 
            
            closest_dist = float('inf')
            best_line = None
            
            # Ищем ближайшую линию слияния
            for (x_val, y_min, y_max) in merge_lines:
                if abs(x - x_val) < x_thresh and y_min <= y <= y_max:
                    if abs(x - x_val) < closest_dist:
                        closest_dist = abs(x - x_val)
                        best_line = (x_val, y) # Привязываем Y к положению мыши
            
            if best_line:
                annot.xy = best_line
                annot.set_text(f"Расстояние: {best_line[0]:.3f}")
                annot.set_visible(True)
                canvas.draw_idle()
            else:
                if annot.get_visible():
                    annot.set_visible(False)
                    canvas.draw_idle()

    # Подключаем событие движения мыши
    hover_cid = canvas.mpl_connect("motion_notify_event", on_hover)

    # --- ПРИМЕНЕНИЕ НАСТРОЕК ОСЕЙ ---
    ax.set_title(f"{method.capitalize()} & {metric.capitalize()} & {file}", fontsize=14)
    ax.set_xlabel(app_settings["xlabel"], fontsize=12)
    ax.grid(axis="x", linestyle="--", alpha=0.7)
    
    current_xlim = ax.get_xlim()
    new_xmin, new_xmax = current_xlim[0], current_xlim[1]
    if app_settings["xmin"].strip():
        try: new_xmin = float(app_settings["xmin"])
        except ValueError: pass
    if app_settings["xmax"].strip():
        try: new_xmax = float(app_settings["xmax"])
        except ValueError: pass
    ax.set_xlim(new_xmin, new_xmax)

    fig.tight_layout()
    canvas.draw()

# 6. ФУНКЦИЯ И ОКНО ДЛЯ ВСЕХ НАСТРОЕК
def open_settings():
    dialog = tk.Toplevel(root)
    dialog.title("Настройки графика")
    dialog.geometry("650x500") # Увеличили окно, чтобы влезли 3 списка
    dialog.transient(root)
    dialog.grab_set()

    notebook = ttk.Notebook(dialog)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- ВКЛАДКА 1: ДАННЫЕ И МЕТОДЫ ---
    tab_data = ttk.Frame(notebook)
    notebook.add(tab_data, text="Данные и Метод")

    # Верхняя часть: Метод и Метрика
    top_frame = ttk.Frame(tab_data)
    top_frame.pack(fill=tk.X, pady=10)
    
    method_var = tk.StringVar(value=app_settings["method"])
    metric_var = tk.StringVar(value=app_settings["metric"])

    ttk.Label(top_frame, text="Метод:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.E)
    ttk.Combobox(top_frame, textvariable=method_var, state="readonly", 
                 values=["ward", "average", "single", "complete", "weighted", "centroid"]).grid(row=0, column=1, sticky=tk.W)

    ttk.Label(top_frame, text="Метрика:").grid(row=0, column=2, padx=10, pady=5, sticky=tk.E)
    ttk.Combobox(top_frame, textvariable=metric_var, state="readonly", 
                 values=["euclidean", "cosine", "cityblock", "correlation", "braycurtis"]).grid(row=0, column=3, sticky=tk.W)

    # Нижняя часть: Три списка для фильтрации
    ttk.Label(tab_data, text="Фильтр данных (зажмите Ctrl для выбора нескольких):", font=("", 10, "bold")).pack(pady=(10, 5))
    
    lists_frame = ttk.Frame(tab_data)
    lists_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    lists_frame.columnconfigure(0, weight=1)
    lists_frame.columnconfigure(1, weight=1)
    lists_frame.columnconfigure(2, weight=1)

    # Вспомогательная функция для создания списков
    def create_listbox(parent, title, items, selected_items, col):
        frame = ttk.Frame(parent)
        frame.grid(row=0, column=col, sticky="nsew", padx=5)
        ttk.Label(frame, text=title).pack(anchor=tk.W)
        
        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        # exportselection=False ВАЖЕН! Иначе при клике на один список, сбрасывается выделение в других
        lb = tk.Listbox(frame, selectmode=tk.MULTIPLE, yscrollcommand=scroll.set, exportselection=False)
        scroll.config(command=lb.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        for i, item in enumerate(items):
            lb.insert(tk.END, item)
            if item in selected_items:
                lb.selection_set(i)
        return lb

    lb_l0 = create_listbox(lists_frame, "l0 - Species", unique_l0, app_settings["selected_l0"], 0)
    lb_l1 = create_listbox(lists_frame, "l1 - Object", unique_l1, app_settings["selected_l1"], 1)
    lb_l2 = create_listbox(lists_frame, "l2 - Tree", unique_l2, app_settings["selected_l2"], 2)

    # --- ВКЛАДКА 2: ОСИ И ПОДПИСИ ---
    tab_axes = ttk.Frame(notebook)
    notebook.add(tab_axes, text="Оси и Подписи")

    xlabel_var = tk.StringVar(value=app_settings["xlabel"])
    xmin_var = tk.StringVar(value=app_settings["xmin"])
    xmax_var = tk.StringVar(value=app_settings["xmax"])
    l0_var = tk.BooleanVar(value=app_settings["show_l0"])
    l1_var = tk.BooleanVar(value=app_settings["show_l1"])
    l2_var = tk.BooleanVar(value=app_settings["show_l2"])

    ttk.Label(tab_axes, text="Что отображать в подписях (Ось Y):", font=("", 10, "bold")).pack(pady=(10, 5))
    ttk.Checkbutton(tab_axes, text="l0 - Species", variable=l0_var).pack(anchor=tk.W, padx=20)
    ttk.Checkbutton(tab_axes, text="l1 - Object", variable=l1_var).pack(anchor=tk.W, padx=20)
    ttk.Checkbutton(tab_axes, text="l2 - Tree", variable=l2_var).pack(anchor=tk.W, padx=20)

    ttk.Label(tab_axes, text="Настройки оси X:", font=("", 10, "bold")).pack(pady=(15, 5))
    ttk.Label(tab_axes, text="Подпись оси X:").pack()
    ttk.Entry(tab_axes, textvariable=xlabel_var).pack(fill=tk.X, padx=20)

    ttk.Label(tab_axes, text="Минимум X (пусто = авто):").pack(pady=(5, 0))
    ttk.Entry(tab_axes, textvariable=xmin_var).pack(fill=tk.X, padx=20)

    ttk.Label(tab_axes, text="Максимум X (пусто = авто):").pack(pady=(5, 0))
    ttk.Entry(tab_axes, textvariable=xmax_var).pack(fill=tk.X, padx=20)

    # --- КНОПКА ПРИМЕНИТЬ ---
    def apply_settings():
        # Сохраняем выбранные элементы из всех трех списков
        app_settings["selected_l0"] = [lb_l0.get(i) for i in lb_l0.curselection()]
        app_settings["selected_l1"] = [lb_l1.get(i) for i in lb_l1.curselection()]
        app_settings["selected_l2"] = [lb_l2.get(i) for i in lb_l2.curselection()]
        
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

    ttk.Button(dialog, text="Применить настройки", command=apply_settings).pack(pady=(0, 10))

# КНОПКА ВЫЗОВА НАСТРОЕК
btn_settings = ttk.Button(control_frame, text="⚙ Настройки", command=open_settings)
btn_settings.pack(side=tk.LEFT, padx=10)

# Рисуем график при запуске
update_plot()
root.mainloop()
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
from tkinter import ttk
from utils import format_list
import matplotlib.pyplot as plt
import numpy as np
import polars as pl
import seaborn as sns
import tkinter as tk

# ==========================================
# 1. ЧТЕНИЕ ДАННЫХ
# ==========================================
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,PartsPerMillion,Percent.txt")

epsilon_val = np.finfo(float).eps


# ==========================================
# 2. ИНТЕРФЕЙС (TKINTER)
# ==========================================
root = tk.Tk()
root.title("Анализ профиля жирных кислот")
root.geometry("1200x900")  # Стартовый размер окна

# Создаем верхнюю панель для выпадающих списков
frame_controls = tk.Frame(root, padx=10, pady=10)
frame_controls.pack(side=tk.TOP, fill=tk.X)

# Выпадающий список для метода трансформации
tk.Label(frame_controls, text="Transform method:", font=("Arial", 12)).pack(
    side=tk.LEFT
)
combo_transform_method = ttk.Combobox(
    frame_controls,
    values=["epsilon", "log1p"],
    state="readonly",
    font=("Arial", 12),
)
combo_transform_method.current(0)  # По умолчанию выбран первый элемент
combo_transform_method.pack(side=tk.LEFT, padx=10)

# Выпадающий список для выбора исходных данных
tk.Label(frame_controls, text="Source data:", font=("Arial", 12)).pack(side=tk.LEFT)
combo_source_data = ttk.Combobox(
    frame_controls,
    values=["Percent", "PartsPerMillion"],
    state="readonly",
    font=("Arial", 12),
)
combo_source_data.current(0)
combo_source_data.pack(side=tk.LEFT, padx=10)

# Выпадающий список для выбора точности округления
tk.Label(frame_controls, text="Round decimals:", font=("Arial", 12)).pack(side=tk.LEFT)
combo_round = ttk.Combobox(
    frame_controls,
    values=[1, 2, 3, 4, 5, 6],
    state="readonly",
    font=("Arial", 12),
)
combo_round.current(0)
combo_round.pack(side=tk.LEFT, padx=10)


# ==========================================
# 3. НАСТРОЙКА ГРАФИКА (MATPLOTLIB)
# ==========================================
fig, axes = plt.subplots(1, 2, figsize=(12, 8), sharey=True)
plt.subplots_adjust(bottom=0.1, right=0.9)
cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])

# Встраиваем график в окно Tkinter
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Добавляем стандартную панель инструментов Matplotlib (для сохранения, зума и т.д.)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()


# ==========================================
# 4. ФУНКЦИЯ ПЕРЕСЧЕТА И ПЕРЕРИСОВКИ
# ==========================================
def update_plot(event=None):
    # Считываем значения из Combo Box
    method = combo_transform_method.get()
    target_col = combo_source_data.get()
    round_decimals = int(combo_round.get())

    # --- А. ПОДГОТОВКА ДАННЫХ ---
    if method == "epsilon":
        transform_expr = (
            pl.when(pl.col(target_col) == 0)
            .then(pl.col(target_col) + epsilon_val)
            .otherwise(pl.col(target_col))
        )
    else:
        transform_expr = pl.col(target_col).log1p()

    df_calc = (
        df.filter(
            (pl.col("FattyAcid") != "17:0")
            & (pl.col("FattyAcid") != "14:0")
            & (pl.col("FattyAcid") != "15:0")
        )
        .filter(pl.col("Plant") != 37)
        .with_columns(transform_expr.alias("ProcessedValue"))
    )

    # ИЗМЕНЕНИЕ 1: Считаем ДВА средних.
    # ProcessedValue - для t-test'а.
    # target_col (Original_Mean) - для расчета Log2FC и вывода на экран.
    df_agg = df_calc.group_by(["Ni", "Week", "FattyAcid"], maintain_order=True).agg(
        Plants=pl.col("Plant"),
        Values=pl.col("ProcessedValue"),  # Трансформированные значения для t-test
        Original_Mean=pl.col(target_col).mean(),  # Оригинальные значения для Log2FC
        Values_StandardDeviation=pl.col(target_col).std(),
    )

    # Защита от деления на ноль при расчете Log2FC
    df_agg = df_agg.with_columns(
        Safe_Original_Mean=pl.when(pl.col("Original_Mean") == 0)
        .then(epsilon_val)
        .otherwise(pl.col("Original_Mean"))
    )

    df_ctrl = df_agg.filter(pl.col("Ni") == 0).select(
        pl.col("Week"),
        pl.col("FattyAcid"),
        pl.col("Plants").alias("Ctrl_Plants"),
        pl.col("Values").alias("Ctrl_Values"),
        pl.col("Values_StandardDeviation").alias("Ctrl_StandardDeviation"),
        pl.col("Safe_Original_Mean").alias("Ctrl_Mean"),  # Берем оригинальное среднее
    )

    df_treat = df_agg.filter(pl.col("Ni") != 0).select(
        pl.col("Week"),
        pl.col("FattyAcid"),
        pl.col("Ni"),
        pl.col("Plants").alias("Treat_Plants"),
        pl.col("Values").alias("Treat_Values"),
        pl.col("Values_StandardDeviation").alias("Treat_StandardDeviation"),
        pl.col("Safe_Original_Mean").alias("Treat_Mean"),  # Берем оригинальное среднее
    )

    df_joined = df_treat.join(df_ctrl, on=["Week", "FattyAcid"], how="left")

    # ИЗМЕНЕНИЕ 2: Log2FC теперь ВСЕГДА считается одинаково и математически верно,
    # так как мы используем оригинальные средние значения.
    df_joined = df_joined.with_columns(
        Log2FC=(pl.col("Treat_Mean") / pl.col("Ctrl_Mean")).log(2)
    )

    # --- Б. СТАТИСТИКА ---
    # t-test по-прежнему делается на трансформированных данных (Treat_Values / Ctrl_Values)
    treat_lists = df_joined["Treat_Values"].to_list()
    ctrl_lists = df_joined["Ctrl_Values"].to_list()
    p_values = []

    for t_vals, c_vals in zip(treat_lists, ctrl_lists):
        t_clean = [x for x in t_vals if x is not None and not np.isnan(x)]
        c_clean = [x for x in c_vals if x is not None and not np.isnan(x)]
        if len(t_clean) >= 2 and len(c_clean) >= 2:
            stat, p = ttest_ind(t_clean, c_clean, equal_var=False)
            p_values.append(p)
        else:
            p_values.append(np.nan)

    df_joined = df_joined.with_columns(p_value=pl.Series(p_values))

    # Сохранение в файл (оставил как у вас)
    df_joined.with_columns(
        [
            format_list("Treat_Plants", round_decimals),
            format_list("Treat_Values", round_decimals),
            format_list("Ctrl_Plants", round_decimals),
            format_list("Ctrl_Values", round_decimals),
        ]
    ).write_csv("Даша/df_joined.txt")

    valid_mask = df_joined["p_value"].is_not_null() & ~df_joined["p_value"].is_nan()
    df_valid = df_joined.filter(valid_mask)

    if df_valid.height > 0:
        p_vals_valid = df_valid["p_value"].to_numpy()
        _, q_vals_valid, _, _ = multipletests(p_vals_valid, method="fdr_bh")
        df_valid = df_valid.with_columns(q_value=pl.Series(q_vals_valid))
        df_joined = df_joined.join(
            df_valid.select(["Week", "FattyAcid", "Ni", "q_value"]),
            on=["Week", "FattyAcid", "Ni"],
            how="left",
            maintain_order="left_right",
        )
    else:
        df_joined = df_joined.with_columns(q_value=pl.lit(None, dtype=pl.Float64))

    # ИЗМЕНЕНИЕ 3: Человекочитаемый Fold Change.
    # Возводим 2 в степень МОДУЛЯ Log2FC.
    # Если Log2FC = 2, FC = 4 (выросло в 4 раза). Если Log2FC = -2, FC = 4 (упало в 4 раза).
    df_joined = df_joined.with_columns(
        FoldChange=(2 ** pl.col("Log2FC").abs()).round(round_decimals)
    )

    # ИЗМЕНЕНИЕ 4: Красивое форматирование текста для хитмапа
    # Звездочки с переносом строки (если значимо)
    stars = (
        pl.when(pl.col("q_value") < 0.001)
        .then(pl.lit("***"))
        .when(pl.col("q_value") < 0.01)
        .then(pl.lit("**"))
        .when(pl.col("q_value") < 0.05)
        .then(pl.lit("*"))
        .otherwise(pl.lit(""))
    )

    # Стрелочки (используем порог 0.01 для исключения микро-шумов float)
    arrows = (
        pl.when(pl.col("Log2FC") > 0.01)
        .then(pl.format("⬈ {}x", pl.col("FoldChange")))
        .when(pl.col("Log2FC") < -0.01)
        .then(pl.format("⬊ {}x", pl.col("FoldChange")))
        .otherwise(pl.lit("без изм."))
    )

    # Собираем итоговую строку
    df_joined = df_joined.with_columns(
        Significance=pl.format(
            "{}({})\n{}±{}\n{}±{}",
            stars,
            arrows,
            pl.col("Treat_Mean").round(round_decimals),
            pl.col("Treat_StandardDeviation").round(round_decimals),
            pl.col("Ctrl_Mean").round(round_decimals),
            pl.col("Ctrl_StandardDeviation").round(round_decimals),
        )
    )

    # --- В. ОТРИСОВКА ---
    df_plot = df_joined.select(
        ["Week", "FattyAcid", "Ni", "Log2FC", "Significance"]
    ).to_pandas()

    axes[0].clear()
    axes[1].clear()
    cbar_ax.clear()

    fig.suptitle(
        f"Изменение профиля жирных кислот при стрессе (Ni vs Ni=0)\n"
        f"Метод: {method.upper()} | Колонка: {target_col.upper()}\n"
        f"Log2FC, Welch's t-test, Benjamini/Hochberg",
        fontsize=14,
    )

    # Заданный порядок для основных ЖК
    priority_fa = [
        "16:0",
        "9-16:1",
        "18:0",
        "11-Me-12-18:1",
        "9-18:1",
        "11-18:1",
        "9,12-18:2",
        "9,12,15-18:3",
    ]

    for i, week in enumerate([1, 5]):
        df_w = df_plot[df_plot["Week"] == week]
        if df_w.empty:
            continue

        # Получаем все уникальные ЖК для текущей недели.
        # Порядок здесь соответствует исходному порядку в вашем txt-файле
        unique_fa = df_w["FattyAcid"].drop_duplicates().tolist()

        # 1. Выбираем те, что есть в приоритетном списке (сохраняя заданный порядок priority_fa)
        top_fa = [fa for fa in priority_fa if fa in unique_fa]

        # 2. Выбираем остальные (20 атомов и более) и ОСТАВЛЯЕМ ИХ В ИСХОДНОМ ПОРЯДКЕ
        other_fa = [fa for fa in unique_fa if fa not in priority_fa]

        # 3. Формируем итоговый список.
        # Добавляем строку " " (пробел) как визуальный разделитель, если есть "остальные" ЖК
        if other_fa:
            ordered_fa = top_fa + [" "] + other_fa
        else:
            ordered_fa = top_fa

        # Пересобираем таблицы. reindex автоматически создаст пустую строку из NaN для " "
        pivot_log2fc = df_w.pivot(
            index="FattyAcid", columns="Ni", values="Log2FC"
        ).reindex(ordered_fa)

        # fillna("") нужен, чтобы в пустой строке-разделителе не писалось слово "nan"
        pivot_sig = (
            df_w.pivot(index="FattyAcid", columns="Ni", values="Significance")
            .reindex(ordered_fa)
            .fillna("")
        )

        sns.heatmap(
            pivot_log2fc,
            annot=pivot_sig,
            fmt="",
            cmap="vlag",
            center=0,
            ax=axes[i],
            cbar=(i == 1),
            cbar_ax=cbar_ax if i == 1 else None,
            linewidths=0.5,
            linecolor="gray",
            annot_kws={"size": 8, "weight": "bold", "color": "black"},
        )

        axes[i].set_title(f"Неделя {week}", fontsize=14)
        axes[i].set_xlabel("Концентрация Ni (mM)", fontsize=12)
        if i == 0:
            axes[i].set_ylabel("Жирные кислоты", fontsize=12)
        else:
            axes[i].set_ylabel("")

    # Обновляем холст
    canvas.draw()


# ==========================================
# 5. ЗАПУСК
# ==========================================
# Привязываем обновление графика к выбору в выпадающих списках
combo_transform_method.bind("<<ComboboxSelected>>", update_plot)
combo_source_data.bind("<<ComboboxSelected>>", update_plot)
combo_round.bind("<<ComboboxSelected>>", update_plot)

# Первичная отрисовка при запуске
update_plot()

# Запуск оконного приложения
root.mainloop()

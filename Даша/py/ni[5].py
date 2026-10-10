import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import polars as pl
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import seaborn as sns
import matplotlib.pyplot as plt

# ==========================================
# 1. ЧТЕНИЕ ДАННЫХ
# ==========================================
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")


epsilon_val = np.finfo(float).eps


def format_list(name):
    return pl.format(
        "[{}]", pl.col(name).cast(pl.List(pl.String)).list.join(",")
    ).alias(name)


# ==========================================
# 2. ИНТЕРФЕЙС (TKINTER)
# ==========================================
root = tk.Tk()
root.title("Анализ профиля жирных кислот")
root.geometry("1200x900")  # Стартовый размер окна

# Создаем верхнюю панель для выпадающих списков
frame_controls = tk.Frame(root, padx=10, pady=10)
frame_controls.pack(side=tk.TOP, fill=tk.X)

# Выпадающий список для метода
tk.Label(frame_controls, text="Метод расчета:", font=("Arial", 12)).pack(side=tk.LEFT)
combo_method = ttk.Combobox(
    frame_controls,
    values=["epsilon", "log1p"],
    state="readonly",
    font=("Arial", 12),
    width=10,
)
combo_method.current(0)  # По умолчанию выбран первый элемент
combo_method.pack(side=tk.LEFT, padx=10)

# Выпадающий список для колонки
tk.Label(frame_controls, text="Колонка данных:", font=("Arial", 12)).pack(
    side=tk.LEFT, padx=(20, 0)
)
combo_col = ttk.Combobox(
    frame_controls,
    values=["pct", "ppm"],
    state="readonly",
    font=("Arial", 12),
    width=10,
)
combo_col.current(0)
combo_col.pack(side=tk.LEFT, padx=10)

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
    df_calc = (
        df.filter(pl.col("FattyAcid") != "17:0")
        .filter(pl.col("Plant") != 37)
        .with_columns(
            # Считаем долю в процентах
            pct=(pl.col("ppm") / pl.col("ppm").sum() * 100).over(
                ["Ni", "Week", "Plant"]
            )
        )
    )
    print(f"df_calc: {df_calc}")
    df_calc.write_csv("Даша/df_calc.txt")

    # Считываем значения из Combo Box
    method = combo_method.get()
    target_col = combo_col.get()

    # --- А. ПОДГОТОВКА ДАННЫХ ---
    if method == "epsilon":
        transform_expr = (
            pl.when(pl.col(target_col) == 0)
            .then(pl.col(target_col) + epsilon_val)
            .otherwise(pl.col(target_col))
        )
    else:
        transform_expr = pl.col(target_col).log1p()
    df_calc = df_calc.with_columns(transform_expr.alias("processed_val"))

    df_agg = df_calc.group_by(["Ni", "Week", "FattyAcid"], maintain_order=True).agg(
        Plants=pl.col("Plant"),
        values=pl.col("processed_val"),
        mean_val=pl.col("processed_val").mean(),
    )

    df_ctrl = df_agg.filter(pl.col("Ni") == 0).select(
        pl.col("Week"),
        pl.col("FattyAcid"),
        pl.col("Plants").alias("Ctrl_Plants"),
        pl.col("values").alias("ctrl_values"),
        pl.col("mean_val").alias("ctrl_mean"),
    )

    df_treat = df_agg.filter(pl.col("Ni") != 0).select(
        pl.col("Week"),
        pl.col("FattyAcid"),
        pl.col("Ni"),
        pl.col("Plants").alias("Treat_Plants"),
        pl.col("values").alias("treat_values"),
        pl.col("mean_val").alias("treat_mean"),
    )

    df_joined = df_treat.join(df_ctrl, on=["Week", "FattyAcid"], how="left")
    df_joined.with_columns(
        [
            format_list("Treat_Plants"),
            format_list("treat_values"),
            format_list("Ctrl_Plants"),
            format_list("ctrl_values"),
        ]
    ).write_csv("Даша/df_joined.txt")

    if method == "epsilon":
        df_joined = df_joined.with_columns(
            Log2FC=(pl.col("treat_mean") / pl.col("ctrl_mean")).log(2)
        )
    else:
        df_joined = df_joined.with_columns(
            Log2FC=(pl.col("treat_mean") - pl.col("ctrl_mean")) / np.log(2)
        )

    # --- Б. СТАТИСТИКА ---
    treat_lists = df_joined["treat_values"].to_list()
    ctrl_lists = df_joined["ctrl_values"].to_list()
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

    # Сохраняем текущий результат в файл
    # df_joined.with_columns(
    #     [format_list("treat_values"), format_list("ctrl_values")]
    # ).write_csv("Даша/output.txt")

    # 1. Считаем во сколько раз изменилось значение (2 в степени модуля Log2FC)
    fold_change = (2 ** pl.col("Log2FC").abs()).round(1)

    df_joined = df_joined.with_columns(
        Significance=pl.format(
            "{}\n{}/{} ({})",
            pl.when(pl.col("q_value") < 0.001)
            .then(pl.lit("***"))
            .when(pl.col("q_value") < 0.01)
            .then(pl.lit("**"))
            .when(pl.col("q_value") < 0.05)
            .then(pl.lit("*"))
            .otherwise(pl.lit("")),
            pl.col("treat_mean").round(1),
            pl.col("ctrl_mean").round(1),
            pl.when(pl.col("Log2FC") > 0)
            .then(pl.format("⬈ {}", fold_change))
            .when(pl.col("Log2FC") < 0)
            .then(pl.format("⬊ {}", fold_change))
            .otherwise(pl.lit("без изменений")),
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

    for i, week in enumerate([1, 5]):
        df_w = df_plot[df_plot["Week"] == week]
        if df_w.empty:
            continue

        ordered_fa = df_w["FattyAcid"].drop_duplicates().tolist()
        pivot_log2fc = df_w.pivot(
            index="FattyAcid", columns="Ni", values="Log2FC"
        ).reindex(ordered_fa)
        pivot_sig = df_w.pivot(
            index="FattyAcid", columns="Ni", values="Significance"
        ).reindex(ordered_fa)

        sns.heatmap(
            pivot_log2fc,
            annot=pivot_sig,
            fmt="",
            cmap="vlag",
            center=0,
            vmin=-3,
            vmax=3,
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
combo_method.bind("<<ComboboxSelected>>", update_plot)
combo_col.bind("<<ComboboxSelected>>", update_plot)

# Первичная отрисовка при запуске
update_plot()

# Запуск оконного приложения
root.mainloop()

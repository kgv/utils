import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import re
import tkinter as tk

# Добавляем импорт NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# 1. Исходные данные
with open(
    "D/_{Type=SIMPER}{Organ=Leaf}{Value=PartsPerMillion_DryWeight}{Week=[5]}{Permutations=9999}{Transform=None}.txt",
    "r",
    encoding="utf-8",
) as file:
    raw_data = file.read()
    print(raw_data)

# 2. Парсинг данных (Polars)
blocks = raw_data.strip().split("## Comparison: ")
all_data = []

for block in blocks[1:]:
    lines = block.strip().split("\n")
    comp_name = lines[0].strip()

    cleaned_lines = []
    for line in lines[1:]:
        line = line.strip()
        if not line or re.match(r"^\|[:\-]+", line):
            continue
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cleaned_lines.append(line)

    table_str = "\n".join(cleaned_lines)

    df = pl.read_csv(io.StringIO(table_str), separator="|", null_values=[""])
    df.columns = [c.strip() for c in df.columns]
    df = df.rename({df.columns[0]: "Feature"})

    df = df.with_columns([pl.col(pl.String).str.strip_chars()])
    df = df.with_columns(pl.lit(comp_name).alias("Comparison"))
    all_data.append(df)

full_df = pl.concat(all_data)
full_df = full_df.with_columns(pl.col("significance").fill_null(""))
full_df = full_df.with_columns(
    [
        pl.col("average").cast(pl.Float64),
        pl.col("sd").cast(pl.Float64),
        pl.col("ratio").cast(pl.Float64),
        pl.col("ava").cast(pl.Float64),
        pl.col("avb").cast(pl.Float64),
        pl.col("cumsum_diff").cast(pl.Float64),
        pl.col("cumsum").cast(pl.Float64) * 100,
        pl.col("p").cast(pl.Float64),
    ]
)

# 3. Подготовка данных
df_control = full_df.filter(pl.col("Comparison").str.starts_with("0.5_"))
df_control = df_control.with_columns(
    pl.col("Comparison")
    .str.split("_")
    .list.get(1)
    .str.split(".")
    .list.get(0)
    .cast(pl.Int32)
    .alias("Ni")
)
df_control = df_control.with_columns(
    ava_percent=(pl.col("ava") / pl.col("ava").sum() * 100).over("Ni"),
    avb_percent=(pl.col("avb") / pl.col("avb").sum() * 100).over("Ni"),
)

# df_control = df_control.with_columns(
#     [
#         pl.col("average").rank(method="min", descending=True).over("Ni").alias("Rank"),
#         pl.col("cumsum")
#         .diff()
#         .over("Ni")
#         .fill_null(pl.col("cumsum"))
#         .alias("cumsum_diff"),
#     ]
# )

feature_importance = (
    df_control.group_by("Feature")
    .agg(pl.col("average").mean().alias("mean_avg"))
    .sort("mean_avg", descending=True)
)
all_features = feature_importance.get_column("Feature").to_list()

# Глобальная переменная для окна с графиками
plot_window = None


# 4. Функция отрисовки графиков во встроенном окне Tkinter
def draw_plots(selected_features, row_height):
    global plot_window

    if not selected_features:
        print("Нет выбранных кислот для отображения.")
        return

    # Создаем или очищаем окно для графиков
    if plot_window is None or not tk.Toplevel.winfo_exists(plot_window):
        plot_window = tk.Toplevel(root)
        plot_window.title("Графики SIMPER")
        plot_window.geometry("1400x800")
    else:
        # Очищаем старые виджеты, если окно уже открыто
        for widget in plot_window.winfo_children():
            widget.destroy()

    # --- Фрейм для панели инструментов (сверху, не прокручивается) ---
    toolbar_frame = tk.Frame(plot_window)
    toolbar_frame.pack(side=tk.TOP, fill=tk.X)

    # --- Фрейм для холста с прокруткой (занимает оставшееся место) ---
    main_frame = tk.Frame(plot_window)
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Настраиваем Canvas и Scrollbar для прокрутки
    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Привязка колесика мыши для прокрутки
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    plot_window.bind("<MouseWheel>", _on_mousewheel)
    plot_window.bind(
        "<Button-4>", lambda e: canvas.yview_scroll(-1, "units")
    )  # Для Linux
    plot_window.bind(
        "<Button-5>", lambda e: canvas.yview_scroll(1, "units")
    )  # Для Linux

    # Построение графиков Matplotlib
    n_features = len(selected_features)
    sns.set_theme(style="whitegrid")

    fig, axes = plt.subplots(
        nrows=n_features, ncols=4, figsize=(20, row_height * n_features)
    )
    axes = np.atleast_2d(axes)

    fig.suptitle(
        f"Профиль SIMPER: {n_features} выбранных жирных кислот",
        fontsize=22,
        weight="bold",
        y=0.99 if n_features > 1 else 1.05,
    )

    metric_titles = [
        "Концентрация (ava / avb)",
        "Собственный вклад (Average ± SD)",
        "Относительный вклад (%)",
        "p-value (Значимость)",
    ]

    for row_idx, feature in enumerate(selected_features):
        feat_df = df_control.filter(pl.col("Feature") == feature).sort("Ni").to_pandas()

        # --- 1. Концентрация (ava и avb) + avb_percent (вторая ось) ---
        ax0 = axes[row_idx, 0]
        line1 = ax0.plot(
            feat_df["Ni"],
            feat_df["ava"],
            color="#2b7bba",
            marker="o",
            markersize=8,
            linewidth=2,
            label="ava (Контроль)",
        )
        line2 = ax0.plot(
            feat_df["Ni"],
            feat_df["avb"],
            color="#f0ad4e",
            marker="s",
            markersize=8,
            linewidth=2,
            label="avb (Опыт)",
        )
        ax0.set_xticks([0, 50, 250, 500, 750, 1000])
        ax0.set_ylabel(f"{feature}\nКонцентрация", fontsize=12, weight="bold")

        ax0_twin = ax0.twinx()
        line3 = ax0_twin.plot(
            feat_df["Ni"],
            feat_df["avb_percent"],
            color="#8e44ad",
            marker="^",
            markersize=8,
            linewidth=2,
            linestyle="--",
            label="avb_percent (%)",
        )
        ax0_twin.set_ylabel(
            "avb_percent (%)", color="#8e44ad", fontsize=10, weight="bold"
        )
        ax0_twin.tick_params(axis="y", labelcolor="#8e44ad")
        ax0_twin.grid(False)

        if row_idx == 0:
            lines = line1 + line2 + line3
            labels = [l.get_label() for l in lines]
            ax0.legend(lines, labels, fontsize=10, loc="best")

        # --- 2. Собственный вклад (Average + SD) ---
        ax1 = axes[row_idx, 1]
        ax1.bar(
            feat_df["Ni"],
            feat_df["average"],
            yerr=feat_df["sd"],
            width=80,
            capsize=5,
            color="#d9534f",
            alpha=0.8,
            edgecolor="black",
        )
        ax1.set_xticks([0, 50, 250, 500, 750, 1000])
        ax1.set_ylabel("")

        # --- 3. Позиция (Ранг) ---
        ax2 = axes[row_idx, 2]
        ax2.plot(
            feat_df["Ni"],
            feat_df["cumsum_diff"],
            color="#5cb85c",
            marker="v",
            markersize=8,
            linewidth=2,
        )
        ax2.set_xticks([0, 50, 250, 500, 750, 1000])
        ax2.set_ylabel("")

        # --- 4. p-value ---
        ax3 = axes[row_idx, 3]
        ax3.plot(
            feat_df["Ni"],
            feat_df["p"],
            color="#9b59b6",
            marker="D",
            markersize=8,
            linewidth=2,
        )
        ax3.axhline(0.05, ls="--", color="red", alpha=0.7)

        for _, row in feat_df.iterrows():
            if row["significance"] and str(row["significance"]).strip() not in [
                "",
                ".",
            ]:
                ax3.text(
                    row["Ni"],
                    row["p"] + 0.02,
                    row["significance"],
                    color="red",
                    fontsize=14,
                    ha="center",
                    va="bottom",
                    weight="bold",
                )

        ax3.set_xticks([0, 50, 250, 500, 750, 1000])
        ax3.set_ylabel("")

        if row_idx == 0:
            for col_idx in range(4):
                axes[row_idx, col_idx].set_title(
                    metric_titles[col_idx], fontsize=14, weight="bold", pad=15
                )

        for col_idx in range(4):
            if row_idx == n_features - 1:
                axes[row_idx, col_idx].set_xlabel("Доза Ni", fontsize=12, weight="bold")
            else:
                axes[row_idx, col_idx].set_xlabel("")

    plt.tight_layout(rect=[0, 0, 1, 0.98])

    # Встраиваем график в Tkinter
    canvas_tk = FigureCanvasTkAgg(fig, master=scrollable_frame)
    canvas_tk.draw()
    canvas_tk.get_tk_widget().pack(fill="both", expand=True)

    # --- ДОБАВЛЯЕМ ПАНЕЛЬ ИНСТРУМЕНТОВ (С КНОПКОЙ СОХРАНЕНИЯ) ---
    toolbar = NavigationToolbar2Tk(canvas_tk, toolbar_frame)
    toolbar.update()

    # Закрываем фигуру в pyplot, чтобы не утекала память
    plt.close(fig)


# 5. Создание окна настроек (GUI)
def on_redraw_click():
    selected_indices = listbox.curselection()
    selected_features = [listbox.get(i) for i in selected_indices]

    try:
        row_height = float(row_height_var.get())
    except ValueError:
        row_height = 3.5

    draw_plots(selected_features, row_height)


root = tk.Tk()
root.title("Настройки отображения ЖК")
root.geometry("380x500")

lbl = tk.Label(
    root,
    text="Выберите ЖК для отображения\n(Зажмите Ctrl для выбора нескольких):",
    font=("Arial", 10, "bold"),
)
lbl.pack(pady=10)

frame_list = tk.Frame(root)
frame_list.pack(pady=5, fill=tk.BOTH, expand=True, padx=20)

scrollbar_list = tk.Scrollbar(frame_list)
scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    frame_list,
    selectmode=tk.EXTENDED,
    yscrollcommand=scrollbar_list.set,
    font=("Arial", 11),
)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar_list.config(command=listbox.yview)

for feature in all_features:
    listbox.insert(tk.END, feature)

listbox.select_set(0, tk.END)

frame_settings = tk.Frame(root)
frame_settings.pack(pady=10, fill=tk.X, padx=20)

tk.Label(frame_settings, text="Высота строки графиков:", font=("Arial", 10)).pack(
    side=tk.LEFT
)
row_height_var = tk.StringVar(value="3.5")
spinbox_height = tk.Spinbox(
    frame_settings,
    from_=1.0,
    to=10.0,
    increment=0.5,
    textvariable=row_height_var,
    width=5,
    font=("Arial", 10),
)
spinbox_height.pack(side=tk.RIGHT)

btn_redraw = tk.Button(
    root,
    text="Перерисовать графики",
    command=on_redraw_click,
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
)
btn_redraw.pack(pady=15, fill=tk.X, padx=20)

on_redraw_click()

root.mainloop()

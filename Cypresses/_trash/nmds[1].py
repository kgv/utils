from scipy.spatial import ConvexHull
from scipy.spatial.distance import pdist, squareform
from skbio.stats.distance import DistanceMatrix, anosim, permanova
from sklearn.manifold import MDS
from tkinter import ttk
import matplotlib
import matplotlib.pyplot as plt
import mplcursors
import numpy as np
import polars as pl
import tkinter as tk

# ==========================================
# 1. ЧТЕНИЕ И ПОДГОТОВКА ДАННЫХ
# ==========================================

df = pl.read_csv(
    "Cypresses/_Wide.txt",
    schema_overrides={
        "Genus": pl.String,
        "Species": pl.String,
        "Variety": pl.String,
        "Identifier": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.String,
    },
).with_columns(
    [
        pl.concat_str(
            [pl.col("Genus"), pl.col("Species")], separator=" ", ignore_nulls=True
        ).alias("Species"),
        pl.concat_str(
            [pl.col("Genus"), pl.col("Species"), pl.col("Variety")],
            separator=" ",
            ignore_nulls=True,
        ).alias("Variety"),
    ]
)

clean_df = df.select(
    pl.all()
    .exclude(["Genus", "Species", "Variety", "Identifier", "Tree", "Vial"])
    .fill_null(0.0)
)

# Создаем подписи для каждой точки
hover_labels = np.array(
    [
        f"{row['Variety']} {row['Identifier']} (Tree: {row['Tree']}, Vial: {row['Vial']})"
        for row in df.to_dicts()
    ]
)

X_raw = clean_df.to_numpy()
print("Данные успешно загружены!")


# ==========================================
# 2. ФУНКЦИЯ АНАЛИЗА
# ==========================================
def run_analysis():
    # Получаем значения из Combobox
    transform_method = combo_transform_method.get()
    distance_metric = combo_distance_metric.get()
    taxonomy = combo_taxonomy.get()
    n_init = int(combo_n_init.get())
    max_iter = int(combo_max_iter.get())
    seed = int(combo_seed.get())

    print(
        f"\nЗапуск: Таксонимия = {taxonomy}, Трансформация = {transform_method}, Расстояние = {distance_metric}"
    )

    # 1. Трансформация
    if transform_method == "log1p":
        X = np.log1p(X_raw)
    else:
        X = X_raw
    # Получаем y динамически на основе выбранного ключа
    y = df[taxonomy].to_numpy()

    # 2. Расчет матрицы расстояний
    try:
        dist_array = pdist(X, metric=distance_metric)
        dist_matrix = squareform(dist_array)
    except Exception as e:
        print(f"Ошибка при расчете дистанции: {e}")
        return

    # Преобразуем в формат scikit-bio
    dm = DistanceMatrix(dist_matrix)
    grouping = list(y)

    # 3. Статистические тесты
    print("--- Результаты ANOSIM ---")
    anosim_res = anosim(dm, grouping, permutations=999)
    print(anosim_res[["test statistic", "p-value"]])

    print("\n--- Результаты PERMANOVA ---")
    permanova_res = permanova(dm, grouping, permutations=999)
    print(permanova_res[["test statistic", "p-value"]])

    # 4. Ординация NMDS
    print("\n--- Выполнение NMDS ординации ---")
    nmds = MDS(
        n_components=2,
        metric="precomputed",
        metric_mds=False,
        init="random",
        normalized_stress="auto",
        n_init=n_init,
        max_iter=max_iter,
        eps=1e-9,
        random_state=seed,
    )
    nmds_coords = nmds.fit_transform(dist_matrix)
    print(f"final_stress: {nmds.stress_}")

    # 5. Визуализация
    fig, ax = plt.subplots(figsize=(10, 8))
    unique_species = np.unique(y)
    colors = matplotlib.colormaps.get_cmap("tab20")

    # Список для хранения объектов scatter и их подписей
    scatters = []

    for i, species in enumerate(unique_species):
        idx = np.where(y == species)[0]
        pts = nmds_coords[idx]
        lbls = hover_labels[idx]

        # Рисуем точки
        sc = ax.scatter(pts[:, 0], pts[:, 1], label=species, color=colors(i), s=50)
        scatters.append((sc, lbls))

        # Отрисовка ConvexHull
        if len(pts) > 2:
            hull = ConvexHull(pts)
            for simplex in hull.simplices:
                ax.plot(
                    pts[simplex, 0], pts[simplex, 1], color=colors(i), lw=2, alpha=0.6
                )
            ax.fill(
                pts[hull.vertices, 0], pts[hull.vertices, 1], color=colors(i), alpha=0.1
            )
        elif len(pts) == 2:
            ax.plot(pts[:, 0], pts[:, 1], color=colors(i), lw=2, alpha=0.6)

    ax.set_title(
        f"NMDS Ordination\nTaxonomy: {taxonomy}; Distance: {distance_metric}; Transform: {transform_method}; Stress: {nmds.stress_:.2f}"
    )
    ax.set_xlabel("NMDS1")
    ax.set_ylabel("NMDS2")
    ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()

    # Всплывающие подсказки
    # Создаем объект аннотации (скрытый по умолчанию)
    annot = ax.annotate(
        "",
        xy=(0, 0),
        xytext=(10, 10),
        textcoords="offset points",
        bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.9, ec="gray"),
        arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        zorder=100,
    )
    annot.set_visible(False)

    def hover(event):
        # Проверяем, что мышь находится в пределах осей графика
        if event.inaxes == ax:
            for sc, lbls in scatters:
                # Проверяем, попала ли мышь на какую-либо точку этого вида
                cont, ind = sc.contains(event)
                if cont:
                    # Получаем индекс точки
                    point_idx = ind["ind"][0]
                    pos = sc.get_offsets()[point_idx]

                    # Обновляем координаты и текст подсказки
                    annot.xy = pos
                    annot.set_text(lbls[point_idx])
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                    return  # Выходим из функции, так как нашли точку

            # Если цикл завершился, значит мышь не на точке -> скрываем подсказку
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()
        else:
            # Если мышь ушла за пределы графика -> скрываем подсказку
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()

    # Привязываем функцию hover к событию движения мыши
    fig.canvas.mpl_connect("motion_notify_event", hover)

    plt.show()


# ==========================================
# 3. СОЗДАНИЕ ГРАФИЧЕСКОГО ИНТЕРФЕЙСА (Tkinter)
# ==========================================
root = tk.Tk()
root.title("NMDS Settings")
root.geometry("512x400")

frame_controls = tk.Frame(root, padx=20, pady=20)
frame_controls.pack(fill=tk.BOTH, expand=True)

# --- Выпадающий список для метода трансформации ---
frame_transform = tk.Frame(frame_controls)
frame_transform.pack(fill=tk.X, pady=5)

tk.Label(
    frame_transform,
    text="transform:",
    font=("Arial", 12),
    width=20,
    anchor="w",
).pack(side=tk.LEFT)
combo_transform_method = ttk.Combobox(
    frame_transform,
    values=["None", "log1p"],
    state="readonly",
    font=("Arial", 12),
)
combo_transform_method.current(1)  # По умолчанию выбран "log1p"
combo_transform_method.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

# --- Выпадающий список для метрики расстояния ---
frame_distance = tk.Frame(frame_controls)
frame_distance.pack(fill=tk.X, pady=5)

tk.Label(
    frame_distance, text="distance:", font=("Arial", 12), width=20, anchor="w"
).pack(side=tk.LEFT)
combo_distance_metric = ttk.Combobox(
    frame_distance,
    values=[
        "braycurtis",
        "canberra",
        "chebyshev",
        "cityblock",
        "correlation",
        "cosine",
        "euclidean",
        "jensenshannon",
        "mahalanobis",
        "minkowski",
        "seuclidean",
        "sqeuclidean",
    ],
    state="readonly",
    font=("Arial", 12),
)
combo_distance_metric.current(0)  # По умолчанию выбран "braycurtis"
combo_distance_metric.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

# --- Выпадающий список для taxonomy ---
frame_taxonomy = tk.Frame(frame_controls)
frame_taxonomy.pack(fill=tk.X, pady=5)
tk.Label(
    frame_taxonomy, text="taxonomy:", font=("Arial", 12), width=20, anchor="w"
).pack(side=tk.LEFT)
combo_taxonomy = ttk.Combobox(
    frame_taxonomy,
    values=["Genus", "Species", "Variety"],
    state="readonly",
    font=("Arial", 12),
)
combo_taxonomy.current(1)
combo_taxonomy.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

# --- Выпадающий список для n_init ---
frame_n_init = tk.Frame(frame_controls)
frame_n_init.pack(fill=tk.X, pady=5)
tk.Label(frame_n_init, text="n_init:", font=("Arial", 12), width=20, anchor="w").pack(
    side=tk.LEFT
)
combo_n_init = ttk.Combobox(
    frame_n_init,
    values=["10", "100", "1000"],
    state="readonly",
    font=("Arial", 12),
)
combo_n_init.current(1)
combo_n_init.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

# --- Выпадающий список для max_iter ---
frame_max_iter = tk.Frame(frame_controls)
frame_max_iter.pack(fill=tk.X, pady=5)
tk.Label(
    frame_max_iter, text="max_iter:", font=("Arial", 12), width=20, anchor="w"
).pack(side=tk.LEFT)
combo_max_iter = ttk.Combobox(
    frame_max_iter,
    values=["10", "100", "1000"],
    state="readonly",
    font=("Arial", 12),
)
combo_max_iter.current(1)
combo_max_iter.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

# --- Выпадающий список для seed ---
frame_seed = tk.Frame(frame_controls)
frame_seed.pack(fill=tk.X, pady=5)
tk.Label(frame_seed, text="seed:", font=("Arial", 12), width=20, anchor="w").pack(
    side=tk.LEFT
)
combo_seed = ttk.Combobox(
    frame_seed,
    values=["42", "1234"],
    state="normal",
    font=("Arial", 12),
)
combo_seed.current(0)
combo_seed.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

# --- Кнопка запуска ---
btn_run = tk.Button(
    frame_controls,
    text="Запустить анализ и построить график",
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
    command=run_analysis,
)
btn_run.pack(pady=20, fill=tk.X)

# Запуск главного цикла приложения
root.mainloop()

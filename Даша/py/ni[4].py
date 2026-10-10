import polars as pl
import numpy as np
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.widgets import RadioButtons

# ==========================================
# 1. ЧТЕНИЕ ДАННЫХ (выполняется один раз)
# ==========================================
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
# Убедитесь, что в файле есть и колонка 'ppm', и колонка 'pct'.

epsilon_val = np.finfo(float).eps


def format_list(name):
    return pl.format(
        "[{}]", pl.col(name).cast(pl.List(pl.String)).list.join(",")
    ).alias(name)


# ==========================================
# 2. НАСТРОЙКА ОСНОВНОГО ОКНА (ГРАФИК)
# ==========================================
fig_main, axes = plt.subplots(1, 2, figsize=(12, 10), sharey=True)
fig_main.canvas.manager.set_window_title("График: Профиль жирных кислот")

# Оставляем место справа для цветовой шкалы
plt.subplots_adjust(bottom=0.1, right=0.9)
cbar_ax = fig_main.add_axes([0.92, 0.15, 0.02, 0.7])

# ==========================================
# 3. НАСТРОЙКА ВТОРОГО ОКНА (ПАНЕЛЬ УПРАВЛЕНИЯ)
# ==========================================
# Создаем маленькое всплывающее окно для настроек
fig_ctrl = plt.figure(figsize=(4, 3))
fig_ctrl.canvas.manager.set_window_title("Настройки")

# Размещаем оси для кнопок в новом окне
ax_radio_method = fig_ctrl.add_axes([0.1, 0.55, 0.8, 0.35])
ax_radio_method.set_title("Метод расчета", fontsize=10)
radio_method = RadioButtons(ax_radio_method, ("log1p", "epsilon"))

ax_radio_col = fig_ctrl.add_axes([0.1, 0.05, 0.8, 0.35])
ax_radio_col.set_title("Колонка данных", fontsize=10)
radio_col = RadioButtons(ax_radio_col, ("ppm", "pct"))

# ==========================================
# 4. ФУНКЦИЯ ПЕРЕСЧЕТА И ПЕРЕРИСОВКИ
# ==========================================
def update_plot(val=None):
    df_calc = (
        df.filter(pl.col("FattyAcid") != "17:0")
        .filter(pl.col("Plant") != 37)
        .with_columns(
            # Считаем долю в процентах
            pct=(pl.col("ppm") / pl.col("ppm").sum() * 100).over("Plant")
        )
    )

    # Считываем текущие значения с кнопок
    method = radio_method.value_selected
    target_col = radio_col.value_selected

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
        values=pl.col("processed_val"),
        mean_val=pl.col("processed_val").mean(),
    )

    df_ctrl = df_agg.filter(pl.col("Ni") == 0).select(
        pl.col("Week"),
        pl.col("FattyAcid"),
        pl.col("values").alias("ctrl_values"),
        pl.col("mean_val").alias("ctrl_mean"),
    )

    df_treat = df_agg.filter(pl.col("Ni") != 0).select(
        pl.col("Week"),
        pl.col("FattyAcid"),
        pl.col("Ni"),
        pl.col("values").alias("treat_values"),
        pl.col("mean_val").alias("treat_mean"),
    )

    df_joined = df_treat.join(df_ctrl, on=["Week", "FattyAcid"], how="left")

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
    df_joined.with_columns(
        [format_list("treat_values"), format_list("ctrl_values")]
    ).write_csv("Даша/output.txt")

    df_joined = df_joined.with_columns(
        Significance=pl.format(
            "{}\n{}/{}\n{}()",
            pl.when(pl.col("q_value") < 0.001)
            .then(pl.lit("***"))
            .when(pl.col("q_value") < 0.01)
            .then(pl.lit("**"))
            .when(pl.col("q_value") < 0.05)
            .then(pl.lit("*"))
            .otherwise(pl.lit("")),
            pl.col("treat_mean").round(1),
            pl.col("ctrl_mean").round(1),
            pl.col("Log2FC").round(2),
        )
    )

    # --- В. ОТРИСОВКА ---
    df_plot = df_joined.select(
        ["Week", "FattyAcid", "Ni", "Log2FC", "Significance"]
    ).to_pandas()

    # Очищаем графики перед новой отрисовкой
    axes[0].clear()
    axes[1].clear()
    cbar_ax.clear()

    fig_main.suptitle(
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

    # Обновляем основное окно
    fig_main.canvas.draw_idle()


# ==========================================
# 5. ЗАПУСК
# ==========================================
# Привязываем функцию к кликам по кнопкам
radio_method.on_clicked(update_plot)
radio_col.on_clicked(update_plot)

# Вызываем один раз вручную, чтобы нарисовать график при запуске
update_plot()

# Показываем оба окна
plt.show()

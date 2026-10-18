import polars as pl
import polars.selectors as cs
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

COMPONENTS = [
    "Monoterpene",
    "Sesquiterpene",
    "Terpene",
]

VALUES = [
    "Percent_Mean",
    "PartsPerMillion_Mean",
]

GROUPS = [
    "Genus",
    "Species",
    "Variety",
]

PERMUTATIONS = [
    9999,
]

TRANSFORMATIONS = [
    # "[log1p]",
    # "[log2]",
    "[]",
]


def read_csv(component, value, group, permutations, transformations):
    input_file = f"Cypresses/csv/_{{Type=SIMPER}}{{Component={component}}}{{Value={value}}}{{Group={group}}}{{Permutations={permutations}}}{{Transformations={transformations}}}.txt"
    return pl.read_csv(input_file, glob=False, null_values="NA")


def write_markdown(df, name, round_decimals=None):
    # Окгругляем числа с плавающей точкой
    if round_decimals is not None:
        df = df.with_columns(cs.float().round(round_decimals))

    # Формируем Markdown-текст
    with pl.Config(
        tbl_formatting="MARKDOWN",
        tbl_hide_column_data_types=True,
        tbl_hide_dataframe_shape=True,
        tbl_rows=-1,
        tbl_cols=-1,
        fmt_str_lengths=1_000_000,
        tbl_width_chars=65535,
    ):
        markdown_text = str(df)

    # Записываем полученную строку в файл
    with open(name, "w", encoding="utf-8") as f:
        f.write(markdown_text)


def select_and_rename_fields(df):
    return df.select(
        Left=pl.col("id").str.split("_").list[0],
        Right=pl.col("id").str.split("_").list[1],
        Component=pl.nth(0).str.split("...").list[0],
        AverageAbundances_Left=pl.col("ava"),
        AverageAbundances_Right=pl.col("avb"),
        Rank=pl.col("average").rank(method="min", descending=True).over("id"),
        AverageDissimilarity=pl.col("average"),
        StandardDeviation=pl.col("sd"),
        Ratio=pl.col("ratio"),
        Contribution=pl.col("cumsum").diff().over("id").fill_null(pl.col("cumsum"))
        * 100,
        CumulativeContribution=pl.col("cumsum") * 100,
        p=pl.col("p"),
        Significance=pl.when(pl.col("p") < 0.001)
        .then(pl.lit("***"))
        .when(pl.col("p") <= 0.01)
        .then(pl.lit("**"))
        .when(pl.col("p") <= 0.05)
        .then(pl.lit("*"))
        .when(pl.col("p") <= 0.1)
        .then(pl.lit("."))
        .when(pl.col("p") <= 1.0)
        .then(pl.lit(""))
        .otherwise(None),  # Для значений > 1 или null
    )


def diverging_bar_chart(df):
    # Выбираем одну пару для детального анализа
    pair_df = df.filter(
        pl.col("Comparison") == "Thuja plicata vs Juniperus rigida"
    ).to_pandas()

    # Сортируем по вкладу
    pair_df = pair_df.sort_values("Contribution", ascending=True)

    plt.figure(figsize=(10, 8))
    # Цветовая палитра: синий для Left, красный для Right
    colors = [
        "#1f77b4" if x < 0 else "#d62728" for x in pair_df["Directional_Contribution"]
    ]

    bars = plt.barh(
        pair_df["FattyAcid"], pair_df["Directional_Contribution"], color=colors
    )

    # Настройка осей
    plt.axvline(0, color="black", linewidth=1)
    plt.xlabel("Вклад в различие (Contribution, %)")
    plt.title(
        "Топ компоненты, определяющие разницу:\nThuja plicata (Синий) vs Juniperus rigida (Красный)"
    )

    # Добавляем звездочки значимости прямо на график
    for bar, sig in zip(bars, pair_df["Significance"]):
        xval = bar.get_width()
        # Позиционируем текст чуть дальше конца бара
        offset = 1 if xval > 0 else -1
        plt.text(
            xval + offset,
            bar.get_y() + bar.get_height() / 2,
            sig,
            va="center",
            ha="left" if xval > 0 else "right",
            fontsize=12,
        )

    plt.tight_layout()
    plt.show()


def bubble_plot(df):
    # Считаем Log2 Fold Change для цвета (добавляем псевдокаунт, чтобы избежать log(0))
    df_bubble = df.with_columns(
        np.log2(
            (pl.col("AverageAbundances_Right") + 1)
            / (pl.col("AverageAbundances_Left") + 1)
        ).alias("Log2FC")
    ).to_pandas()

    plt.figure(figsize=(12, 10))
    sns.scatterplot(
        data=df_bubble,
        x="Comparison",
        y="FattyAcid",
        size="Contribution",
        hue="Log2FC",
        palette="vlag",  # Красно-синяя палитра
        sizes=(50, 800),  # Разброс размеров пузырьков
        edgecolor="black",
        alpha=0.8,
    )

    plt.xticks(rotation=45, ha="right")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.title("Вклад компонентов в попарные различия видов")
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.show()


def dual_axis_plot(df):
    pair_df = df.filter(
        pl.col("Comparison") == "Thuja plicata vs Microbiota decussata"
    ).to_pandas()
    pair_df = pair_df.sort_values("Rank")

    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Ширина баров
    x = np.arange(len(pair_df["FattyAcid"]))
    width = 0.35

    # Бары с реальными концентрациями (лучше логарифмировать, если разброс большой)
    ax1.bar(
        x - width / 2,
        np.log1p(pair_df["AverageAbundances_Left"]),
        width,
        label="Thuja plicata",
        color="skyblue",
    )
    ax1.bar(
        x + width / 2,
        np.log1p(pair_df["AverageAbundances_Right"]),
        width,
        label="Microbiota decussata",
        color="salmon",
    )

    ax1.set_ylabel("Log(Abundance + 1)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(pair_df["FattyAcid"], rotation=45, ha="right")
    ax1.legend(loc="upper left")

    # Вторая ось для кумулятивного вклада
    ax2 = ax1.twinx()
    ax2.plot(
        x,
        pair_df["CumulativeContribution"],
        color="black",
        marker="o",
        linestyle="-",
        linewidth=2,
        label="Cumulative Contribution %",
    )
    ax2.set_ylabel("Cumulative Contribution (%)")
    ax2.set_ylim(0, 105)
    ax2.legend(loc="upper right")

    plt.title("Сравнение обилий и кумулятивный вклад (SIMPER)")
    plt.tight_layout()
    plt.show()


for component in COMPONENTS:
    for value in VALUES:
        for group in GROUPS:
            for permutations in PERMUTATIONS:
                for transformations in TRANSFORMATIONS:
                    base_name = (
                        f"_{{Type=SIMPER}}"
                        f"{{Component={component}}}"
                        f"{{Value={value}}}"
                        f"{{Group={group}}}"
                        f"{{Permutations={permutations}}}"
                        f"{{Transformations={transformations}}}"
                    )
                    input_file = f"Cypresses/csv/{base_name}.txt"
                    output_file = f"Cypresses/md/{base_name}.md"

                    read_df = pl.read_csv(input_file, glob=False, null_values="NA")

                    select_df = select_and_rename_fields(read_df)

                    filter_df = select_df.filter(
                        (pl.col("Contribution") > 10)
                        # | ((pl.col("Contribution") > 1) & (pl.col("p") < 0.05))
                    )
                    # df_plot = filter_df.filter(
                    #     (pl.col("Rank") <= 10)
                    #     # & (pl.col("p") < 0.05)
                    # )
                    # filter_df.with_columns(
                    #     [
                    #         # Определяем, у кого вещества больше
                    #         (
                    #             pl.col("AverageAbundances_Right")
                    #             - pl.col("AverageAbundances_Left")
                    #         ).alias("Abundance_Diff"),
                    #         # Направленный вклад: если больше справа, то +, если слева, то -
                    #         pl.when(
                    #             pl.col("AverageAbundances_Right")
                    #             > pl.col("AverageAbundances_Left")
                    #         )
                    #         .then(pl.col("Contribution"))
                    #         .otherwise(-pl.col("Contribution"))
                    #         .alias("Directional_Contribution"),
                    #         # Создаем колонку с названием пары для удобства
                    #         (pl.col("Left") + " vs " + pl.col("Right")).alias(
                    #             "Comparison"
                    #         ),
                    #     ]
                    # )
                    # diverging_bar_chart(df_plot)
                    # bubble_plot(df_plot)
                    # dual_axis_plot(df_plot)

                    write_markdown(
                        filter_df,
                        round_decimals=4,
                        name=output_file,
                    )

import polars as pl
import polars.selectors as cs

ORGANS = [
    "Leaf",
    # "Root",
]

VALUES = [
    # "Percent_Area",
    "PartsPerMillion_DryWeight",
]

WEEKS = [
    "[1,5]",
    # "[1]",
    # "[5]",
]


def read_csv(organ, value, weeks):
    input_file = f"D/csv/_{{Type=SIMPER}}{{Organ={organ}}}{{Value={value}}}{{Weeks={weeks}}}{{Permutations=9999}}{{Transformations=[]}}.txt"
    return pl.read_csv(input_file, glob=False)


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
    ):
        markdown_text = str(df)

    # Записываем полученную строку в файл
    with open(name, "w", encoding="utf-8") as f:
        f.write(markdown_text)


def select_and_rename_fields(df):
    return df.select(
        Ni_Left=pl.col("groups").str.split("_").list[0].str.split(".").list[0],
        Week_Left=pl.col("groups").str.split("_").list[0].str.split(".").list[1],
        Ni_Right=pl.col("groups").str.split("_").list[1].str.split(".").list[0],
        Week_Right=pl.col("groups").str.split("_").list[1].str.split(".").list[1],
        FattyAcid=pl.nth(0).str.split("...").list[0],
        AverageAbundances_Left=pl.col("ava"),
        AverageAbundances_Right=pl.col("avb"),
        Rank=pl.col("average").rank(method="min", descending=True).over("groups"),
        AverageDissimilarity=pl.col("average"),
        StandardDeviation=pl.col("sd"),
        Ratio=pl.col("ratio"),
        Contribution=pl.col("cumsum").diff().over("groups").fill_null(pl.col("cumsum"))
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


for organ in ORGANS:
    for value in VALUES:
        for weeks in WEEKS:
            read_df = read_csv(organ, value, weeks)
            select_df = select_and_rename_fields(read_df)
            write_markdown(select_df, round_decimals=4, name="D/md/_markdown_table.md")

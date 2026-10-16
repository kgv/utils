import polars as pl
import polars.selectors as cs

# "Ni",
# "Week",
# "Plant",
# "Sample",
# "WaterFraction",
# "FreshWeight",
# "FattyAcid",
# "Standard": pl.Float64,
# "Area": pl.Float64,
# "Percent_Area": pl.Float64,
# "PartsPerThousand_DryWeight": pl.Float64,
# "PartsPerMillion_DryWeight": pl.Float64,
# "Sum_Percent_Area": pl.Float64,
# "Sum_PartsPerThousand_DryWeight": pl.Float64,
# "Sum_PartsPerMillion_DryWeight": pl.Float64,

KIND = [
    "Leaf",
    "Root",
]

# Столбец, откуда берем сами цифры
VALUE = [
    "Percent_Area",
    "PartsPerMillion_DryWeight",
]

WEEK = [
    None,
    1,
    5,
]

LEAF_MAJORS = [
    "16:0",
    "7,10,13-16:3",
    "18:0",
    "9-18:1",
    "11-18:1",
    "9,12-18:2",
    "9,12,15-18:3",
]

ROOT_MAJORS = [
    "16:0",
    "9-16:1",
    "18:0",
    "11-Me-12-18:1",
    "9-18:1",
    "11-18:1",
    "9,12-18:2",
    "9,12,15-18:3",
]

OVER = ["Ni", "Week", "Sample", "Plant"]


for kind in KIND:
    for value in VALUE:
        input_file = f"D/csv/_{{Kind={kind}}}{{Fields=Ni,Week,Sample,Plant,FattyAcid,PartsPerX}}.txt"
        read_df = pl.read_csv(input_file)
        print(f"read: {read_df}")

        # Фильтруем, оставляя только биохимически обоснованные ЖК
        filter_df = read_df.filter(
            (pl.col("FattyAcid") != "17:0") & (pl.col("FattyAcid") != "15:0")
        )
        print(f"filter_df: {filter_df}")

        majors = LEAF_MAJORS if kind == "Leaf" else ROOT_MAJORS
        unique_fa = filter_df["FattyAcid"].unique().to_list()
        # Оставляем только те, которых нет в списке majors
        minors = [fa for fa in unique_fa if fa not in majors]
        # Формируем динамическое название. Сортируем для красоты.
        if minors:
            minors_name = f"Minors[{';'.join(sorted(minors))}]"
        else:
            minors_name = "Minors"  # На случай, если миноров вообще нет

        # Группируем минорные кислоты в "Minors[]"
        group_df = (
            filter_df.with_columns(
                pl.when(pl.col("FattyAcid").is_in(majors))
                .then(pl.col("FattyAcid"))
                .otherwise(pl.lit(minors_name))
                .alias("FattyAcid")
            )
            .group_by(OVER + ["FattyAcid"], maintain_order=True)
            .agg(pl.col(value).sum())
        )
        print(f"group_df: {group_df}")

        # Превращаем в широкий формат
        pivot_df = group_df.pivot(
            index=["Ni", "Week", "Sample"],
            on="FattyAcid",  # Столбец, значения которого станут новыми заголовками
            values=value,
        )

        if minors_name in pivot_df.columns:
            pivot_df = pivot_df.select(
                pl.all().exclude(minors_name), pl.col(minors_name)
            )

        for week in WEEK:
            week_df = pivot_df
            if week is not None:
                week_df = week_df.filter(pl.col("Week") == week)

            week_suffix = f"{{Week={week}}}" if week is not None else ""

            output_file = (
                f"D/csv/_{{Type=Wide}}{{Kind={kind}}}{{Value={value}}}{week_suffix}.txt"
            )
            week_df.write_csv(output_file)

        # df = df.filter(pl.col("Week") == 5)
        # df = df.with_columns(
        #     pl.when(pl.col("Ni") == 0)
        #     .then(pl.lit("Control"))
        #     .otherwise(pl.lit("Experiment"))
        #     .alias("Ni")
        # )

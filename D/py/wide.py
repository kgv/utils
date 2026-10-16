import polars as pl

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

for kind in KIND:
    for value in VALUE:
        input_file = f"D/csv/_{{Kind={kind}}}{{Fields=Ni,Week,Sample,Plant,FattyAcid,PartsPerX}}.txt"
        read_df = pl.read_csv(input_file)
        print(f"read: {read_df}")

        # Фильтруем, оставляя только биохимически обоснованные ЖК
        filter_df = read_df.filter(
            (pl.col("FattyAcid") != "17:0") & (pl.col("FattyAcid") != "15:0")
        )

        # Превращаем в широкий формат
        pivot_df = filter_df.pivot(
            index=["Ni", "Week", "Sample"],
            on="FattyAcid",  # Столбец, значения которого станут новыми заголовками
            values=value,
        )

        for week in WEEK:
            week_df = pivot_df
            if week is not None:
                week_df = week_df.filter(pl.col("Week") == week)

            week_suffix = f"{{Week={week}}}" if week is not None else ""

            output_file = f"D/csv/_{{Type=Wide}}{{Kind={kind}}}{{Value={value}}}{week_suffix}.txt"
            week_df.write_csv(output_file)

        # df = df.filter(pl.col("Week") == 5)
        # df = df.with_columns(
        #     pl.when(pl.col("Ni") == 0)
        #     .then(pl.lit("Control"))
        #     .otherwise(pl.lit("Experiment"))
        #     .alias("Ni")
        # )

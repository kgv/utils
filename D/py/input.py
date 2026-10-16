import polars as pl

ORGANS = [
    "Leaf",
    "Root",
]

for organ in ORGANS:
    read_dfs = [
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=0mM}}{{Week=1}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=0mM}}{{Week=5}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=50mM}}{{Week=1}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=50mM}}{{Week=5}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=250mM}}{{Week=1}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=250mM}}{{Week=5}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=500mM}}{{Week=1}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=500mM}}{{Week=5}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=750mM}}{{Week=1}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=750mM}}{{Week=5}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=1000mM}}{{Week=1}}.txt"),
        pl.read_csv(f"D/csv/{{Kind={organ}}}{{Ni=1000mM}}{{Week=5}}.txt"),
    ]

    unpivot_dfs = [
        read_df.unpivot(
            index=["FattyAcid", "Standard", "Ni", "Week"],
            variable_name="Sample",
            value_name="Area",
        )
        .with_columns(
            pl.col("Sample").cast(pl.Int64),
        )
        .select(
            [
                "Ni",
                "Week",
                "Sample",
                "FattyAcid",
                "Standard",
                "Area",
            ]
        )
        for read_df in read_dfs
    ]

    unpivot_df = pl.concat(unpivot_dfs)
    print(f"unpivot: {unpivot_df}")

    # unpivot_df.write_csv(
    #     "D/csv/_{{Kind={kind}}}{{Fields=Ni,Week,Sample,FattyAcid,Standard,Area}}.txt"
    # )

    # join #####################################################################

    sample_df = pl.read_csv(
        f"D/csv/{{Kind={organ}}}{{Fields=Ni,Week,Sample,Plant,WaterFraction,FreshWeight}}.txt"
    )
    print(f"sample_df: {sample_df}")

    join_df = unpivot_df.join(
        sample_df,
        on=["Ni", "Week", "Sample"],
        how="full",
        coalesce=True,
        maintain_order="left_right",
    ).select(
        [
            "Ni",
            "Week",
            "Sample",
            "Plant",
            "WaterFraction",
            "FreshWeight",
            "FattyAcid",
            "Standard",
            "Area",
        ]
    )
    print(f"join_df: {join_df}")

    # join_df.write_csv(
    #     f"D/csv/_{{Kind={kind}}}{{Fields=Ni,Week,Sample,Plant,WaterFraction,FreshWeight,FattyAcid,Standard,Area}}.txt"
    # )

    # ppx ######################################################################
    # PartsPerHundred PartsPerThousand PartsPerMillion
    # https://en.wikipedia.org/wiki/Parts-per_notation

    over = ["Ni", "Week", "Sample", "Plant"]

    calculate_df = (
        join_df.with_columns(
            (pl.col("FreshWeight") * (1 - pl.col("WaterFraction"))).alias("DryWeight_g")
        )
        .with_columns(
            # Находим площадь (Area) внутреннего стандарта для каждого Plant
            pl.col("Area")
            .filter(pl.col("Standard").is_not_null())
            .first()
            .over(over)
            .alias("_IS_Area"),
            # Находим значение концентрации (Standard) для каждого Plant
            pl.col("Standard").drop_nulls().first().over(over).alias("_IS_Weight_mg"),
        )
        .with_columns(
            # Считаем абсолютную массу кислоты в мг
            ((pl.col("Area") / pl.col("_IS_Area")) * pl.col("_IS_Weight_mg")).alias(
                "Weight_mg"
            ),
        )
        .with_columns(
            pl.col("Area")
            .filter(pl.col("Standard").is_null())
            .sum()
            .over(over)
            .alias("Sum_Area"),
            pl.col("Weight_mg")
            .filter(pl.col("Standard").is_null())
            .sum()
            .over(over)
            .alias("Sum_Weight_mg"),
        )
        .with_columns(
            (pl.col("Area") / pl.col("Sum_Area") * 100).alias("Percent_Area"),
            # Считаем итоговый ppt по сухой массе
            (pl.col("Weight_mg") / pl.col("DryWeight_g")).alias(
                "PartsPerThousand_DryWeight"
            ),
            # Считаем итоговый ppm по сухой массе
            ((pl.col("Weight_mg") / pl.col("DryWeight_g")) * 1000).alias(
                "PartsPerMillion_DryWeight"
            ),
        )
        .with_columns(
            (pl.col("Sum_Weight_mg") / pl.col("DryWeight_g"))
            .over(over)
            .alias("_Lipids_mg_g"),
            pl.col("Percent_Area")
            .filter(pl.col("Standard").is_null())
            .sum()
            .round(1)
            .over(over)
            .alias("Sum_Percent_Area"),
            pl.col("PartsPerThousand_DryWeight")
            .filter(pl.col("Standard").is_null())
            .sum()
            .over(over)
            .alias("Sum_PartsPerThousand_DryWeight"),
            pl.col("PartsPerMillion_DryWeight")
            .filter(pl.col("Standard").is_null())
            .sum()
            .over(over)
            .alias("Sum_PartsPerMillion_DryWeight"),
        )
        .select(
            [
                "Ni",
                "Week",
                "Sample",
                "Plant",
                "WaterFraction",
                "FreshWeight",
                "FattyAcid",
                "Standard",
                "Area",
                "Percent_Area",
                "PartsPerThousand_DryWeight",
                "PartsPerMillion_DryWeight",
                "Sum_Percent_Area",
                "Sum_PartsPerThousand_DryWeight",
                "Sum_PartsPerMillion_DryWeight",
            ]
        )
    )
    print(f"calculate_df: {calculate_df}")

    calculate_df.write_csv(
        f"D/csv/_{{Kind={organ}}}{{Fields=Ni,Week,Sample,Plant,FattyAcid,PartsPerX}}.txt"
    )

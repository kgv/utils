import polars as pl

over = ["Ni", "Week", "Sample", "Plant"]

# Чтение данных
df = pl.read_csv(
    "D/{Kind=Leaf}{Fields=Ni,Week,Sample,Plant,WaterFraction,FreshWeight,FattyAcid,Standard,Area}.txt"
)
print(f"df: {df}")

df = df.with_columns(DryWeight_g=pl.col("FreshWeight") * (1 - pl.col("WaterFraction")))
print(f"DryWeight: {df}")

df = (
    df.with_columns(
        # Находим площадь (Area) внутреннего стандарта для каждого Plant
        _IS_Area=pl.col("Area")
        .filter(pl.col("Standard").is_not_null())
        .first()
        .over(over),
        # Находим значение концентрации (Standard) для каждого Plant
        _IS_Weight_mg=pl.col("Standard").drop_nulls().first().over(over),
    )
    .with_columns(
        # Считаем абсолютную массу кислоты в мг
        Weight_mg=(pl.col("Area") / pl.col("_IS_Area"))
        * pl.col("_IS_Weight_mg"),
    )
    .with_columns(
        Sum_Area=pl.col("Area").filter(pl.col("Standard").is_null()).sum().over(over),
        Sum_Weight_mg=pl.col("Weight_mg")
        .filter(pl.col("Standard").is_null())
        .sum()
        .over(over),
    )
    .with_columns(
        Percent_Area=(pl.col("Area") / pl.col("Sum_Area") * 100),
        # Считаем итоговый ppt по сухой массе
        PartsPerThousand_DryWeight=(pl.col("Weight_mg") / pl.col("DryWeight_g")),
        # Считаем итоговый ppm по сухой массе
        PartsPerMillion_DryWeight=(pl.col("Weight_mg") / pl.col("DryWeight_g")) * 1000,
    )
    .with_columns(
        _Lipids_mg_g=(pl.col("Sum_Weight_mg") / pl.col("DryWeight_g")).over(over),
        Sum_Percent_Area=pl.col("Percent_Area")
        .filter(pl.col("Standard").is_null())
        .sum()
        .round(1)
        .over(over),
        Sum_PartsPerThousand_DryWeight=pl.col("PartsPerThousand_DryWeight")
        .filter(pl.col("Standard").is_null())
        .sum()
        .over(over),
        Sum_PartsPerMillion_DryWeight=pl.col("PartsPerMillion_DryWeight")
        .filter(pl.col("Standard").is_null())
        .sum()
        .over(over),
    )
    # .drop(["_IS_Area", "_IS_Standard"])
)

df = df.select(
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

df.write_csv("D/{Kind=Leaf}{Fields=Ni,Week,Sample,Plant,FattyAcid,PartsPerX}.txt")
# https://en.wikipedia.org/wiki/Parts-per_notation
# PartsPerHundred PartsPerThousand PartsPerMillion

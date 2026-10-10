import polars as pl

over = ["Ni", "Week", "Plant", "Sample"]

# Чтение данных
df = pl.read_csv(
    "Даша/Ni,Week,Plant,Sample,WaterFraction,FreshWeight,FattyAcid,Standard,Area.txt"
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
        _IS_Standard=pl.col("Standard").drop_nulls().first().over(over),
    )
    .with_columns(
        # Считаем абсолютную массу кислоты в мг
        Mass_mg=(pl.col("Area") / pl.col("_IS_Area"))
        * pl.col("_IS_Standard")
    )
    .with_columns(
        Sum_Mass_mg=pl.col("Mass_mg")
        .filter(pl.col("Standard").is_null())
        .sum()
        .over(over),
        # Считаем итоговый ppm по сухой массе
        PartsPerMillion=(pl.col("Mass_mg") / pl.col("DryWeight_g")) * 1000,
    )
    .with_columns(
        Lipids_mg_g=(pl.col("Sum_Mass_mg") / pl.col("DryWeight_g") * 1000).over(over),
        _PartsPerMillion_Sum=pl.col("PartsPerMillion")
        .filter(pl.col("Standard").is_null())
        .sum()
        .over(over),
        _Area_Sum=pl.col("Area").filter(pl.col("Standard").is_null()).sum().over(over),
    )
    .with_columns(
        Percent=(pl.col("Area") / pl.col("_Area_Sum") * 100),
    )
    .with_columns(
        _Percent_Sum=pl.col("Percent")
        .filter(pl.col("Standard").is_null())
        .sum()
        .round(1)
        .over(over),
    )
    # .drop(["_IS_Area", "_IS_Standard"])
)

df = df.select(
    [
        "Ni",
        "Week",
        "Plant",
        "Sample",
        "WaterFraction",
        "FreshWeight",
        "FattyAcid",
        "Standard",
        "Area",
        "PartsPerMillion",
        "Percent",
        "_PartsPerMillion_Sum",
        "_Percent_Sum",
    ]
)
# df = df.drop(
#     [
#         "WaterFraction",
#         "FreshWeight",
#         "Standard",
#         "Area",
#         "DryWeight_g",
#         "Mass_mg",
#         "Sum_Mass_mg",
#         "Lipids_mg_g",
#         "ppm_Sum",
#         "ppm_log1p",
#     ]
# )

df.write_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,PartsPerMillion,Percent.txt")

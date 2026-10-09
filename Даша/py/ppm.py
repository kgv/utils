import polars as pl

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,Water,FreshWeight,FattyAcid,Standard,Area.txt")
print(f"df: {df}")

df = df.with_columns(
    IS_Area=pl.col("Area")
)

# df = (
#     df.with_columns(
#         # 1. Находим площадь (Area) внутреннего стандарта для каждого Plant
#         IS_Area=pl.col("Area")
#         .filter(pl.col("Standard").is_not_null())
#         .first()
#         .over("Plant"),
#         # 2. Находим значение концентрации (Standard) для каждого Plant
#         IS_Standard=pl.col("Standard").drop_nulls().first().over("Plant"),
#     ).with_columns(
#         # 3. Считаем итоговый ppm по формуле
#         ppm=(pl.col("Area") / pl.col("IS_Area"))
#         * pl.col("IS_Standard")
#     )
#     # .drop(["IS_Area", "IS_Standard"])
# )  # удаляем промежуточные колонки, если они не нужны


df.write_csv("Даша/output.txt")

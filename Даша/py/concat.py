import polars as pl

# Чтение данных
df_0_1 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=0mM}{Week=1}.txt")
df_0_5 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=0mM}{Week=5}.txt")
df_50_1 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=50mM}{Week=1}.txt")
df_50_5 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=50mM}{Week=5}.txt")
df_250_1 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=250mM}{Week=1}.txt")
df_250_5 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=250mM}{Week=5}.txt")
df_500_1 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=500mM}{Week=1}.txt")
df_500_5 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=500mM}{Week=5}.txt")
df_750_1 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=750mM}{Week=1}.txt")
df_750_5 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=750mM}{Week=5}.txt")
df_1000_1 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=1000mM}{Week=1}.txt")
df_1000_5 = pl.read_csv("Даша/csv/{Name=Корни}{Ni=1000mM}{Week=5}.txt")

dfs = [
    df_0_1,
    df_0_5,
    df_50_1,
    df_50_5,
    df_250_1,
    df_250_5,
    df_500_1,
    df_500_5,
    df_750_1,
    df_750_5,
    df_1000_1,
    df_1000_5,
]

unpivot_dfs = [
    df.unpivot(
        index=["FattyAcid", "Standard", "Ni", "Week"],
        variable_name="Plant",
        value_name="Area",
    )
    .with_columns(
        pl.col("Plant").cast(pl.Int64),
    )
    .select([pl.col("Plant"), pl.all().exclude("Plant")])
    for df in dfs
]

df = pl.concat(unpivot_dfs)
print(f"unpivot: {df}")

df.write_csv("Даша/output.txt")

# df = (
#     df.unpivot(
#         index=["FattyAcid", "Standard", "Ni", "Week"],
#         variable_name="Plant",
#         value_name="Area",
#     )
#     .with_columns(
#         pl.col("Plant").cast(pl.Int64),
#     )
#     .select([pl.col("Plant"), pl.all().exclude("Plant")])
# )

# df = df.join(
#     df,
#     on=["Vial"],
#     how="full",
#     coalesce=True,
#     # maintain_order="left_right",
# ).select(
#     [
#         "Species",
#         "Object",
#         "Tree",
#         "Vial",
#         "Component",
#         "CAS",
#         "RI",
#         "RT",
#         "Percent",
#         "PartsPerMillion",
#     ]
# )
# print(f"df: {df}")

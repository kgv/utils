import polars as pl

# Чтение данных
df = pl.read_csv("D/Plant,FattyAcid,Standard,Ni,Week,Area.txt")
print(f"df: {df}")
plant_df = pl.read_csv("D/csv/Plant,Sample.txt")
print(f"plant_df: {plant_df}")

df = df.join(
    plant_df,
    on=["Plant"],
    how="full",
    coalesce=True,
    maintain_order="left_right",
).select(
    [
        "Ni",
        "Week",
        "Plant",
        "Sample",
        "Water",
        "FreshWeight",
        "FattyAcid",
        "Standard",
        "Area",
    ]
)

df.write_csv("D/output.txt")

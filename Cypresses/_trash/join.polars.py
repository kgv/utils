import polars as pl

# Чтение данных
species_df = pl.read_csv("Cypresses/csv/Species,Object,Tree,Vial,Light,Description.txt")
print(f"species_df: {species_df}")
df = pl.read_csv("Cypresses/csv/Vial,Component,CAS,RI,RT,Percent,PartsPerMillion.txt")
print(f"df: {df}")

df = species_df.join(
    df,
    on=["Vial"],
    how="full",
    coalesce=True,
    # maintain_order="left_right",
).select(
    [
        "Species",
        "Object",
        "Tree",
        "Vial",
        "Component",
        "CAS",
        "RI",
        "RT",
        "Percent",
        "PartsPerMillion",
    ]
)
print(f"df: {df}")
df.write_csv("output.txt")

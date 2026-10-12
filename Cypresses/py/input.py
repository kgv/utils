import polars as pl
from utils import format_list

# Чтение данных

# PartsPerMillion
ppm_df = pl.read_csv("Cypresses/csv/{Kind=Input}{Name=PartsPerMillion}.txt")
print(f"ppm_df: {ppm_df}")
ppm_df = (
    ppm_df.unpivot(
        index=["Component", "CAS", "RI", "RT"],
        variable_name="Vial",
        value_name="PartsPerMillion",
    )
    .with_columns(
        [
            pl.col("Vial").str.split(by=" ").list.first().cast(pl.Int64),
            pl.col("PartsPerMillion").replace("", None).cast(pl.Float64),
        ]
    )
    .sort(pl.col("Vial"))
    .select(
        "Vial",
        "Component",
        "CAS",
        "RI",
        "RT",
        "PartsPerMillion",
    )
)
print(f"ppm_df: {ppm_df}")
ppm_df.write_csv("Cypresses/_PartsPerMillion.txt")

# Percent
pc_df = pl.read_csv("Cypresses/csv/{Kind=Input}{Name=Percent}.txt")
print(f"pc_df: {pc_df}")
pc_df = (
    pc_df.unpivot(
        index=["Component", "CAS", "RI", "RT"],
        variable_name="Vial",
        value_name="Percent",
    )
    .with_columns(
        [
            pl.col("Vial").str.split(by=" ").list.first().cast(pl.Int64),
            pl.col("Percent").replace("", None).cast(pl.Float64),
        ]
    )
    .sort(pl.col("Vial"))
    .select(
        "Vial",
        "Component",
        "CAS",
        "RI",
        "RT",
        "Percent",
    )
)
print(f"pc_df: {pc_df}")
pc_df.write_csv("Cypresses/_Percent.txt")

df = pc_df.join(
    ppm_df,
    on=["Vial", "Component", "CAS", "RI", "RT"],
    how="full",
    coalesce=True,
    maintain_order="left_right",
).select(
    [
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
df.write_csv("Cypresses/{Fields=Vial,Component,CAS,RI,RT,Percent,PartsPerMillion}.txt")

# Species
species_df = pl.read_csv(
    "Cypresses/csv/{Kind=Input}{Fields=Identifier,Genus,Species,Variety,Url}.txt"
)
print(f"species_df: {species_df}")
# Description
description_df = pl.read_csv(
    "Cypresses/csv/{Kind=Input}{Fields=Identifier,Tree,Vial,Description}.txt"
)
print(f"description_df: {description_df}")

# + Identifier,Tree
df = description_df.join(
    df,
    on=["Vial"],
    how="full",
    coalesce=True,
    maintain_order="right_left",
).select(
    [
        "Identifier",
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

# + Genus,Species,Variety
df = species_df.join(
    df,
    on=["Identifier"],
    how="full",
    coalesce=True,
    maintain_order="right_left",
).select(
    [
        "Genus",
        "Species",
        "Variety",
        "Identifier",
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

df.write_csv(
    "Cypresses/csv/{Kind=Output}{Fields=Genus,Species,Variety,Identifier,Tree,Vial,Component,CAS,RI,RT,Percent,PartsPerMillion}.txt"
)

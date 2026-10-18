import polars as pl
from utils import format_list

# Чтение данных

# PartsPerMillion
ppm_df = pl.read_csv("Cypresses/csv/{Type=Input}{Name=PartsPerMillion}.txt")
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
# ppm_df.write_csv("Cypresses/_PartsPerMillion.txt")

# Percent
pc_df = pl.read_csv("Cypresses/csv/{Type=Input}{Name=Percent}.txt")
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
# pc_df.write_csv("Cypresses/_Percent.txt")

pc_ppm_df = pc_df.join(
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
print(f"pc_df+ppm_df: {pc_ppm_df}")

# Species
species_df = pl.read_csv(
    "Cypresses/csv/{Type=Input}{Fields=Identifier,Genus,Species,Variety,Url}.txt"
)
print(f"species_df: {species_df}")
# Description
description_df = pl.read_csv(
    "Cypresses/csv/{Type=Input}{Fields=Identifier,Tree,Vial,Description}.txt"
)
print(f"description_df: {description_df}")

# + Identifier,Tree
identifier_df = description_df.join(
    pc_ppm_df,
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
join_df = species_df.join(
    identifier_df,
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

# Monoterpene < 1200 (1166.8)
# Sesquiterpene
terpene_df = join_df.with_columns(
    pl.when(pl.col("RI").cast(pl.Float64, strict=False) < 1200)
    .then(pl.lit("Monoterpene"))
    .otherwise(pl.lit("Sesquiterpene"))
    .alias("Terpene")
).select(
    [
        "Genus",
        "Species",
        "Variety",
        "Identifier",
        "Tree",
        "Vial",
        "Terpene",
        "Component",
        "CAS",
        "RI",
        "RT",
        "Percent",
        "PartsPerMillion",
    ]
)

terpene_df.write_csv(
    "Cypresses/csv/_{Type=Output}{Fields=Genus,Species,Variety,Identifier,Tree,Vial,Terpene,Component,CAS,RI,RT,Percent,PartsPerMillion}.txt"
)

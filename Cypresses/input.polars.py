import polars as pl

# Чтение данных
ppm_df = pl.read_csv("Cypresses/csv/Input_PartsPerMillion.txt")
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
ppm_df.write_csv("_PartsPerMillion.txt")

pc_df = pl.read_csv("Cypresses/csv/Input_Percent.txt")
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
pc_df.write_csv("_Percent.txt")

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
df.write_csv("Vial,Component,CAS,RI,RT,Percent,PartsPerMillion.txt")

import polars as pl

# Чтение данных
ppm_df = pl.read_csv("Cypresses/csv/_PartsPerMillion.txt")
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
            pl.col("Vial").alias("File"),
        ]
    )
    .select(
        "Vial",
        "File",
    )
    .unique()
    .sort(pl.col("Vial"))
)
print(f"ppm_df: {ppm_df}")
ppm_df.write_csv("temp.txt")

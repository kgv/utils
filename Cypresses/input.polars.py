from pathlib import Path
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns

N = 3
CONTROL_LINE = "54 WT"

# Чтение данных
df = pl.read_csv(
    "Cypresses/csv/Vial,Species,Object,Tree,Component,CAS,RI,RT,Absolute.txt",
    schema_overrides={"Object": pl.String},
)
print(f"df: {df}")

percent = pl.read_csv("Cypresses/csv/Percent.txt")
print(f"read: {percent}")

# # Вычищаем лишние пробелы из заголовков
# df = df.rename({col: col.strip() for col in df.columns})
# print(f"rename: {df}")

# df = df.with_columns(
#     [
#         pl.col("Вид").str.strip_chars().replace("", None).forward_fill(),
#         pl.col("Образец").str.strip_chars().replace("", None).forward_fill(),
#     ]
# )
# print(f"forward_fill: {df}")

percent = percent.unpivot(
    index=["Component", "CAS", "RI", "RT"],
    variable_name="Vial",
    value_name="Percent",
).with_columns(pl.col("Vial").cast(pl.Int64))
print(f"unpivot: {percent}")

df = df.join(
    percent, on=["Vial", "Component", "CAS", "RI", "RT"], how="full", coalesce=True
).select(
    [
        "Vial",
        "Species",
        "Object",
        "Tree",
        "Component",
        "CAS",
        "RI",
        "RT",
        "Percent",
        "Absolute",
    ]
).sort("Vial")

print(f"join: {df}")

df.write_csv("output.txt")


# # pl.struct("Vial", "Value").alias("Values")
# df = df.group_by(["Component", "CAS", "RI", "RT"]).agg(["Vial", "Value"])
# print(f"group_by: {df}")

# df = df.explode(["Vial", "Value"])
# print(f"explode: {df}")

# df = df.pivot(index=["Проба (виала)"], on="Компонент", values="Value")
# print(f"df: {df}")
# day_df.pivot(values="Log_p_value", index="FattyAcid", on="Line")

# # Вычищаем пробелы из всех строковых колонок и приводим типы
# df = df.with_columns(pl.col(pl.String()).str.strip_chars()).with_columns(
#     pl.col("Вид"),
#     pl.col("Образец"),
#     pl.col("Проба").cast(pl.Int64),
# )
# print(f"df: {df}")

# df = df.unpivot(
#     index=["Вид", "Образец", "Проба"], variable_name="VariableName", value_name="Value"
# )
# print(f"df: {df}")

# df = df.group_by(["Вид", "Образец"]).agg("Проба")
# print(f"df: {df}")

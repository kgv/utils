from pathlib import Path
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import polars as pl
import seaborn as sns

N = 3
light = pl.Enum(["min", "med", "max"])

# Чтение данных
# header = pl.read_csv(
#     "Cypresses/csv/Vial,Species,Object,Tree,Description,Light.txt",
#     schema_overrides={"Light": light},
# )
# print(f"read: {header}")

df = pl.read_csv(
    "Cypresses/csv/Species,Object,Tree,Vial,Component,CAS,RI,RT,Percent,Absolute.txt",
    schema_overrides={"Object": pl.String},
)
print(f"df: {df}")

traits_df = pl.read_csv(
    "Cypresses/csv/Vial,Species,Object,Tree,Description,Light.txt",
    schema_overrides={"Object": pl.String, "Light": light},
)
print(f"traits_df: {traits_df}")

df = df.group_by(["Species", "Object", "Tree", "Vial"]).agg().sort("Vial")
print(f"df: {df}")

# df = df.with_columns(
#     Tree=pl.struct(["Species", "Object", "Tree"]).rank().cast(pl.Int64)
# )
# print(f"df: {df}")

# # 1. Выделяем все уникальные пары "Object + Tree"
# # maintain_order=True гарантирует, что они останутся в том порядке, как шли в CSV
# other = (
#     df.select(["Object", "Tree"])
#     .unique(maintain_order=True)
#     .with_columns(
#         # Генерируем числа от 1 до количества уникальных деревьев
#         GlobalTree=pl.int_range(1, pl.len() + 1)
#     )
# )

# # 2. Присоединяем эти новые номера к основному датафрейму
# df = (
#     df.join(other, on=["Object", "Tree"], how="left")
#     .drop("Tree")  # Удаляем старую колонку со сбитой нумерацией (1,2, 1,2)
#     .rename({"GlobalTree": "Tree"})
#     .select(
#         "Species",
#         "Object",
#         "Tree",
#         "Vial",
#         "Component",
#         "CAS",
#         "RI",
#         "RT",
#         "Percent",
#         "Absolute",
#     )
# )

df.write_csv("output.txt")

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

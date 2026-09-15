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
    "Cypresses/csv/Vial,Species,Object,Tree,Component,CAS,RI,RT,Percent,Absolute.txt",
    schema_overrides={"Object": pl.String},
)
print(f"df: {df}")

traits_df = pl.read_csv(
    "Cypresses/csv/Vial,Species,Object,Tree,Description,Light.txt",
    schema_overrides={"Object": pl.String, "Light": light},
)
print(f"traits_df: {traits_df}")

# 2. Трансформируем данные в "широкий" формат
df = df.pivot(
    values="Absolute",
    index=["Object", "Tree"],
    on="Component",
    aggregate_function="mean"
).fill_null(0.0) 
print(f"pivot: {df}")

# 3. Выделяем матрицу признаков (изолируем только химические компоненты)
# Получаем список столбцов, игнорируя метаданные (Object, Tree)
component_cols = [col for col in df.columns if col not in ["Object", "Tree"]]
print(f"component_cols: {component_cols}")

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

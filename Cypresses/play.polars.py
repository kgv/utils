from pathlib import Path
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import polars as pl
import polars.selectors as cs
import seaborn as sns

# 1166,8 (1200) - монотерпены
# сесквитерпены
# н/и RI 1671.6 (вероятно, производное ионола) - исключаем как вероятно, производное ионола

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
    schema_overrides={
        "Species": pl.String,
        "Object": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.Int64,
        "CAS": pl.String,
        "RI": pl.Float64,
        "RT": pl.Float64,
        "Percent": pl.Float64,
        "Absolute": pl.Float64,
    },
)
print(f"df: {df}")

traits_df = pl.read_csv(
    "Cypresses/csv/Species,Object,Tree,Vial,Light,Description.txt",
    schema_overrides={"Object": pl.String, "Light": light},
)
print(f"traits_df: {traits_df}")

# $RSD_{pooled} = \sqrt{ \frac{(n_1-1)RSD_1^2 + (n_2-1)RSD_2^2 + \dots + (n_k-1)RSD_k^2}{(n_1-1) + (n_2-1) + \dots + (n_k-1)} }$

################################################################################
# Mean for Tree
tree_component_stats = (
    df.group_by(["Species", "Object", "Tree", "Component"], maintain_order=True)
    .agg(
        pl.col("Vial"),
        pl.col("Absolute").mean().round(1).alias("Absolute_Mean"),
        pl.col("Absolute").std().round(1).alias("Absolute_StandardDeviation"),
        (pl.col("Absolute").std() / pl.col("Absolute").mean() * 100)
        .round(1)
        .alias("Absolute_RelativeStandardDeviation"),
        pl.col("Percent").mean().round(1).alias("Percent_Mean"),
        pl.col("Percent").std().round(1).alias("Percent_StandardDeviation"),
        (pl.col("Percent").std() / pl.col("Percent").mean() * 100)
        .round(1)
        .alias("Percent_RelativeStandardDeviation"),
        pl.len().alias("N"),
    )
    .with_columns(
        pl.format("[{}]", pl.col("Vial").cast(pl.List(pl.String)).list.join(",")),
    )
    .select(
        [
            "Species",
            "Object",
            "Tree",
            "Vial",
            "Component",
            "Absolute_Mean",
            "Absolute_StandardDeviation",
            "Absolute_RelativeStandardDeviation",
            "Percent_Mean",
            "Percent_StandardDeviation",
            "Percent_RelativeStandardDeviation",
            "N",
        ]
    )
)
print(f"tree_component_stats: {tree_component_stats}")
tree_component_stats.write_csv("TreeComponentStats.txt")

tree_stats = (
    tree_component_stats.with_columns(
        # Числитель: (n - 1) * RSD^2
        ((pl.col("N") - 1) * (pl.col("Absolute_RelativeStandardDeviation") ** 2)).alias(
            "_Numerator"
        ),
        # Знаменатель: (n - 1)
        (pl.col("N") - 1).alias("_Denominator"),
    )
    .group_by(["Species", "Object", "Tree"], maintain_order=True)
    .agg(
        pl.col("Vial"),
        # Суммируем числители и знаменатели
        pl.col("_Numerator").sum().alias("_Numerator"),
        pl.col("_Denominator").sum().alias("_Denominator"),
        # Считаем, сколько веществ пошло в расчет
        pl.len().alias("N"),
    )
    .with_columns(
        pl.col("Vial").list.unique().list.join(","),
        # Итоговый Pooled RSD для дерева
        # (pl.col("_Numerator") / pl.col("_Denominator")).sqrt()
        pl.when(pl.col("_Denominator") > 0)
        .then((pl.col("_Numerator") / pl.col("_Denominator")).sqrt())
        .otherwise(None)
        .alias("RSD"),
    )
    .drop(["_Numerator", "_Denominator"])
    .with_columns(cs.float().round(2))
    .select(
        [
            "Species",
            "Object",
            "Tree",
            "Vial",
            "RSD",
            "N",
        ]
    )
)
print(f"tree_stats: {tree_stats}")
tree_stats.write_csv("TreeStats.txt")

# ################################################################################
# # Mean for Object
# object_component_stats = (
#     df.group_by(["Species", "Object", "Component"], maintain_order=True)
#     .agg(
#         pl.col("Tree"),
#         pl.col("Vial"),
#         pl.col("Absolute").mean().round(1).alias("Absolute_Mean"),
#         pl.col("Absolute").std().round(1).alias("Absolute_StandardDeviation"),
#         (pl.col("Absolute").std() / pl.col("Absolute").mean() * 100)
#         .round(1)
#         .alias("Absolute_RelativeStandardDeviation"),
#         pl.col("Percent").mean().round(1).alias("Percent_Mean"),
#         pl.col("Percent").std().round(1).alias("Percent_StandardDeviation"),
#         (pl.col("Percent").std() / pl.col("Percent").mean() * 100)
#         .round(1)
#         .alias("Percent_RelativeStandardDeviation"),
#         pl.len().alias("N"),
#     )
#     .with_columns(
#         [
#             pl.format("[{}]", pl.col("Tree").cast(pl.List(pl.String)).list.join(",")),
#             pl.format("[{}]", pl.col("Vial").cast(pl.List(pl.String)).list.join(",")),
#         ]
#     )
#     .select(
#         [
#             "Species",
#             "Object",
#             "Tree",
#             "Vial",
#             "Component",
#             "Absolute_Mean",
#             "Absolute_StandardDeviation",
#             "Absolute_RelativeStandardDeviation",
#             "Percent_Mean",
#             "Percent_StandardDeviation",
#             "Percent_RelativeStandardDeviation",
#             "N",
#         ]
#     )
# )
# # Absolute_Mean,Absolute_StandardDeviation,Absolute_RelativeStandardDeviation,Percent_Mean,Percent_StandardDeviation,Percent_RelativeStandardDeviation,Tree,Vial,N
# print(f"object_component_stats: {object_component_stats}")
# object_component_stats.write_csv("ObjectComponentStats.txt")

# object_stats = (
#     object_component_stats.with_columns(
#         # Числитель: (n - 1) * RSD^2
#         ((pl.col("N") - 1) * (pl.col("Absolute_RelativeStandardDeviation") ** 2)).alias(
#             "_Numerator"
#         ),
#         # Знаменатель: (n - 1)
#         (pl.col("N") - 1).alias("_Denominator"),
#     )
#     .group_by(["Species", "Object"], maintain_order=True)
#     .agg(
#         pl.col("Tree"),
#         pl.col("Vial"),
#         # Суммируем числители и знаменатели
#         pl.col("_Numerator").sum().alias("_Numerator"),
#         pl.col("_Denominator").sum().alias("_Denominator"),
#         # Считаем, сколько веществ пошло в расчет
#         pl.len().alias("N"),
#     )
#     .with_columns(
#         pl.col("Tree").list.unique().list.join(","),
#         pl.col("Vial").list.unique().list.join(","),
#         # Итоговый Pooled RSD для дерева
#         (pl.col("_Numerator") / pl.col("_Denominator")).sqrt().alias("RSD"),
#     )
#     .drop(["_Numerator", "_Denominator"])
#     .with_columns(cs.float().round(2))
#     .select(
#         [
#             "Species",
#             "Object",
#             "Tree",
#             "Vial",
#             "RSD",
#             "N",
#         ]
#     )
# )
# print(f"object_stats: {object_stats}")
# object_stats.write_csv("ObjectStats.txt")

################################################################################

# df = df.group_by(["Species", "Object", "Tree", "Vial"]).agg().sort("Vial")
# print(f"df: {df}")

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

from pathlib import Path
from scipy.stats import ttest_ind_from_stats
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import polars as pl
import polars.selectors as cs
import seaborn as sns

# 1166,8 (1200) - монотерпены
# сесквитерпены
# "н/и RI 1671.6 (вероятно, производное ионола)" - исключаем как вероятно, производное ионола

df = pl.read_csv(
    "Cypresses/csv/Species,Object,Tree,Vial,Component,CAS,RI,RT,Percent,PartsPerMillion.txt",
    schema_overrides={
        "Species": pl.String,
        "Object": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.Int64,
        "CAS": pl.String,
        "RI": pl.Float64,
        "RT": pl.Float64,
        "Percent": pl.Float64,
        "PartsPerMillion": pl.Float64,
    },
)
print(f"read: {df}")

df = df.filter(pl.col("Component") != "н/и RI 1671.6 (вероятно, производное ионола)")
print(f"filter: {df}")

# Mean for Tree
df = (
    df.group_by(["Species", "Object", "Tree", "Component"], maintain_order=True)
    .agg(
        pl.col("Vial"),
        pl.col("PartsPerMillion").mean().alias("PartsPerMillion_Mean"),
        pl.col("PartsPerMillion").std().alias("PartsPerMillion_StandardDeviation"),
        (
            pl.col("PartsPerMillion").std() / pl.col("PartsPerMillion").mean() * 100
        ).alias("PartsPerMillion_RelativeStandardDeviation"),
        pl.col("Percent").mean().alias("Percent_Mean"),
        pl.col("Percent").std().alias("Percent_StandardDeviation"),
        (pl.col("Percent").std() / pl.col("Percent").mean() * 100).alias(
            "Percent_RelativeStandardDeviation"
        ),
        pl.len().alias("N"),
    )
    .with_columns(
        pl.format("[{}]", pl.col("Vial").cast(pl.List(pl.String)).list.join(",")).alias(
            "Vial"
        ),
    )
    .select(
        [
            "Species",
            "Object",
            "Tree",
            "Vial",
            "Component",
            "PartsPerMillion_Mean",
            "PartsPerMillion_StandardDeviation",
            "PartsPerMillion_RelativeStandardDeviation",
            "Percent_Mean",
            "Percent_StandardDeviation",
            "Percent_RelativeStandardDeviation",
            "N",
        ]
    )
)
print(f"group: {df}")

# df = (
#     df.with_columns(cs.float().round(3))
#     .with_columns(
#         pl.format(
#             "{}±{}",
#             pl.col("PartsPerMillion_Mean"),
#             pl.col("PartsPerMillion_StandardDeviation").cast(pl.String).fill_null(""),
#         ).alias("PartsPerMillion")
#     )
#     .pivot(
#         index=[
#             "Species",
#             "Object",
#             "Tree",
#             "Vial",
#         ],
#         on="Component",
#         values="PartsPerMillion",
#     )
# )
# print(f"pivot: {df}")
df = df.pivot(
    index=[
        "Species",
        "Object",
        "Tree",
        "Vial",
    ],
    on="Component",
    values="PartsPerMillion_Mean",
)
df.write_csv("TreeComponent.txt")

# # $RSD_{pooled} = \sqrt{ \frac{(n_1-1)RSD_1^2 + (n_2-1)RSD_2^2 + \dots + (n_k-1)RSD_k^2}{(n_1-1) + (n_2-1) + \dots + (n_k-1)} }$
# tree_stats = (
#     tree_component_stats.with_columns(
#         # Числитель: (n - 1) * RSD^2
#         (
#             (pl.col("N") - 1)
#             * (pl.col("PartsPerMillion_RelativeStandardDeviation") ** 2)
#         ).alias("_Numerator"),
#         # Знаменатель: (n - 1)
#         (pl.col("N") - 1).alias("_Denominator"),
#     )
#     .group_by(["Species", "Object", "Tree"], maintain_order=True)
#     .agg(
#         pl.col("Vial"),
#         # Суммируем числители и знаменатели
#         pl.col("_Numerator").sum().alias("_Numerator"),
#         pl.col("_Denominator").sum().alias("_Denominator"),
#         # Считаем, сколько веществ пошло в расчет
#         pl.len().alias("N"),
#     )
#     .with_columns(
#         pl.col("Vial").list.unique().list.join(","),
#         # Итоговый Pooled RSD для дерева
#         # (pl.col("_Numerator") / pl.col("_Denominator")).sqrt()
#         pl.when(pl.col("_Denominator") > 0)
#         .then((pl.col("_Numerator") / pl.col("_Denominator")).sqrt())
#         .otherwise(None)
#         .alias("RSD"),
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
# print(f"tree_stats: {tree_stats}")
# tree_stats.write_csv("TreeStats.txt")

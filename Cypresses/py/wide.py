from pathlib import Path
from scipy.stats import ttest_ind_from_stats
from sklearn.feature_selection import chi2
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import cosine_distances
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances
from sklearn.preprocessing import normalize
from utils import format_list
import matplotlib.pyplot as plot
import matplotlib.pyplot as plt
import polars as pl
import polars.selectors as cs
import seaborn as sns

# 1166,8 (1200) - монотерпены
# сесквитерпены
# "н/и RI 1671.6 (вероятно, производное ионола)" - исключаем как вероятно, производное ионола

df = pl.read_csv(
    "Cypresses/csv/{Kind=Output}{Fields=Genus,Species,Variety,Identifier,Tree,Vial,Component,CAS,RI,RT,Percent,PartsPerMillion}.txt",
    schema_overrides={
        "Genus": pl.String,
        "Species": pl.String,
        "Variety": pl.String,
        "Identifier": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.Int64,
        "Component": pl.String,
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
    df.group_by(
        ["Genus", "Species", "Variety", "Identifier", "Tree", "Component"],
        maintain_order=True,
    )
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
    .with_columns(format_list("Vial"))
    .select(
        [
            "Genus",
            "Species",
            "Variety",
            "Identifier",
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
df.write_csv("Cypresses/_Stats.txt")

df = df.pivot(
    index=[
        "Genus",
        "Species",
        "Variety",
        "Identifier",
        "Tree",
        "Vial",
    ],
    on="Component",
    values="PartsPerMillion_Mean",
)
df.write_csv("Cypresses/_Wide.txt")

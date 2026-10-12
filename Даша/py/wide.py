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

# "Ni",
# "Week",
# "Plant",
# "Sample",
# "WaterFraction",
# "FreshWeight",
# "FattyAcid",
# "Standard": pl.Float64,
# "Area": pl.Float64,
# "Percent_Area": pl.Float64,
# "PartsPerThousand_DryWeight": pl.Float64,
# "PartsPerMillion_DryWeight": pl.Float64,
# "Sum_Percent_Area": pl.Float64,
# "Sum_PartsPerThousand_DryWeight": pl.Float64,
# "Sum_PartsPerMillion_DryWeight": pl.Float64,

# kind = "Leaf"
kind = "Root"
# values = "Percent_Area" # Столбец, откуда берем сами цифры
values = "PartsPerMillion_DryWeight"

df = pl.read_csv(
    f"Даша/{{Kind={kind}}}{{Fields=Ni,Week,Sample,Plant,FattyAcid,PartsPerX}}.txt",
)
print(f"read: {df}")

# Превращаем в широкий формат
df = df.filter((pl.col("FattyAcid") != "17:0") & (pl.col("FattyAcid") != "15:0")).pivot(
    index=["Ni", "Week", "Sample"],
    on="FattyAcid",  # Столбец, значения которого станут новыми заголовками
    values=values,
)

# df = df.filter(pl.col("Week") == 5)
# df = df.with_columns(
#     pl.when(pl.col("Ni") == 0)
#     .then(pl.lit("Control"))
#     .otherwise(pl.lit("Experiment"))
#     .alias("Ni")
# )

df.write_csv(f"Даша/_Wide{{Kind={kind}}}{{Value={values}}}.txt")
# df.write_csv(f"Даша/_Wide{{Kind={kind}}}{{Value={values}}}{{Week=5}}.txt")

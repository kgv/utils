from utils import format_list
import polars as pl
import polars.selectors as cs

COMPONENT = [
    "Terpene",
    "Monoterpene",
    "Sesquiterpene",
]

VALUE = [
    "Percent_Mean",
    "PartsPerMillion_Mean",
]

read_df = pl.read_csv(
    "Cypresses/csv/_{Type=Output}{Fields=Genus,Species,Variety,Identifier,Tree,Vial,Terpene,Component,CAS,RI,RT,Percent,PartsPerMillion}.txt",
    schema_overrides={
        "Genus": pl.String,
        "Subgenus": pl.String,
        "Species": pl.String,
        "Variety": pl.String,
        "Identifier": pl.String,
        "Tree": pl.Int64,
        "Vial": pl.Int64,
        "Terpene": pl.String,
        "Component": pl.String,
        "CAS": pl.String,
        "RI": pl.Float64,
        "RT": pl.Float64,
        "Percent": pl.Float64,
        "PartsPerMillion": pl.Float64,
    },
)
print(f"read: {read_df}")

# "н/и RI 1671.6 (вероятно, производное ионола)" - исключаем как вероятно, производное ионола
filter_df = read_df.filter(
    pl.col("Component") != "н/и RI 1671.6 (вероятно, производное ионола)"
)
print(f"filter: {filter_df}")

# Technical replications (Mean for Tree)
stats_df = (
    filter_df.group_by(
        [
            "Genus",
            "Subgenus",
            "Species",
            "Variety",
            "Identifier",
            "Tree",
            "Terpene",
            "Component",
        ],
        maintain_order=True,
    )
    .agg(
        pl.col("Vial"),
        pl.col("PartsPerMillion"),
        pl.col("PartsPerMillion").mean().alias("PartsPerMillion_Mean"),
        pl.col("PartsPerMillion").std().alias("PartsPerMillion_StandardDeviation"),
        (
            pl.col("PartsPerMillion").std() / pl.col("PartsPerMillion").mean() * 100
        ).alias("PartsPerMillion_RelativeStandardDeviation"),
        pl.col("Percent").alias("Percent"),
        pl.col("Percent").mean().alias("Percent_Mean"),
        pl.col("Percent").std().alias("Percent_StandardDeviation"),
        (pl.col("Percent").std() / pl.col("Percent").mean() * 100).alias(
            "Percent_RelativeStandardDeviation"
        ),
        pl.len().alias("N"),
    )
    .with_columns(
        [format_list("Vial"), format_list("PartsPerMillion"), format_list("Percent")]
    )
    .select(
        [
            "Genus",
            "Subgenus",
            "Species",
            "Variety",
            "Identifier",
            "Tree",
            "Vial",
            "Terpene",
            "Component",
            "PartsPerMillion",
            "PartsPerMillion_Mean",
            "PartsPerMillion_StandardDeviation",
            "PartsPerMillion_RelativeStandardDeviation",
            "Percent",
            "Percent_Mean",
            "Percent_StandardDeviation",
            "Percent_RelativeStandardDeviation",
            "N",
        ]
    )
)
# 1. Мы целенаправленно брали наиболее отличающиеся друг от друга технические повторности (свет/тень, среднестатистический/с особенностями развития, чтобы охватить весь возможный разброс профилей.
# 2. Пройтись по всем техническим повторностям еще раз и понять причину различий.
# трейты для биологических объектов: возраст, пол
# gps координаты для объектов
# stats_df = stats_df.filter(pl.col("PartsPerMillion_RelativeStandardDeviation") > 25)
# print(f"stats: {stats_df}")
# stats_df.write_csv("Cypresses/csv/_Stats.txt")

for component in COMPONENT:
    for value in VALUE:
        component_df = stats_df
        if component == "Monoterpene":
            component_df = stats_df.filter(pl.col("Terpene") == "Monoterpene")
        elif component == "Sesquiterpene":
            component_df = stats_df.filter(pl.col("Terpene") == "Sesquiterpene")

        wide_df = (
            component_df.pivot(
                index=[
                    "Genus",
                    "Subgenus",
                    "Species",
                    "Variety",
                    "Identifier",
                    "Tree",
                    "Vial",
                ],
                on="Component",
                values=value,
            )
            .with_columns(
                [
                    pl.concat_str(
                        [pl.col("Genus"), pl.col("Subgenus")],
                        separator=" ",
                        ignore_nulls=True,
                    ).alias("Subgenus"),
                    pl.concat_str(
                        [pl.col("Genus"), pl.col("Subgenus"), pl.col("Species")],
                        separator=" ",
                        ignore_nulls=True,
                    ).alias("Species"),
                    pl.concat_str(
                        [
                            pl.col("Genus"),
                            pl.col("Subgenus"),
                            pl.col("Species"),
                            pl.col("Variety"),
                        ],
                        separator=" ",
                        ignore_nulls=True,
                    ).alias("Variety"),
                ]
            )
            .with_columns(cs.float().fill_null(0.0))
        )
        wide_df.write_csv(
            f"Cypresses/csv/_{{Type=Wide}}{{Component={component}}}{{Value={value}}}.txt"
        )

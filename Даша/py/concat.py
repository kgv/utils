import polars as pl

KIND = [
    "Leaf",
    "Root",
]

for kind in KIND:
    dfs = [
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=0mM}}{{Week=1}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=0mM}}{{Week=5}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=50mM}}{{Week=1}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=50mM}}{{Week=5}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=250mM}}{{Week=1}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=250mM}}{{Week=5}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=500mM}}{{Week=1}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=500mM}}{{Week=5}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=750mM}}{{Week=1}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=750mM}}{{Week=5}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=1000mM}}{{Week=1}}.txt"),
        pl.read_csv(f"Даша/csv/{{Kind={kind}}}{{Ni=1000mM}}{{Week=5}}.txt"),
    ]

    unpivot_dfs = [
        df.unpivot(
            index=["FattyAcid", "Standard", "Ni", "Week"],
            variable_name="Sample",
            value_name="Area",
        )
        .with_columns(
            pl.col("Sample").cast(pl.Int64),
        )
        .select(
            [
                "Ni",
                "Week",
                "Sample",
                "FattyAcid",
                "Standard",
                "Area",
            ]
        )
        for df in dfs
    ]

unpivot_df = pl.concat(unpivot_dfs)
print(f"unpivot: {unpivot_df}")

unpivot_df.write_csv(
    "Даша/csv/_{Kind=Root}{Fields=Ni,Week,Sample,FattyAcid,Standard,Area}.txt"
)
# df.group_by(["Ni", "Week", "Plant"], maintain_order=True).agg().write_csv(
#     "Даша/output.txt"
# )

################################################################################

sample_df = pl.read_csv(
    "Даша/csv/{Kind=Root}{Fields=Ni,Week,Sample,Plant,WaterFraction,FreshWeight}.txt"
)
print(f"sample_df: {sample_df}")

# join_df = unpivot_df.join(
#     sample_df,
#     on=["Ni", "Week", "Plant"],
#     how="full",
#     coalesce=True,
#     maintain_order="left_right",
# ).select(
#     [
#         "Ni",
#         "Week",
#         "Sample",
#         "Plant",
#         "WaterFraction",
#         "FreshWeight",
#         "FattyAcid",
#         "Standard",
#         "Area",
#     ]
# )
join_df = unpivot_df.join(
    sample_df,
    on=["Ni", "Week", "Sample"],
    how="full",
    coalesce=True,
    maintain_order="left_right",
).select(
    [
        "Ni",
        "Week",
        "Sample",
        "Plant",
        "WaterFraction",
        "FreshWeight",
        "FattyAcid",
        "Standard",
        "Area",
    ]
)


join_df.write_csv(
    "Даша/csv/_{Kind=Root}{Fields=Ni,Week,Sample,Plant,WaterFraction,FreshWeight,FattyAcid,Standard,Area}.txt"
)

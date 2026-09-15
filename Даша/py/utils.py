import polars as pl


def format_list(name, round_decimals=1):
    return pl.format(
        "[{}]",
        pl.col(name)
        .list.eval(pl.element().round(round_decimals))
        .cast(pl.List(pl.String))
        .list.join(","),
    ).alias(name)

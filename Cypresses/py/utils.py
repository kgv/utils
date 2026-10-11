import polars as pl


def format_list(name, round_decimals=None):
    expr = pl.col(name)
    if round_decimals is not None:
        expr = expr.list.eval(pl.element().round(round_decimals))

    return pl.format(
        "[{}]",
        expr.cast(pl.List(pl.String)).list.join(","),
    ).alias(name)


# def format_list(name, round_decimals=1):
#     return pl.format(
#         "[{}]",
#         pl.col(name)
#         .list.eval(pl.element().round(round_decimals))
#         .cast(pl.List(pl.String))
#         .list.join(","),
#     ).alias(name)

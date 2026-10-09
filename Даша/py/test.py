import polars as pl

# Чтение данных
df = pl.read_csv("Даша/Ni,Week,Plant,Sample,FattyAcid,ppm.txt")
print(f"df: {df}")

df = df.filter(pl.col("FattyAcid") != "17:0")

df.write_csv("Даша/output.txt")

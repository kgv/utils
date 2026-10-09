import polars as pl

# Чтение данных
df = pl.read_csv("Даша/Sample,FattyAcid,Standard,Ni,Week,Area.txt")
print(f"df: {df}")

df.write_csv("Даша/output.txt")

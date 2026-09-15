library(vegan)
library(indicspecies)

# 1. Вставляем ваши сырые данные прямо в переменные 
# (я вставил первые 10 строк для примера, вы можете вставить ВСЕ 70 строк между кавычками)
text_108 <- "
| 1     | [Oleic/2;Linoleic;Oleic/2]                                | [12, 11.7, 10.4] |
| 2     | [Oleic/2;Linoleic;Palmitic/2]                             | [8.9, 8.8, 8.6]  |
| 3     | [Oleic/2;Oleic;Oleic/2]                                   | [7.3, 7.6, 8.3]  |
| 4     | [Oleic/2;Oleic;Palmitic/2]                                | [5.4, 5.7, 6.9]  |
| 5     | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]          | [5, 4.7, 3.1]    |
| 6     | [Linoleic/2;Linoleic;Oleic/2]                             | [3.4, 3.2, 3.4]  |
| 7     | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]       | [3.7, 3.6, 2.6]  |
| 8     | [Oleic/2;Linoleic;α-Linolenic/2]                          | [3.1, 2.9, 3]    |
| 9     | [Oleic/2;Linoleic;Stearic/2]                              | [2.3, 2.4, 2.3]  |
| 10    | [Linoleic/2;Oleic;Oleic/2]                                | [2.1, 2.1, 2.8]  |
"

text_1210 <- "
| 1      | [Palmitic/2;Linoleic;Palmitic/2]                          | [11.4, 12, 11.7] |
| 2      | [Palmitic/2;Oleic;Palmitic/2]                             | [10, 12.3, 11.6] |
| 3      | [Linoleic/2;Linoleic;Palmitic/2]                          | [7.8, 7.3, 7.4]  |
| 4      | [Linoleic/2;Oleic;Palmitic/2]                             | [6.8, 7.5, 7.4]  |
| 5      | [Oleic/2;Linoleic;Palmitic/2]                             | [6.5, 6.4, 6.7]  |
| 6      | [Oleic/2;Oleic;Palmitic/2]                                | [5.7, 6.6, 6.7]  |
| 7      | [Palmitic/2;Roughanic;Palmitic/2]                         | [4.4, 4.1, 3.6]  |
| 8      | [Palmitic/2;Linoleic;α-Linolenic/2]                       | [3.7, 3.3, 3.3]  |
| 9      | [Palmitic/2;Oleic;α-Linolenic/2]                          | [3.2, 3.4, 3.3]  |
| 10     | [Linoleic/2;Roughanic;Palmitic/2]                         | [3, 2.5, 2.3]    |
"

# --- ФУНКЦИЯ ДЛЯ ЧТЕНИЯ ВАШЕГО ФОРМАТА ТАБЛИЦ ---
parse_table <- function(txt, prefix) {
  lines <- strsplit(trimws(txt), "\n")[[1]]
  lines <- lines[grepl("\\[", lines)] # берем только строки с данными
  
  compounds <- character(); r1 <- numeric(); r2 <- numeric(); r3 <- numeric()
  
  for(l in lines) {
    parts <- trimws(unlist(strsplit(l, "\\|")))
    parts <- parts[parts != ""]
    comp <- parts[2]
    # Убираем скобки и разбиваем по запятой
    vals <- as.numeric(unlist(strsplit(gsub("\\[|\\]", "", parts[3]), ","))) 
    compounds <- c(compounds, comp)
    r1 <- c(r1, vals[1]); r2 <- c(r2, vals[2]); r3 <- c(r3, vals[3])
  }
  
  df <- data.frame(Compound = compounds, Rep1 = r1, Rep2 = r2, Rep3 = r3)
  colnames(df)[2:4] <- paste0(prefix, "_", 1:3)
  return(df)
}

# 2. Обрабатываем и объединяем данные
df_108 <- parse_table(text_108, "C108")
df_1210 <- parse_table(text_1210, "C1210")

# print(df_108)

# Собираем общую таблицу (если молекулы нет в одном образце, ставим 0)
full_data <- merge(df_108, df_1210, by = "Compound", all = TRUE)
full_data[is.na(full_data)] <- 0

print(full_data)

# Транспонируем (чтобы образцы были строками, а молекулы - столбцами)
rownames(full_data) <- full_data$Compound
abund_matrix <- t(full_data[, -1]) 

print(full_data)

# Задаем группы
groups <- factor(c(rep("C-108", 3), rep("C-1210", 3)))

# ========================================================
# НАЧИНАЕМ АНАЛИЗ
# ========================================================

# 1. PERMANOVA
cat("\n=== 1. PERMANOVA ===\n")
# Используем adonis2 (современная версия)
perm <- adonis2(abund_matrix ~ groups, method = "bray")
print(perm)

# 2. ANOSIM
cat("\n=== 2. ANOSIM ===\n")
ano <- anosim(abund_matrix, groups, distance = "bray")
summary(ano)

# 3. NMDS (Визуализация)
# Т.к. образцов мало (6), стресс будет близок к 0, это отлично.
nmds <- metaMDS(abund_matrix, distance="bray", k=2, autotransform = FALSE)
plot(nmds, type = "n", main="NMDS: C-108 vs C-1210")
points(nmds, display = "sites", pch = 16, cex = 2, col = c(rep("blue", 3), rep("red", 3)))
ordihull(nmds, groups = groups, draw = "polygon", col = c("blue", "red"), alpha = 50)
legend("topright", legend = levels(groups), fill = c("blue", "red"))

# 4. SIMPER (Кто вносит наибольший вклад в различия?)
cat("\n=== 4. SIMPER ===\n")
sim <- simper(abund_matrix, groups)
summary(sim)

# 5. IndVal (Индикаторные молекулы)
cat("\n=== 5. IndVal ===\n")
inv <- multipatt(abund_matrix, groups, func = "IndVal.g", control = how(nperm=999))
summary(inv)
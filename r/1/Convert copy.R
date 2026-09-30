# library(tidyverse)
library(vegan)
library(indicspecies)

# =====================================================================
# ШАГ 1: ПРЕОБРАЗОВАНИЕ ДАННЫХ И СОЗДАНИЕ CSV
# =====================================================================

raw_data <- "
| #   | FA                       | C-108  | C-1210 | C-70   | H-242  | H-1564 | H-150  |
| --- | ------------------------ | ------ | ------ | ------ | ------ | ------ | ------ |
| 0   | 14:0                     | [0.06] | [0.08] | [2.1]  | [0.08] | [3.2]  | [9.9]  |
| 1   | 16:0                     | [16.7] | [38.9] | [21.5] | [23.1] | [20.8] | [29.9] |
| 2   | 16:1Δ7c                  | [0.4]  | [0.0]  | [0.05] | [0.08] | [0.0]  | [0.0]  |
| 3   | 16:2Δ7c,10c              | [3.9]  | [1.7]  | [0.2]  | [0.1]  | [0.3]  | [0.3]  |
| 4   | 18:0                     | [3.9]  | [1]    | [0.6]  | [2]    | [0.4]  | [0.2]  |
| 5   | 16:3Δ7c,10c,13c          | [1.1]  | [3]    | [0.0]  | [0.0]  | [0.0]  | [0.0]  |
| 6   | 18:1Δ9c                  | [45.9] | [22.9] | [8.5]  | [8.8]  | [6.8]  | [1.3]  |
| 7   | 18:2Δ9c,12c              | [18.3] | [24.8] | [1.8]  | [4.6]  | [2.3]  | [0.2]  |
| 8   | 18:3Δ9c,12c,15c          | [7]    | [6.5]  | [0.2]  | [1.8]  | [0.0]  | [0.0]  |
| 9   | 20:1Δ11c                 | [1]    | [0.0]  | [0.0]  | [0.0]  | [0.0]  | [0.0]  |
| 10  | 16:1Δ9c                  | [0.0]  | [0.0]  | [55.5] | [50.7] | [60.3] | [51]   |
| 11  | 20:4Δ5c,8c,11c,14c       | [0.0]  | [0.0]  | [1.4]  | [1.1]  | [0.6]  | [0.6]  |
| 12  | 20:5Δ5c,8c,11c,14c,17c   | [0.0]  | [0.0]  | [6.7]  | [5.6]  | [3.4]  | [3.6]  |
"

# 1.1 Читаем текст. ВАЖНО: comment.char = "" запрещает R удалять строку из-за символа #
df_raw <- read.table(text = raw_data, sep = "|", strip.white = TRUE, 
                     stringsAsFactors = FALSE, quote = "", fill = TRUE, comment.char = "")

# 1.2 Находим все строки, в которых есть хотя бы одна скобка '[' (это строки с данными)
data_rows_idx <- apply(df_raw, 1, function(x) any(grepl("\\[", x)))

if (sum(data_rows_idx) == 0) {
  stop("Ошибка: В таблице не найдено ни одной строки с квадратными скобками '['.")
}

df_data <- df_raw[data_rows_idx, , drop = FALSE]

# 1.3 Находим столбцы, в которых содержатся данные (есть скобки)
is_group_col <- sapply(df_data, function(x) any(grepl("\\[", x)))

# 1.4 Ищем шапку таблицы. Это первая строка, где нет скобок '[' и нет разделителей '---'
header_row_idx <- which(!data_rows_idx & !apply(df_raw, 1, function(x) any(grepl("---", x))))[1]

# Извлекаем названия групп
group_names <- as.character(df_raw[header_row_idx, is_group_col])
group_names <- trimws(group_names)

# 1.5 Названия жирных кислот (TAG) всегда находятся в столбце прямо перед первой группой
first_group_idx <- which(is_group_col)[1]
tag_col_idx <- first_group_idx - 1
tags <- trimws(as.character(df_data[, tag_col_idx]))

# 1.6 Оставляем только столбцы с группами и переименовываем их
df_groups <- df_data[, is_group_col, drop = FALSE]
colnames(df_groups) <- group_names

# 1.7 Подготовка списков для сбора данных
mat_list <- list()          
group_factor <- c()         
rownames_list <- c()        

# 1.8 Цикл по всем найденным группам
for (g in group_names) {
  # Убираем квадратные скобки из чисел
  clean_vals <- gsub("\\[|\\]", "", df_groups[[g]])
  
  # Разбиваем по запятой
  split_vals <- strsplit(clean_vals, ",\\s*")
  
  # Превращаем в числа
  num_list <- lapply(split_vals, as.numeric)
  
  # Находим максимальное количество повторностей в этой группе
  max_reps <- max(lengths(num_list))
  
  # Если где-то стоит просто 0.0, дублируем его до нужного количества повторностей
  num_list <- lapply(num_list, function(x) {
    if(length(x) == 1 && max_reps > 1) rep(x, max_reps) else x
  })
  
  # Превращаем в числовую матрицу
  num_mat <- do.call(rbind, num_list)
  
  # Транспонируем (строки - повторности, столбцы - TAG)
  t_mat <- t(num_mat)
  
  # Сохраняем матрицу в список
  mat_list[[g]] <- t_mat
  
  # Генерируем метки для статистики
  group_factor <- c(group_factor, rep(g, max_reps))
  rownames_list <- c(rownames_list, paste0(g, "_Rep", 1:max_reps))
}

# 1.9 Объединяем все группы в одну итоговую матрицу
m_abund <- do.call(rbind, mat_list)
colnames(m_abund) <- tags
rownames(m_abund) <- rownames_list

# Сохраняем готовый CSV файл на диск
mydata_export <- data.frame(Sample = rownames(m_abund), Group = group_factor, m_abund, check.names = FALSE)
write.csv(mydata_export, "data.csv", row.names = FALSE)

cat(sprintf("Файл data.csv успешно создан! Найдено групп: %d, всего образцов: %d\n\n", length(group_names), length(group_factor)))
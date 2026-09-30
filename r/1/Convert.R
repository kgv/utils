# library(tidyverse)
library(vegan)
library(indicspecies)

# =====================================================================
# ШАГ 1: ПРЕОБРАЗОВАНИЕ ДАННЫХ И СОЗДАНИЕ CSV
# =====================================================================

raw_data <- "
| #   | FA                     | C-70             | H-150  | H-1564           |
| --- | ---------------------- | ---------------- | ------ | ---------------- |
| 0   | 14:0                   | [3,2.9,2.8]      | [3.6]  | [1.5,1.5,1.7]    |
| 1   | 16:0                   | [24.1,24.5,24.3] | [22.3] | [25.3,27.1,26.2] |
| 2   | 16:1Δ9c                | [32.9,34.2,34.3] | [43.8] | [53.2,52.8,51.9] |
| 5   | 18:1Δ9c                | [7.6,6.9,6.9]    | [0.4]  | [5.7,5.6,6.2]    |
| 6   | 18:2Δ9c,12c            | [6,5.5,5.6]      | [0.8]  | [1.8,1.7,2]      |
| 7   | 20:4Δ5c,8c,11c,14c     | [6,6.1,6.2]      | [5.6]  | [1.7,1.5,1.6]    |
| 8   | 20:5Δ5c,8c,11c,14c,17c | [14.1,14.8,14.8] | [14.1] | [6.7,6.1,6.4]    |
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
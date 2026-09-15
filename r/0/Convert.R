library(vegan)
library(indicspecies)

# =====================================================================
# ШАГ 1: ПРЕОБРАЗОВАНИЕ ДАННЫХ И СОЗДАНИЕ CSV (СУПЕР-НАДЕЖНАЯ ВЕРСИЯ)
# =====================================================================

# Вставьте вашу таблицу между кавычками (все 99 строк)
raw_data <- "
| #   | Triacylglycerol                                        | C-108, % | C-1210, % | C-70, %   | H-242, % | H-1564, % | H-150, %  |
| --- | ------------------------------------------------------ | -------- | --------- | --------- | -------- | --------- | --------- |
| 1   | [Oleic/2;Linoleic;Oleic/2]                             | [11.4]   | [0.9]     | [0.05]    | [0.03]   | [0.02]    | [0]       |
| 2   | [Oleic/2;Linoleic;Palmitic/2]                          | [8.8]    | [6.5]     | [0.02]    | [0.03]   | [0.08]    | [0]       |
| 3   | [Oleic/2;Oleic;Oleic/2]                                | [7.7]    | [0.9]     | [0.04]    | [0.03]   | [0.03]    | [0]       |
| 4   | [Oleic/2;Oleic;Palmitic/2]                             | [6]      | [6.3]     | [0.01]    | [0.03]   | [0.1]     | [0]       |
| 5   | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]       | [4.3]    | [0.1]     | [0.0009]  | [0.003]  | [0.002]   | [0.0002]  |
| 6   | [Linoleic/2;Linoleic;Oleic/2]                          | [3.4]    | [2.1]     | [0.006]   | [0.03]   | [0.008]   | [0]       |
| 7   | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [3.3]    | [1]       | [0.0003]  | [0.003]  | [0.01]    | [0.007]   |
| 8   | [Oleic/2;Linoleic;α-Linolenic/2]                       | [3]      | [1]       | [0]       | [0.01]   | [0]       | [0]       |
| 9   | [Oleic/2;Linoleic;Stearic/2]                           | [2.3]    | [0.2]     | [0]       | [0.01]   | [0.003]   | [0]       |
| 10  | [Linoleic/2;Oleic;Oleic/2]                             | [2.3]    | [2]       | [0.006]   | [0.03]   | [0.02]    | [0]       |
| 11  | [Oleic/2;Palmitic;Oleic/2]                             | [2.1]    | [0.07]    | [0.7]     | [0.8]    | [0.1]     | [0.001]   |
| 12  | [Oleic/2;Oleic;α-Linolenic/2]                          | [2.1]    | [0.9]     | [0]       | [0.01]   | [0]       | [0]       |
| 13  | [Oleic/2;α-Linolenic;Oleic/2]                          | [1.9]    | [0.07]    | [0.01]    | [0.01]   | [0]       | [0]       |
| 14  | [Palmitic/2;Linoleic;Palmitic/2]                       | [1.7]    | [11.7]    | [0.001]   | [0.007]  | [0.09]    | [0]       |
| 15  | [Oleic/2;Palmitic;Palmitic/2]                          | [1.6]    | [0.5]     | [0.3]     | [0.8]    | [0.6]     | [0.05]    |
| 16  | [Oleic/2;Oleic;Stearic/2]                              | [1.6]    | [0.2]     | [0]       | [0.01]   | [0.005]   | [0]       |
| 17  | [Oleic/2;Roughanic;Oleic/2]                            | [1.6]    | [0.3]     | [0]       | [0]      | [0]       | [0]       |
| 18  | [Oleic/2;α-Linolenic;Palmitic/2]                       | [1.4]    | [0.5]     | [0.005]   | [0.01]   | [0]       | [0]       |
| 19  | [Linoleic/2;Linoleic;Palmitic/2]                       | [1.3]    | [7.5]     | [0.001]   | [0.01]   | [0.02]    | [0]       |
| 20  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]    | [1.3]    | [0.3]     | [0.0001]  | [0.003]  | [0.001]   | [0.00004] |
| 21  | [Oleic/2;Roughanic;Palmitic/2]                         | [1.2]    | [2.3]     | [0]       | [0]      | [0]       | [0]       |
| 22  | [Palmitic/2;Oleic;Palmitic/2]                          | [1.2]    | [11.3]    | [0.001]   | [0.008]  | [0.2]     | [0]       |
| 23  | [Palmitic/2;Linoleic;α-Linolenic/2]                    | [1.2]    | [3.4]     | [0]       | [0.006]  | [0]       | [0]       |
| 24  | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2] | [1.1]    | [0.2]     | [0]       | [0.001]  | [0]       | [0]       |
| 25  | [Linoleic/2;Oleic;Palmitic/2]                          | [0.9]    | [7.2]     | [0.001]   | [0.02]   | [0.04]    | [0]       |
| 26  | [Palmitic/2;Oleic;α-Linolenic/2]                       | [0.8]    | [3.3]     | [0]       | [0.006]  | [0]       | [0]       |
| 27  | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2] | [0.6]    | [1.9]     | [0.00003] | [0.0006] | [0.01]    | [0.08]    |
| 28  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2] | [0.5]    | [1.2]     | [0.00002] | [0.001]  | [0.003]   | [0.0009]  |
| 29  | [Linoleic/2;Linoleic;α-Linolenic/2]                    | [0.4]    | [1.1]     | [0]       | [0.006]  | [0]       | [0]       |
| 30  | [Linoleic/2;Oleic;α-Linolenic/2]                       | [0.3]    | [1.1]     | [0]       | [0.006]  | [0]       | [0]       |
| 31  | [Linoleic/2;Linoleic;Linoleic/2]                       | [0.3]    | [1.2]     | [0.0002]  | [0.007]  | [0.001]   | [0]       |
| 32  | [Palmitic/2;Roughanic;Palmitic/2]                      | [0.2]    | [4]       | [0]       | [0]      | [0]       | [0]       |
| 33  | [Linoleic/2;Roughanic;Palmitic/2]                      | [0.2]    | [2.6]     | [0]       | [0]      | [0]       | [0]       |
| 34  | [Linoleic/2;Oleic;Linoleic/2]                          | [0.2]    | [1.2]     | [0.0002]  | [0.008]  | [0.002]   | [0]       |
| 35  | [Palmitic/2;Roughanic;α-Linolenic/2]                   | [0.2]    | [1.2]     | [0]       | [0]      | [0]       | [0]       |
| 36  | [Palmitoleic/2;Stearic;Palmitoleic/2]                  | [0]      | [0]       | [1.3]     | [0.6]    | [0.08]    | [0]       |
| 37  | [Palmitoleic/2;Palmitoleic;Palmitoleic/2]              | [0]      | [0]       | [11.8]    | [10.8]   | [21.5]    | [7.9]     |
| 38  | [Palmitoleic/2;Palmitic;α-Linolenic/2]                 | [0]      | [0]       | [0]       | [1.6]    | [0]       | [0]       |
| 39  | [Palmitoleic/2;Palmitic;Stearic/2]                     | [0]      | [0]       | [0]       | [1.5]    | [0.2]     | [0.005]   |
| 40  | [Palmitoleic/2;Palmitic;Palmitoleic/2]                 | [0]      | [0]       | [30.5]    | [21.4]   | [13.2]    | [0.2]     |
| 41  | [Palmitoleic/2;Oleic;Palmitoleic/2]                    | [0]      | [0]       | [1.7]     | [0.9]    | [3]       | [0]       |
| 42  | [Palmitoleic/2;Myristic;Palmitoleic/2]                 | [0]      | [0]       | [1.4]     | [1]      | [1.5]     | [0]       |
| 43  | [Palmitoleic/2;Linoleic;Palmitoleic/2]                 | [0]      | [0]       | [1.9]     | [0.8]    | [1.5]     | [0]       |
| 44  | [Palmitic/2;Palmitoleic;Palmitoleic/2]                 | [0]      | [0]       | [0.6]     | [2]      | [10.3]    | [23.8]    |
| 45  | [Palmitic/2;Palmitoleic;Palmitic/2]                    | [0]      | [0]       | [0.009]   | [0.09]   | [1.2]     | [17.9]    |
| 46  | [Palmitic/2;Palmitic;Palmitoleic/2]                    | [0]      | [0]       | [1.7]     | [3.9]    | [6.4]     | [0.7]     |
| 47  | [Palmitic/2;Oleic;Palmitoleic/2]                       | [0]      | [0]       | [0.1]     | [0.2]    | [1.5]     | [0]       |
| 48  | [Oleic/2;Palmitoleic;Palmitoleic/2]                    | [0]      | [0]       | [3.6]     | [4.2]    | [4.4]     | [1.1]     |
| 49  | [Oleic/2;Palmitoleic;Palmitic/2]                       | [0]      | [0]       | [0.1]     | [0.4]    | [1.1]     | [1.6]     |
| 50  | [Oleic/2;Palmitic;Palmitoleic/2]                       | [0]      | [0]       | [9.4]     | [8.3]    | [2.7]     | [0.03]    |
| 51  | [Myristic/2;Palmitoleic;Palmitoleic/2]                 | [0]      | [0]       | [0.6]     | [0]      | [2]       | [8.2]     |
| 52  | [Myristic/2;Palmitoleic;Palmitic/2]                    | [0]      | [0]       | [0.02]    | [0]      | [0.5]     | [12.3]    |
| 53  | [Myristic/2;Palmitoleic;Myristic/2]                    | [0]      | [0]       | [0.007]   | [0]      | [0.05]    | [2.1]     |
| 54  | [Myristic/2;Palmitic;Palmitoleic/2]                    | [0]      | [0]       | [1.5]     | [0]      | [1.2]     | [0.3]     |
| 55  | [Linoleic/2;Palmitoleic;Palmitoleic/2]                 | [0]      | [0]       | [0.3]     | [2]      | [1.1]     | [0.1]     |
| 56  | [Linoleic/2;Palmitic;Palmitoleic/2]                    | [0]      | [0]       | [0.7]     | [4]      | [0.7]     | [0.004]   |
| 57  | [Eicosapentaenoic/2;Palmitoleic;Palmitoleic/2]         | [0]      | [0]       | [3.1]     | [2.6]    | [3.1]     | [2.8]     |
| 58  | [Eicosapentaenoic/2;Palmitoleic;Palmitic/2]            | [0]      | [0]       | [0.09]    | [0.2]    | [0.7]     | [4.1]     |
| 59  | [Eicosapentaenoic/2;Palmitoleic;Myristic/2]            | [0]      | [0]       | [0.08]    | [0]      | [0.1]     | [1.4]     |
| 60  | [Eicosapentaenoic/2;Palmitic;Palmitoleic/2]            | [0]      | [0]       | [8]       | [5.2]    | [1.9]     | [0.08]    |
| 61  | [Eicosapentaenoic/2;Palmitic;Oleic/2]                  | [0]      | [0]       | [1.2]     | [1]      | [0.2]     | [0.006]   |
| 62  | [Arachidonic/2;Palmitic;Palmitoleic/2]                 | [0]      | [0]       | [1.7]     | [1.1]    | [0.3]     | [0.02]    |
"

# 1. Разбиваем текст на отдельные строки
lines <- strsplit(trimws(raw_data), "\n")[[1]]
lines <- trimws(lines)
lines <- lines[lines != ""] # Убираем пустые строки

# 2. Убираем строку-разделитель Markdown (вида |---|---|)
lines <- lines[!grepl("-{2,}", lines)]

if (length(lines) < 2) {
  stop("Ошибка: Не найдено данных. Проверьте, что скопировали таблицу целиком.")
}

# 3. Функция для аккуратного парсинга одной строки Markdown-таблицы
parse_line <- function(line) {
  line <- sub("^\\|", "", line) # Убираем первый |
  line <- sub("\\|$", "", line) # Убираем последний |
  cells <- strsplit(line, "\\|")[[1]]
  trimws(cells)
}

# 4. Парсим все строки и превращаем в таблицу (data.frame)
parsed_list <- lapply(lines, parse_line)
df_raw <- as.data.frame(do.call(rbind, parsed_list), stringsAsFactors = FALSE)

# 5. Первая строка - это шапка
raw_headers <- as.character(df_raw[1, ])
df_raw <- df_raw[-1, , drop = FALSE]

# 6. Ищем колонку с названиями липидов (Triacylglycerol или TAG)
tag_col_idx <- grep("Triacylglycerol|TAG", raw_headers, ignore.case = TRUE)[1]

# Если колонка не нашлась по имени, ищем первую колонку, где есть текст (а не только цифры 1, 2, 3...)
if (is.na(tag_col_idx)) {
  is_numeric_col <- grepl("^[0-9]+$", trimws(df_raw[, 1]))
  if (all(is_numeric_col)) {
    tag_col_idx <- 2
  } else {
    tag_col_idx <- 1
  }
}

# 7. Названия групп - все столбцы правее колонки TAG
group_names <- raw_headers[(tag_col_idx + 1):ncol(df_raw)]
group_names <- gsub(",\\s*%", "", group_names) # Очищаем от ", %"
group_names <- trimws(group_names)

# 8. Оставляем только нужные колонки (TAG и сами данные)
df_raw <- df_raw[, c(tag_col_idx, (tag_col_idx + 1):ncol(df_raw)), drop = FALSE]
colnames(df_raw) <- c("TAG", group_names)

# 9. Подготовка списков для сбора данных
mat_list <- list()          
group_factor <- c()         
rownames_list <- c()        

# 10. Цикл по всем найденным группам
for (g in group_names) {
  # Убираем квадратные скобки из чисел
  clean_vals <- gsub("\\[|\\]", "", df_raw[[g]])
  clean_vals[clean_vals == "" | is.na(clean_vals)] <- "0" # Защита от пустых ячеек
  
  # Разбиваем по запятой (если есть повторности)
  split_vals <- strsplit(clean_vals, ",\\s*")
  
  # Превращаем в числовую матрицу
  num_mat <- do.call(rbind, lapply(split_vals, function(x) {
    if (length(x) == 0) return(0)
    val <- suppressWarnings(as.numeric(x))
    val[is.na(val)] <- 0
    return(val)
  }))
  
  # Транспонируем (строки - образцы, столбцы - TAG)
  t_mat <- t(num_mat)
  mat_list[[g]] <- t_mat
  
  n_reps <- nrow(t_mat)
  group_factor <- c(group_factor, rep(g, n_reps))
  rownames_list <- c(rownames_list, paste0(g, "_Rep", 1:n_reps))
}

# 11. Объединяем все группы в одну итоговую матрицу
m_abund <- do.call(rbind, mat_list)
colnames(m_abund) <- df_raw$TAG
rownames(m_abund) <- rownames_list

# Сохраняем готовый CSV файл на диск
mydata_export <- data.frame(Sample = rownames(m_abund), Group = group_factor, m_abund, check.names = FALSE)
write.csv(mydata_export, "data.csv", row.names = FALSE)

cat(sprintf("Файл data.csv успешно создан! Найдено групп: %d, всего образцов: %d\n", length(group_names), length(group_factor)))
cat("Названия групп:", paste(group_names, collapse = ", "), "\n\n")
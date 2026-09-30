# library(tidyverse)
library(vegan)
library(indicspecies)

# =====================================================================
# ШАГ 1: ПРЕОБРАЗОВАНИЕ ДАННЫХ И СОЗДАНИЕ CSV
# =====================================================================

# Вставьте вашу таблицу между кавычками (здесь показан фрагмент, 
# вы можете вставить все 99 строк прямо сюда)
raw_data <- "
| #   | Triacylglycerol                                        | C-108, %         | C-1210, %          | C-70, %   | H-242, % | H-1564, % | H-150, %  |
| --- | ------------------------------------------------------ | ---------------- | ------------------ | --------- | -------- | --------- | --------- |
| 1   | [Oleic/2;Linoleic;Oleic/2]                             | [12, 11.7, 10.4] | [0.9, 0.9, 1]      | [0.05]    | [0.03]   | [0.02]    | [0]       |
| 2   | [Oleic/2;Linoleic;Palmitic/2]                          | [8.9, 8.8, 8.6]  | [6.5, 6.4, 6.7]    | [0.02]    | [0.03]   | [0.08]    | [0]       |
| 3   | [Oleic/2;Oleic;Oleic/2]                                | [7.3, 7.6, 8.3]  | [0.8, 0.9, 1]      | [0.04]    | [0.03]   | [0.03]    | [0]       |
| 4   | [Oleic/2;Oleic;Palmitic/2]                             | [5.4, 5.7, 6.9]  | [5.7, 6.6, 6.7]    | [0.01]    | [0.03]   | [0.1]     | [0]       |
| 5   | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]       | [5, 4.7, 3.1]    | [0.2, 0.1, 0.1]    | [0.0009]  | [0.003]  | [0.002]   | [0.0002]  |
| 6   | [Linoleic/2;Linoleic;Oleic/2]                          | [3.4, 3.2, 3.4]  | [2.2, 1.9, 2.1]    | [0.006]   | [0.03]   | [0.008]   | [0]       |
| 7   | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [3.7, 3.6, 2.6]  | [1.1, 1.1, 1]      | [0.0003]  | [0.003]  | [0.01]    | [0.007]   |
| 8   | [Oleic/2;Linoleic;α-Linolenic/2]                       | [3.1, 2.9, 3]    | [1.1, 0.9, 1]      | [0]       | [0.01]   | [0]       | [0]       |
| 9   | [Oleic/2;Linoleic;Stearic/2]                           | [2.3, 2.4, 2.3]  | [0.2, 0.1, 0.2]    | [0]       | [0.01]   | [0.003]   | [0]       |
| 10  | [Linoleic/2;Oleic;Oleic/2]                             | [2.1, 2.1, 2.8]  | [2, 2, 2.1]        | [0.006]   | [0.03]   | [0.02]    | [0]       |
| 11  | [Oleic/2;Palmitic;Oleic/2]                             | [2.5, 2.4, 1.6]  | [0.06, 0.06, 0.08] | [0.7]     | [0.8]    | [0.1]     | [0.001]   |
| 12  | [Oleic/2;Oleic;α-Linolenic/2]                          | [1.9, 1.9, 2.4]  | [0.9, 0.9, 1]      | [0]       | [0.01]   | [0]       | [0]       |
| 13  | [Oleic/2;α-Linolenic;Oleic/2]                          | [2.1, 2.1, 1.4]  | [0.08, 0.07, 0.07] | [0.01]    | [0.01]   | [0]       | [0]       |
| 14  | [Palmitic/2;Linoleic;Palmitic/2]                       | [1.6, 1.7, 1.8]  | [11.4, 12, 11.7]   | [0.001]   | [0.007]  | [0.09]    | [0]       |
| 15  | [Oleic/2;Palmitic;Palmitic/2]                          | [1.8, 1.8, 1.3]  | [0.4, 0.5, 0.6]    | [0.3]     | [0.8]    | [0.6]     | [0.05]    |
| 16  | [Oleic/2;Oleic;Stearic/2]                              | [1.4, 1.6, 1.8]  | [0.1, 0.1, 0.2]    | [0]       | [0.01]   | [0.005]   | [0]       |
| 17  | [Oleic/2;Roughanic;Oleic/2]                            | [1.3, 1.3, 2.1]  | [0.4, 0.3, 0.3]    | [0]       | [0]      | [0]       | [0]       |
| 18  | [Oleic/2;α-Linolenic;Palmitic/2]                       | [1.5, 1.6, 1.2]  | [0.6, 0.5, 0.5]    | [0.005]   | [0.01]   | [0]       | [0]       |
| 19  | [Linoleic/2;Linoleic;Palmitic/2]                       | [1.3, 1.2, 1.4]  | [7.8, 7.3, 7.4]    | [0.001]   | [0.01]   | [0.02]    | [0]       |
| 20  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]    | [1.4, 1.3, 1]    | [0.4, 0.3, 0.3]    | [0.0001]  | [0.003]  | [0.001]   | [0.00004] |
| 21  | [Oleic/2;Roughanic;Palmitic/2]                         | [0.9, 1, 1.7]    | [2.5, 2.2, 2.1]    | [0]       | [0]      | [0]       | [0]       |
| 22  | [Palmitic/2;Oleic;Palmitic/2]                          | [1, 1.1, 1.4]    | [10, 12.3, 11.6]   | [0.001]   | [0.008]  | [0.2]     | [0]       |
| 23  | [Palmitic/2;Linoleic;α-Linolenic/2]                    | [1.2, 1.1, 1.2]  | [3.7, 3.3, 3.3]    | [0]       | [0.006]  | [0]       | [0]       |
| 24  | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2] | [1.3, 1.2, 0.9]  | [0.2, 0.1, 0.1]    | [0]       | [0.001]  | [0]       | [0]       |
| 25  | [Linoleic/2;Oleic;Palmitic/2]                          | [0.8, 0.8, 1.1]  | [6.8, 7.5, 7.4]    | [0.001]   | [0.02]   | [0.04]    | [0]       |
| 26  | [Palmitic/2;Oleic;α-Linolenic/2]                       | [0.7, 0.7, 1]    | [3.2, 3.4, 3.3]    | [0]       | [0.006]  | [0]       | [0]       |
| 27  | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2] | [0.7, 0.7, 0.5]  | [1.9, 2, 1.7]      | [0.00003] | [0.0006] | [0.01]    | [0.08]    |
| 28  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2] | [0.5, 0.5, 0.4]  | [1.3, 1.2, 1.1]    | [0.00002] | [0.001]  | [0.003]   | [0.0009]  |
| 29  | [Linoleic/2;Linoleic;α-Linolenic/2]                    | [0.4, 0.4, 0.5]  | [1.3, 1, 1.1]      | [0]       | [0.006]  | [0]       | [0]       |
| 30  | [Linoleic/2;Oleic;α-Linolenic/2]                       | [0.3, 0.3, 0.4]  | [1.1, 1, 1]        | [0]       | [0.006]  | [0]       | [0]       |
| 31  | [Linoleic/2;Linoleic;Linoleic/2]                       | [0.2, 0.2, 0.3]  | [1.3, 1.1, 1.2]    | [0.0002]  | [0.007]  | [0.001]   | [0]       |
| 32  | [Palmitic/2;Roughanic;Palmitic/2]                      | [0.2, 0.2, 0.4]  | [4.4, 4.1, 3.6]    | [0]       | [0]      | [0]       | [0]       |
| 33  | [Linoleic/2;Roughanic;Palmitic/2]                      | [0.1, 0.1, 0.3]  | [3, 2.5, 2.3]      | [0]       | [0]      | [0]       | [0]       |
| 34  | [Linoleic/2;Oleic;Linoleic/2]                          | [0.1, 0.1, 0.2]  | [1.2, 1.1, 1.2]    | [0.0002]  | [0.008]  | [0.002]   | [0]       |
| 35  | [Palmitic/2;Roughanic;α-Linolenic/2]                   | [0.1, 0.1, 0.3]  | [1.4, 1.1, 1]      | [0]       | [0]      | [0]       | [0]       |
| 36  | [Palmitoleic/2;Stearic;Palmitoleic/2]                  | [0, 0, 0]        | [0, 0, 0]          | [1.3]     | [0.6]    | [0.08]    | [0]       |
| 37  | [Palmitoleic/2;Palmitoleic;Palmitoleic/2]              | [0, 0, 0]        | [0, 0, 0]          | [11.8]    | [10.8]   | [21.5]    | [7.9]     |
| 38  | [Palmitoleic/2;Palmitic;α-Linolenic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [0]       | [1.6]    | [0]       | [0]       |
| 39  | [Palmitoleic/2;Palmitic;Stearic/2]                     | [0, 0, 0]        | [0, 0, 0]          | [0]       | [1.5]    | [0.2]     | [0.005]   |
| 40  | [Palmitoleic/2;Palmitic;Palmitoleic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [30.5]    | [21.4]   | [13.2]    | [0.2]     |
| 41  | [Palmitoleic/2;Oleic;Palmitoleic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [1.7]     | [0.9]    | [3]       | [0]       |
| 42  | [Palmitoleic/2;Myristic;Palmitoleic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [1.4]     | [1]      | [1.5]     | [0]       |
| 43  | [Palmitoleic/2;Linoleic;Palmitoleic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [1.9]     | [0.8]    | [1.5]     | [0]       |
| 44  | [Palmitic/2;Palmitoleic;Palmitoleic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [0.6]     | [2]      | [10.3]    | [23.8]    |
| 45  | [Palmitic/2;Palmitoleic;Palmitic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [0.009]   | [0.09]   | [1.2]     | [17.9]    |
| 46  | [Palmitic/2;Palmitic;Palmitoleic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [1.7]     | [3.9]    | [6.4]     | [0.7]     |
| 47  | [Palmitic/2;Oleic;Palmitoleic/2]                       | [0, 0, 0]        | [0, 0, 0]          | [0.1]     | [0.2]    | [1.5]     | [0]       |
| 48  | [Oleic/2;Palmitoleic;Palmitoleic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [3.6]     | [4.2]    | [4.4]     | [1.1]     |
| 49  | [Oleic/2;Palmitoleic;Palmitic/2]                       | [0, 0, 0]        | [0, 0, 0]          | [0.1]     | [0.4]    | [1.1]     | [1.6]     |
| 50  | [Oleic/2;Palmitic;Palmitoleic/2]                       | [0, 0, 0]        | [0, 0, 0]          | [9.4]     | [8.3]    | [2.7]     | [0.03]    |
| 51  | [Myristic/2;Palmitoleic;Palmitoleic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [0.6]     | [0]      | [2]       | [8.2]     |
| 52  | [Myristic/2;Palmitoleic;Palmitic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [0.02]    | [0]      | [0.5]     | [12.3]    |
| 53  | [Myristic/2;Palmitoleic;Myristic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [0.007]   | [0]      | [0.05]    | [2.1]     |
| 54  | [Myristic/2;Palmitic;Palmitoleic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [1.5]     | [0]      | [1.2]     | [0.3]     |
| 55  | [Linoleic/2;Palmitoleic;Palmitoleic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [0.3]     | [2]      | [1.1]     | [0.1]     |
| 56  | [Linoleic/2;Palmitic;Palmitoleic/2]                    | [0, 0, 0]        | [0, 0, 0]          | [0.7]     | [4]      | [0.7]     | [0.004]   |
| 57  | [Eicosapentaenoic/2;Palmitoleic;Palmitoleic/2]         | [0, 0, 0]        | [0, 0, 0]          | [3.1]     | [2.6]    | [3.1]     | [2.8]     |
| 58  | [Eicosapentaenoic/2;Palmitoleic;Palmitic/2]            | [0, 0, 0]        | [0, 0, 0]          | [0.09]    | [0.2]    | [0.7]     | [4.1]     |
| 59  | [Eicosapentaenoic/2;Palmitoleic;Myristic/2]            | [0, 0, 0]        | [0, 0, 0]          | [0.08]    | [0]      | [0.1]     | [1.4]     |
| 60  | [Eicosapentaenoic/2;Palmitic;Palmitoleic/2]            | [0, 0, 0]        | [0, 0, 0]          | [8]       | [5.2]    | [1.9]     | [0.08]    |
| 61  | [Eicosapentaenoic/2;Palmitic;Oleic/2]                  | [0, 0, 0]        | [0, 0, 0]          | [1.2]     | [1]      | [0.2]     | [0.006]   |
| 62  | [Arachidonic/2;Palmitic;Palmitoleic/2]                 | [0, 0, 0]        | [0, 0, 0]          | [1.7]     | [1.1]    | [0.3]     | [0.02]    |
"

# 1.1 Читаем текст как таблицу (fill = TRUE спасает от неровных строк)
df_raw <- read.table(text = raw_data, sep = "|", strip.white = TRUE, 
                     stringsAsFactors = FALSE, quote = "", fill = TRUE)

# 1.2 Безопасное удаление пустых столбцов (возникают из-за символов | по краям)
# Оставляем только те столбцы, которые не состоят целиком из пустот или NA
is_not_empty <- sapply(df_raw, function(x) !all(is.na(x) | trimws(x) == ""))
df_raw <- df_raw[, is_not_empty, drop = FALSE]

# 1.3 Отсекаем шапку таблицы и разделители Markdown (если они были скопированы)
# Мы точно знаем, что настоящие данные содержат скобку "[" во 2-м столбце (названия TAG)
df_raw <- df_raw[grepl("\\[", df_raw[, 2]), , drop = FALSE]

# 1.4 Теперь 1-й столбец - это порядковый номер (1, 2, 3...), смело удаляем его
df_raw <- df_raw[, -1, drop = FALSE]

# 1.5 Динамическое переименование столбцов
# 1-й оставшийся столбец - это TAG, все остальные - это группы (Value)
num_groups <- ncol(df_raw) - 1
group_names <- paste0("Group", 0:(num_groups - 1))
colnames(df_raw) <- c("TAG", group_names)

# 1.6 Подготовка списков для сбора данных
mat_list <- list()          
group_factor <- c()         
rownames_list <- c()        

# 1.7 Цикл по всем найденным группам
for (g in group_names) {
  # Убираем квадратные скобки из чисел
  clean_vals <- gsub("\\[|\\]", "", df_raw[[g]])
  
  # Разбиваем по запятой
  split_vals <- strsplit(clean_vals, ",\\s*")
  
  # Превращаем в числовую матрицу (строки - TAG, столбцы - повторности)
  num_mat <- do.call(rbind, lapply(split_vals, as.numeric))
  
  # Транспонируем (строки - повторности, столбцы - TAG)
  t_mat <- t(num_mat)
  
  # Сохраняем матрицу в список
  mat_list[[g]] <- t_mat
  
  # Определяем, сколько повторностей было в этой группе
  n_reps <- nrow(t_mat)
  
  # Генерируем метки для статистики
  group_factor <- c(group_factor, rep(g, n_reps))
  rownames_list <- c(rownames_list, paste0(g, "_Rep", 1:n_reps))
}

# 1.8 Объединяем все группы в одну итоговую матрицу
m_abund <- do.call(rbind, mat_list)
colnames(m_abund) <- df_raw$TAG
rownames(m_abund) <- rownames_list

# (Опционально) Сохраняем готовый CSV файл на диск
mydata_export <- data.frame(Sample = rownames(m_abund), Group = group_factor, m_abund, check.names = FALSE)
write.csv(mydata_export, "data.csv", row.names = FALSE)

cat(sprintf("Файл data.csv успешно создан! Найдено групп: %d, всего образцов: %d\n\n", num_groups, length(group_factor)))
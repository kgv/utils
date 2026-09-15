# 1. Вставьте ваши данные между кавычками (здесь показано начало таблиц)
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
| 11    | [Oleic/2;Palmitic;Oleic/2]                                | [2.5, 2.4, 1.6]  |
| 12    | [Oleic/2;Oleic;α-Linolenic/2]                             | [1.9, 1.9, 2.4]  |
| 13    | [Oleic/2;α-Linolenic;Oleic/2]                             | [2.1, 2.1, 1.4]  |
| 14    | [Palmitic/2;Linoleic;Palmitic/2]                          | [1.6, 1.7, 1.8]  |
| 15    | [Oleic/2;Palmitic;Palmitic/2]                             | [1.8, 1.8, 1.3]  |
| 16    | [Oleic/2;Oleic;Stearic/2]                                 | [1.4, 1.6, 1.8]  |
| 17    | [Oleic/2;Roughanic;Oleic/2]                               | [1.3, 1.3, 2.1]  |
| 18    | [Oleic/2;α-Linolenic;Palmitic/2]                          | [1.5, 1.6, 1.2]  |
| 19    | [Linoleic/2;Linoleic;Palmitic/2]                          | [1.3, 1.2, 1.4]  |
| 20    | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]       | [1.4, 1.3, 1]    |
| 21    | [Oleic/2;Roughanic;Palmitic/2]                            | [0.9, 1, 1.7]    |
| 22    | [Palmitic/2;Oleic;Palmitic/2]                             | [1, 1.1, 1.4]    |
| 23    | [Palmitic/2;Linoleic;α-Linolenic/2]                       | [1.2, 1.1, 1.2]  |
| 24    | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2]    | [1.3, 1.2, 0.9]  |
| 25    | [Palmitic/2;Linoleic;Stearic/2]                           | [0.9, 0.9, 0.9]  |
| 26    | [Linoleic/2;Oleic;Palmitic/2]                             | [0.8, 0.8, 1.1]  |
| 27    | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Stearic/2]        | [1, 1, 0.7]      |
| 28    | [Palmitic/2;Oleic;α-Linolenic/2]                          | [0.7, 0.7, 1]    |
| 29    | [Linoleic/2;Palmitic;Oleic/2]                             | [0.7, 0.7, 0.5]  |
| 30    | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [0.7, 0.7, 0.5]  |
| 31    | [Palmitic/2;Oleic;Stearic/2]                              | [0.5, 0.6, 0.7]  |
| 32    | [Gondoic/2;Linoleic;Oleic/2]                              | [0.6, 0.6, 0.6]  |
| 33    | [Oleic/2;Palmitic;α-Linolenic/2]                          | [0.6, 0.6, 0.5]  |
| 34    | [Linoleic/2;α-Linolenic;Oleic/2]                          | [0.6, 0.6, 0.5]  |
| 35    | [Oleic/2;α-Linolenic;α-Linolenic/2]                       | [0.5, 0.5, 0.4]  |
| 36    | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [0.5, 0.5, 0.4]  |
| 37    | [Linoleic/2;Roughanic;Oleic/2]                            | [0.4, 0.4, 0.7]  |
| 38    | [Linoleic/2;Linoleic;α-Linolenic/2]                       | [0.4, 0.4, 0.5]  |
| 39    | [Oleic/2;Palmitic;Stearic/2]                              | [0.5, 0.5, 0.3]  |
| 40    | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2] | [0.5, 0.4, 0.4]  |
| 41    | [Oleic/2;Hypogeic;Oleic/2]                                | [0.5, 0.5, 0.4]  |
| 42    | [Oleic/2;Roughanic;α-Linolenic/2]                         | [0.3, 0.3, 0.6]  |
| 43    | [Gondoic/2;Oleic;Oleic/2]                                 | [0.3, 0.4, 0.5]  |
| 44    | [Oleic/2;α-Linolenic;Stearic/2]                           | [0.4, 0.4, 0.3]  |
| 45    | [Linoleic/2;Linoleic;Stearic/2]                           | [0.3, 0.3, 0.4]  |
| 46    | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Stearic/2]     | [0.4, 0.4, 0.3]  |
| 47    | [Oleic/2;Hypogeic;Palmitic/2]                             | [0.4, 0.3, 0.3]  |
| 48    | [Oleic/2;Roughanic;Stearic/2]                             | [0.2, 0.3, 0.5]  |
| 49    | [Palmitic/2;Palmitic;Palmitic/2]                          | [0.3, 0.3, 0.3]  |
| 50    | [Linoleic/2;Oleic;α-Linolenic/2]                          | [0.3, 0.3, 0.4]  |
| 51    | [Stearic/2;Linoleic;α-Linolenic/2]                        | [0.3, 0.3, 0.3]  |
| 52    | [Oleic/2;Linoleic;cis-Vaccenic/2]                         | [0.3, 0.3, 0.3]  |
| 53    | [Palmitic/2;α-Linolenic;Palmitic/2]                       | [0.3, 0.3, 0.2]  |
| 54    | [Linoleic/2;Linoleic;Linoleic/2]                          | [0.2, 0.2, 0.3]  |
| 55    | [Linoleic/2;Palmitic;Palmitic/2]                          | [0.3, 0.2, 0.2]  |
| 56    | [Palmitic/2;Roughanic;Palmitic/2]                         | [0.2, 0.2, 0.4]  |
| 57    | [Linoleic/2;Oleic;Stearic/2]                              | [0.2, 0.2, 0.3]  |
| 58    | [Gondoic/2;Linoleic;Palmitic/2]                           | [0.2, 0.2, 0.2]  |
| 59    | [Gondoic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]        | [0.2, 0.3, 0.2]  |
| 60    | [Palmitic/2;Palmitic;α-Linolenic/2]                       | [0.2, 0.2, 0.2]  |
| 61    | [Stearic/2;Oleic;α-Linolenic/2]                           | [0.2, 0.2, 0.3]  |
| 62    | [Linoleic/2;α-Linolenic;Palmitic/2]                       | [0.2, 0.2, 0.2]  |
| 63    | [Oleic/2;Linoleic;γ-Linolenic/2]                          | [0.2, 0.2, 0.2]  |
| 64    | [α-Linolenic/2;Linoleic;α-Linolenic/2]                    | [0.2, 0.2, 0.2]  |
| 65    | [Oleic/2;Oleic;cis-Vaccenic/2]                            | [0.2, 0.2, 0.2]  |
| 66    | [Palmitic/2;α-Linolenic;α-Linolenic/2]                    | [0.2, 0.2, 0.2]  |
| 67    | [Linoleic/2;Roughanic;Palmitic/2]                         | [0.1, 0.1, 0.3]  |
| 68    | [Linoleic/2;Oleic;Linoleic/2]                             | [0.1, 0.1, 0.2]  |
| 69    | [Palmitic/2;Palmitic;Stearic/2]                           | [0.2, 0.2, 0.1]  |
| 70    | [Palmitic/2;Roughanic;α-Linolenic/2]                      | [0.1, 0.1, 0.3]  |
" # <-- вставьте сюда все остальные строки C-108

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
| 11     | [Oleic/2;Roughanic;Palmitic/2]                            | [2.5, 2.2, 2.1]  |
| 12     | [Linoleic/2;Linoleic;Oleic/2]                             | [2.2, 1.9, 2.1]  |
| 13     | [Linoleic/2;Oleic;Oleic/2]                                | [2, 2, 2.1]      |
| 14     | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [1.9, 2, 1.7]    |
| 15     | [Linoleic/2;Linoleic;Linoleic/2]                          | [1.3, 1.1, 1.2]  |
| 16     | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [1.3, 1.2, 1.1]  |
| 17     | [Palmitic/2;Roughanic;α-Linolenic/2]                      | [1.4, 1.1, 1]    |
| 18     | [Linoleic/2;Oleic;Linoleic/2]                             | [1.2, 1.1, 1.2]  |
| 19     | [Linoleic/2;Linoleic;α-Linolenic/2]                       | [1.3, 1, 1.1]    |
| 20     | [Linoleic/2;Oleic;α-Linolenic/2]                          | [1.1, 1, 1]      |
| 21     | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]       | [1.1, 1.1, 1]    |
| 22     | [Oleic/2;Linoleic;α-Linolenic/2]                          | [1.1, 0.9, 1]    |
| 23     | [Oleic/2;Oleic;α-Linolenic/2]                             | [0.9, 0.9, 1]    |
| 24     | [Oleic/2;Linoleic;Oleic/2]                                | [0.9, 0.9, 1]    |
| 25     | [Palmitic/2;α-Linolenic;Palmitic/2]                       | [1, 1, 0.8]      |
| 26     | [Oleic/2;Oleic;Oleic/2]                                   | [0.8, 0.9, 1]    |
| 27     | [Palmitic/2;Palmitic;Palmitic/2]                          | [0.8, 0.9, 1]    |
| 28     | [Linoleic/2;Roughanic;Oleic/2]                            | [0.9, 0.7, 0.7]  |
| 29     | [Linoleic/2;α-Linolenic;Palmitic/2]                       | [0.7, 0.6, 0.5]  |
| 30     | [Linoleic/2;Palmitic;Palmitic/2]                          | [0.5, 0.5, 0.6]  |
| 31     | [Palmitic/2;Linoleic;Stearic/2]                           | [0.5, 0.5, 0.6]  |
| 32     | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2] | [0.6, 0.5, 0.5]  |
| 33     | [Palmitic/2;Oleic;Stearic/2]                              | [0.5, 0.5, 0.6]  |
| 34     | [Oleic/2;α-Linolenic;Palmitic/2]                          | [0.6, 0.5, 0.5]  |
| 35     | [Oleic/2;Palmitic;Palmitic/2]                             | [0.4, 0.5, 0.6]  |
| 36     | [Palmitic/2;Linoleic;cis-Vaccenic/2]                      | [0.5, 0.5, 0.5]  |
| 37     | [Palmitic/2;Oleic;cis-Vaccenic/2]                         | [0.4, 0.5, 0.5]  |
| 38     | [Linoleic/2;Roughanic;Linoleic/2]                         | [0.5, 0.4, 0.4]  |
| 39     | [Linoleic/2;Roughanic;α-Linolenic/2]                      | [0.5, 0.3, 0.3]  |
| 40     | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]       | [0.4, 0.3, 0.3]  |
| 41     | [Oleic/2;Roughanic;α-Linolenic/2]                         | [0.4, 0.3, 0.3]  |
| 42     | [Oleic/2;Roughanic;Oleic/2]                               | [0.4, 0.3, 0.3]  |
| 43     | [Palmitic/2;α-Linolenic;α-Linolenic/2]                    | [0.3, 0.3, 0.2]  |
| 44     | [Palmitic/2;Palmitic;α-Linolenic/2]                       | [0.2, 0.2, 0.3]  |
| 45     | [α-Linolenic/2;Linoleic;α-Linolenic/2]                    | [0.3, 0.2, 0.2]  |
| 46     | [α-Linolenic/2;Oleic;α-Linolenic/2]                       | [0.3, 0.2, 0.2]  |
| 47     | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Linoleic/2]    | [0.2, 0.2, 0.2]  |
| 48     | [Palmitic/2;Roughanic;Stearic/2]                          | [0.2, 0.2, 0.2]  |
| 49     | [Linoleic/2;Linoleic;Stearic/2]                           | [0.2, 0.2, 0.2]  |
| 50     | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2] | [0.2, 0.2, 0.1]  |
| 51     | [Linoleic/2;Oleic;Stearic/2]                              | [0.2, 0.2, 0.2]  |
| 52     | [Palmitic/2;Roughanic;cis-Vaccenic/2]                     | [0.2, 0.2, 0.2]  |
| 53     | [Linoleic/2;α-Linolenic;Oleic/2]                          | [0.2, 0.2, 0.2]  |
| 54     | [Linoleic/2;Palmitic;Oleic/2]                             | [0.1, 0.1, 0.2]  |
| 55     | [Oleic/2;Linoleic;Stearic/2]                              | [0.2, 0.1, 0.2]  |
| 56     | [Linoleic/2;Linoleic;cis-Vaccenic/2]                      | [0.2, 0.1, 0.2]  |
| 57     | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2]    | [0.2, 0.1, 0.1]  |
| 58     | [Oleic/2;Oleic;Stearic/2]                                 | [0.1, 0.1, 0.2]  |
| 59     | [Linoleic/2;Oleic;cis-Vaccenic/2]                         | [0.1, 0.1, 0.2]  |
| 60     | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]          | [0.2, 0.1, 0.1]  |
| 61     | [Oleic/2;Linoleic;cis-Vaccenic/2]                         | [0.1, 0.1, 0.1]  |
| 62     | [Oleic/2;Oleic;cis-Vaccenic/2]                            | [0.1, 0.1, 0.1]  |
| 63     | [Palmitic/2;Stearic;Palmitic/2]                           | [0.1, 0.1, 0.2]  |
| 64     | [Lignoceric/2;Linoleic;Palmitic/2]                        | [0.1, 0.1, 0.1]  |
| 65     | [Lignoceric/2;Oleic;Palmitic/2]                           | [0.1, 0.1, 0.1]  |
| 66     | [Linoleic/2;α-Linolenic;Linoleic/2]                       | [0.1, 0.1, 0.1]  |
| 67     | [Linoleic/2;Palmitic;Linoleic/2]                          | [0.1, 0.1, 0.1]  |
| 68     | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Stearic/2]     | [0.1, 0.1, 0.1]  |
| 69     | [α-Linolenic/2;Roughanic;α-Linolenic/2]                   | [0.1, 0.1, 0.1]  |
| 70     | [Linoleic/2;α-Linolenic;α-Linolenic/2]                    | [0.1, 0.1, 0.1]  |
" # <-- вставьте сюда все остальные строки C-1210

# 2. Функция для расшифровки вашего текста
parse_table <- function(txt, prefix) {
  lines <- strsplit(trimws(txt), "\n")[[1]]
  lines <- lines[grepl("\\[", lines)] # берем только строки с данными
  
  compounds <- character(); r1 <- numeric(); r2 <- numeric(); r3 <- numeric()
  
  for(l in lines) {
    parts <- trimws(unlist(strsplit(l, "\\|")))
    parts <- parts[parts != ""]
    if(length(parts) >= 3) {
      comp <- trimws(parts[2])
      vals <- as.numeric(unlist(strsplit(gsub("\\[|\\]", "", parts[3]), ","))) 
      compounds <- c(compounds, comp)
      r1 <- c(r1, vals[1]); r2 <- c(r2, vals[2]); r3 <- c(r3, vals[3])
    }
  }
  df <- data.frame(Compound = compounds, Rep1 = r1, Rep2 = r2, Rep3 = r3)
  colnames(df)[2:4] <- paste0(prefix, "_", 1:3)
  return(df)
}

# 3. Обрабатываем тексты
df_108 <- parse_table(text_108, "C108")
df_1210 <- parse_table(text_1210, "C1210")

# 4. Объединяем (заполняем нулями молекулы, которых нет во второй группе)
full_data <- merge(df_108, df_1210, by = "Compound", all = TRUE)
full_data[is.na(full_data)] <- 0

# 5. Транспонируем, чтобы образцы стали строками
t_data <- t(full_data[, -1])
colnames(t_data) <- full_data$Compound

# 6. Создаем финальную красивую таблицу с колонкой "Группа"
final_df <- data.frame(
  SampleID = rownames(t_data),
  Group = c("C-108", "C-108", "C-108", "C-1210", "C-1210", "C-1210")
)
final_df <- cbind(final_df, t_data)

# 7. Сохраняем в CSV файл в вашу рабочую папку
write.csv(final_df, "my_data.csv", row.names = FALSE)
cat("Файл my_data.csv успешно создан и сохранен в папке:", getwd(), "\n")
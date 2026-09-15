# library(tidyverse)
library(vegan)
library(indicspecies)

# =====================================================================
# ШАГ 1: ПРЕОБРАЗОВАНИЕ ДАННЫХ И СОЗДАНИЕ CSV
# =====================================================================

# Вставьте вашу таблицу между кавычками (здесь показан фрагмент, 
# вы можете вставить все 99 строк прямо сюда)
raw_data <- "
| #   | Triacylglycerol                                           | Value[0], %              | Value[1], %              |
| --- | --------------------------------------------------------- | ------------------------ | ------------------------ |
| 1   | [Oleic/2;Linoleic;Oleic/2]                                | [11.981, 11.736, 10.358] | [0.937, 0.852, 0.97]     |
| 2   | [Oleic/2;Linoleic;Palmitic/2]                             | [8.878, 8.833, 8.563]    | [6.527, 6.383, 6.739]    |
| 3   | [Oleic/2;Oleic;Oleic/2]                                   | [7.273, 7.622, 8.326]    | [0.82, 0.878, 0.965]     |
| 4   | [Oleic/2;Oleic;Palmitic/2]                                | [5.389, 5.736, 6.883]    | [5.713, 6.58, 6.707]     |
| 5   | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]          | [4.99, 4.739, 3.096]     | [0.159, 0.14, 0.138]     |
| 6   | [Linoleic/2;Linoleic;Oleic/2]                             | [3.413, 3.24, 3.435]     | [2.23, 1.945, 2.13]      |
| 7   | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]       | [3.698, 3.566, 2.559]    | [1.105, 1.052, 0.957]    |
| 8   | [Oleic/2;Linoleic;α-Linolenic/2]                          | [3.123, 2.886, 3.015]    | [1.05, 0.868, 0.958]     |
| 9   | [Oleic/2;Linoleic;Stearic/2]                              | [2.318, 2.437, 2.251]    | [0.152, 0.137, 0.179]    |
| 10  | [Linoleic/2;Oleic;Oleic/2]                                | [2.072, 2.104, 2.761]    | [1.952, 2.005, 2.12]     |
| 11  | [Oleic/2;Palmitic;Oleic/2]                                | [2.477, 2.365, 1.605]    | [0.063, 0.062, 0.083]    |
| 12  | [Oleic/2;Oleic;α-Linolenic/2]                             | [1.896, 1.875, 2.424]    | [0.92, 0.895, 0.953]     |
| 13  | [Oleic/2;α-Linolenic;Oleic/2]                             | [2.062, 2.115, 1.446]    | [0.08, 0.068, 0.069]     |
| 14  | [Palmitic/2;Linoleic;Palmitic/2]                          | [1.645, 1.662, 1.77]     | [11.371, 11.957, 11.705] |
| 15  | [Oleic/2;Palmitic;Palmitic/2]                             | [1.836, 1.78, 1.327]     | [0.437, 0.464, 0.574]    |
| 16  | [Oleic/2;Oleic;Stearic/2]                                 | [1.407, 1.583, 1.81]     | [0.133, 0.141, 0.178]    |
| 17  | [Oleic/2;Roughanic;Oleic/2]                               | [1.257, 1.322, 2.11]     | [0.359, 0.292, 0.299]    |
| 18  | [Oleic/2;α-Linolenic;Palmitic/2]                          | [1.528, 1.592, 1.195]    | [0.555, 0.511, 0.477]    |
| 19  | [Linoleic/2;Linoleic;Palmitic/2]                          | [1.264, 1.219, 1.42]     | [7.77, 7.287, 7.401]     |
| 20  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]       | [1.422, 1.308, 1.027]    | [0.378, 0.321, 0.302]    |
| 21  | [Oleic/2;Roughanic;Palmitic/2]                            | [0.932, 0.995, 1.744]    | [2.504, 2.186, 2.074]    |
| 22  | [Palmitic/2;Oleic;Palmitic/2]                             | [0.998, 1.079, 1.423]    | [9.954, 12.325, 11.649]  |
| 23  | [Palmitic/2;Linoleic;α-Linolenic/2]                       | [1.157, 1.086, 1.246]    | [3.66, 3.254, 3.328]     |
| 24  | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2]    | [1.301, 1.165, 0.901]    | [0.178, 0.143, 0.136]    |
| 25  | [Palmitic/2;Linoleic;Stearic/2]                           | [0.859, 0.917, 0.931]    | [0.529, 0.512, 0.623]    |
| 26  | [Linoleic/2;Oleic;Palmitic/2]                             | [0.768, 0.792, 1.141]    | [6.802, 7.512, 7.365]    |
| 27  | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Stearic/2]        | [0.966, 0.984, 0.673]    | [0.026, 0.023, 0.025]    |
| 28  | [Palmitic/2;Oleic;α-Linolenic/2]                          | [0.702, 0.705, 1.002]    | [3.204, 3.354, 3.312]    |
| 29  | [Linoleic/2;Palmitic;Oleic/2]                             | [0.706, 0.653, 0.532]    | [0.149, 0.141, 0.181]    |
| 30  | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [0.685, 0.671, 0.529]    | [1.925, 1.971, 1.662]    |
| 31  | [Palmitic/2;Oleic;Stearic/2]                              | [0.521, 0.596, 0.748]    | [0.464, 0.528, 0.62]     |
| 32  | [Gondoic/2;Linoleic;Oleic/2]                              | [0.571, 0.64, 0.587]     | [0, 0, 0]                |
| 33  | [Oleic/2;Palmitic;α-Linolenic/2]                          | [0.646, 0.582, 0.467]    | [0.07, 0.063, 0.082]     |
| 34  | [Linoleic/2;α-Linolenic;Oleic/2]                          | [0.587, 0.584, 0.48]     | [0.19, 0.156, 0.151]     |
| 35  | [Oleic/2;α-Linolenic;α-Linolenic/2]                       | [0.537, 0.52, 0.421]     | [0.089, 0.07, 0.068]     |
| 36  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Palmitic/2]    | [0.527, 0.492, 0.424]    | [1.316, 1.201, 1.051]    |
| 37  | [Linoleic/2;Roughanic;Oleic/2]                            | [0.358, 0.365, 0.7]      | [0.855, 0.666, 0.656]    |
| 38  | [Linoleic/2;Linoleic;α-Linolenic/2]                       | [0.445, 0.398, 0.5]      | [1.251, 0.991, 1.052]    |
| 39  | [Oleic/2;Palmitic;Stearic/2]                              | [0.479, 0.491, 0.349]    | [0.01, 0.01, 0.015]      |
| 40  | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2] | [0.482, 0.439, 0.373]    | [0.62, 0.536, 0.472]     |
| 41  | [Oleic/2;Hypogeic;Oleic/2]                                | [0.476, 0.454, 0.363]    | [0, 0, 0]                |
| 42  | [Oleic/2;Roughanic;α-Linolenic/2]                         | [0.328, 0.325, 0.614]    | [0.403, 0.297, 0.295]    |
| 43  | [Gondoic/2;Oleic;Oleic/2]                                 | [0.346, 0.416, 0.472]    | [0, 0, 0]                |
| 44  | [Oleic/2;α-Linolenic;Stearic/2]                           | [0.399, 0.439, 0.314]    | [0.013, 0.011, 0.013]    |
| 45  | [Linoleic/2;Linoleic;Stearic/2]                           | [0.33, 0.336, 0.373]     | [0.181, 0.156, 0.197]    |
| 46  | [Palmitic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Stearic/2]     | [0.358, 0.37, 0.278]     | [0.09, 0.084, 0.088]     |
| 47  | [Oleic/2;Hypogeic;Palmitic/2]                             | [0.353, 0.341, 0.3]      | [0, 0, 0]                |
| 48  | [Oleic/2;Roughanic;Stearic/2]                             | [0.243, 0.275, 0.459]    | [0.058, 0.047, 0.055]    |
| 49  | [Palmitic/2;Palmitic;Palmitic/2]                          | [0.34, 0.335, 0.274]     | [0.762, 0.869, 0.997]    |
| 50  | [Linoleic/2;Oleic;α-Linolenic/2]                          | [0.27, 0.259, 0.402]     | [1.095, 1.022, 1.047]    |
| 51  | [Stearic/2;Linoleic;α-Linolenic/2]                        | [0.302, 0.3, 0.328]      | [0.085, 0.07, 0.089]     |
| 52  | [Oleic/2;Linoleic;cis-Vaccenic/2]                         | [0.293, 0.285, 0.291]    | [0.137, 0.126, 0.143]    |
| 53  | [Palmitic/2;α-Linolenic;Palmitic/2]                       | [0.283, 0.3, 0.247]      | [0.967, 0.957, 0.829]    |
| 54  | [Linoleic/2;Linoleic;Linoleic/2]                          | [0.243, 0.224, 0.285]    | [1.327, 1.11, 1.17]      |
| 55  | [Linoleic/2;Palmitic;Palmitic/2]                          | [0.261, 0.246, 0.22]     | [0.521, 0.529, 0.63]     |
| 56  | [Palmitic/2;Roughanic;Palmitic/2]                         | [0.173, 0.187, 0.36]     | [4.362, 4.094, 3.603]    |
| 57  | [Linoleic/2;Oleic;Stearic/2]                              | [0.2, 0.218, 0.3]        | [0.158, 0.161, 0.196]    |
| 58  | [Gondoic/2;Linoleic;Palmitic/2]                           | [0.211, 0.241, 0.243]    | [0, 0, 0]                |
| 59  | [Gondoic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Oleic/2]        | [0.238, 0.258, 0.175]    | [0, 0, 0]                |
| 60  | [Palmitic/2;Palmitic;α-Linolenic/2]                       | [0.239, 0.219, 0.193]    | [0.245, 0.236, 0.283]    |
| 61  | [Stearic/2;Oleic;α-Linolenic/2]                           | [0.183, 0.195, 0.263]    | [0.075, 0.072, 0.088]    |
| 62  | [Linoleic/2;α-Linolenic;Palmitic/2]                       | [0.218, 0.22, 0.198]     | [0.661, 0.583, 0.524]    |
| 63  | [Oleic/2;Linoleic;γ-Linolenic/2]                          | [0.222, 0.204, 0.19]     | [0, 0, 0]                |
| 64  | [α-Linolenic/2;Linoleic;α-Linolenic/2]                    | [0.203, 0.177, 0.219]    | [0.295, 0.221, 0.237]    |
| 65  | [Oleic/2;Oleic;cis-Vaccenic/2]                            | [0.178, 0.185, 0.234]    | [0.12, 0.13, 0.143]      |
| 66  | [Palmitic/2;α-Linolenic;α-Linolenic/2]                    | [0.199, 0.196, 0.174]    | [0.311, 0.26, 0.236]     |
| 67  | [Linoleic/2;Roughanic;Palmitic/2]                         | [0.133, 0.137, 0.289]    | [2.981, 2.495, 2.278]    |
| 68  | [Linoleic/2;Oleic;Linoleic/2]                             | [0.148, 0.145, 0.229]    | [1.162, 1.145, 1.164]    |
| 69  | [Palmitic/2;Palmitic;Stearic/2]                           | [0.178, 0.185, 0.144]    | [0.035, 0.037, 0.053]    |
| 70  | [Palmitic/2;Roughanic;α-Linolenic/2]                      | [0.121, 0.122, 0.254]    | [1.404, 1.114, 1.024]    |
| 71  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2] | [0.185, 0.161, 0.149]    | [0.212, 0.163, 0.149]    |
| 72  | [Gondoic/2;Oleic;Palmitic/2]                              | [0.128, 0.156, 0.195]    | [0, 0, 0]                |
| 73  | [Oleic/2;Linoleic;Stearidonic/2]                          | [0.163, 0.153, 0.154]    | [0, 0, 0]                |
| 74  | [Arachidic/2;Linoleic;Oleic/2]                            | [0.158, 0.165, 0.138]    | [0, 0, 0]                |
| 75  | [Palmitic/2;α-Linolenic;Stearic/2]                        | [0.148, 0.165, 0.13]     | [0.045, 0.041, 0.044]    |
| 76  | [Oleic/2;Oleic;γ-Linolenic/2]                             | [0.135, 0.132, 0.152]    | [0, 0, 0]                |
| 77  | [α-Linolenic/2;Oleic;α-Linolenic/2]                       | [0.124, 0.115, 0.176]    | [0.258, 0.228, 0.235]    |
| 78  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Stearic/2]     | [0.138, 0.136, 0.112]    | [0.031, 0.026, 0.028]    |
| 79  | [Palmitic/2;Roughanic;Stearic/2]                          | [0.09, 0.103, 0.19]      | [0.203, 0.175, 0.192]    |
| 80  | [Linoleic/2;Hypogeic;Oleic/2]                             | [0.136, 0.125, 0.12]     | [0, 0, 0]                |
| 81  | [Stearic/2;Linoleic;Stearic/2]                            | [0.112, 0.127, 0.122]    | [0.006, 0.005, 0.008]    |
| 82  | [Stearic/2;(7Z,10Z)-hexadeca-7,10-dienoic;α-Linolenic/2]  | [0.126, 0.121, 0.098]    | [0.014, 0.011, 0.013]    |
| 83  | [Oleic/2;Hypogeic;α-Linolenic/2]                          | [0.124, 0.112, 0.106]    | [0, 0, 0]                |
| 84  | [Gondoic/2;Palmitic;Oleic/2]                              | [0.118, 0.129, 0.091]    | [0, 0, 0]                |
| 85  | [Palmitic/2;Linoleic;cis-Vaccenic/2]                      | [0.108, 0.107, 0.12]     | [0.478, 0.473, 0.497]    |
| 86  | [Oleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;cis-Vaccenic/2]   | [0.122, 0.115, 0.087]    | [0.023, 0.021, 0.02]     |
| 87  | [Oleic/2;Oleic;Stearidonic/2]                             | [0.099, 0.099, 0.124]    | [0, 0, 0]                |
| 88  | [Oleic/2;Stearic;Oleic/2]                                 | [0.139, 0.108, 0.073]    | [0.006, 0.007, 0.014]    |
| 89  | [Arachidic/2;Oleic;Oleic/2]                               | [0.096, 0.107, 0.111]    | [0, 0, 0]                |
| 90  | [Linoleic/2;(7Z,10Z)-hexadeca-7,10-dienoic;Linoleic/2]    | [0.101, 0.09, 0.085]     | [0.225, 0.183, 0.166]    |
| 91  | [Palmitic/2;Oleic;cis-Vaccenic/2]                         | [0.066, 0.07, 0.097]     | [0.418, 0.488, 0.495]    |
| 92  | [Linoleic/2;Roughanic;α-Linolenic/2]                      | [0.047, 0.045, 0.102]    | [0.48, 0.339, 0.324]     |
| 93  | [Linoleic/2;Linoleic;cis-Vaccenic/2]                      | [0.042, 0.039, 0.048]    | [0.163, 0.144, 0.157]    |
| 94  | [Linoleic/2;Roughanic;Linoleic/2]                         | [0.026, 0.025, 0.058]    | [0.509, 0.38, 0.36]      |
| 95  | [Linoleic/2;Oleic;cis-Vaccenic/2]                         | [0.025, 0.026, 0.039]    | [0.143, 0.149, 0.156]    |
| 96  | [Palmitic/2;Roughanic;cis-Vaccenic/2]                     | [0.011, 0.012, 0.025]    | [0.183, 0.162, 0.153]    |
| 97  | [Palmitic/2;Stearic;Palmitic/2]                           | [0.019, 0.015, 0.012]    | [0.077, 0.093, 0.171]    |
| 98  | [Lignoceric/2;Linoleic;Palmitic/2]                        | [0.003, 0.006, 0.006]    | [0.069, 0.129, 0.135]    |
| 99  | [Lignoceric/2;Oleic;Palmitic/2]                           | [0.002, 0.004, 0.005]    | [0.06, 0.133, 0.135]     |
"

# 1.1 Чтение текста и базовая очистка
df_raw <- read.delim(text = raw_data, sep = "|", header = FALSE, strip.white = TRUE) %>%
  select(V3, V4, V5) %>% # Оставляем только столбцы с TAG и значениями
  filter(grepl("\\[", V3)) %>% # Убираем строки разметки (где нет скобок в названии)
  rename(TAG = V3, Value0 = V4, Value1 = V5)

# 1.2 Удаление квадратных скобок из значений и разделение на 3 реплики
df_clean <- df_raw %>%
  mutate(
    Value0 = str_remove_all(Value0, "\\[|\\]"),
    Value1 = str_remove_all(Value1, "\\[|\\]")
  ) %>%
  separate(Value0, into = c("Group0_Rep1", "Group0_Rep2", "Group0_Rep3"), sep = ",\\s*", convert = TRUE) %>%
  separate(Value1, into = c("Group1_Rep1", "Group1_Rep2", "Group1_Rep3"), sep = ",\\s*", convert = TRUE)

# 1.3 Транспонирование: строки -> образцы, столбцы -> TAG
df_final <- df_clean %>%
  pivot_longer(cols = starts_with("Group"), names_to = "Sample", values_to = "Abundance") %>%
  mutate(Group = str_extract(Sample, "Group[01]")) %>% # Создаем факторную переменную группы
  select(Sample, Group, TAG, Abundance) %>%
  pivot_wider(names_from = TAG, values_from = Abundance)

# 1.4 Сохранение в CSV, пригодный для vegan
write.csv(df_final, "data.csv", row.names = FALSE)
cat("Файл data.csv успешно создан!\n\n")

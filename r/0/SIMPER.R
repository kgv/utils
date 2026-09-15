# average: средний вклад вида в различие между этими двумя биотопами.
# cumsum: накопленный процент.
# Интерпретация: Виды, расположенные в самом верху списка каждой пары — это главные «виновники» того, что два биотопа отличаются друг от друга (в одном их много, в другом мало или нет совсем).

library(vegan)
library(indicspecies)

# Фиксируем генератор случайных чисел (чтобы результат перестановок всегда был одинаковым)
set.seed(1234)

# Загружаем встроенные тестовые данные
mydata <- read.csv("data.csv", check.names = FALSE)

# Отделяем матрицу обилий (начиная с 3-го столбца, т.к. 1 - Sample, 2 - Group)
abund <- mydata[, 3:ncol(mydata)]
m_abund <- as.matrix(abund)
group_factor <- mydata$Group

cat("\n=== Результаты SIMPER ===\n")
sim <- simper(m_abund, group_factor)
# print(summary(sim))

sim_sum <- summary(sim) 

# Проходим циклом по всем попарным сравнениям (Group0_Group1, Group0_Group2 и т.д.)
for (comp_name in names(sim_sum)) {
  # Извлекаем данные текущего сравнения
  comp_data <- sim_sum[[comp_name]]
  
  # Добавляем колонку с названием молекулы (TAG), которая хранится в именах строк
  comp_data$TAG <- rownames(comp_data)
  
  # Добавляем колонку с названием сравнения
  comp_data$Comparison <- comp_name
  
  # Переставляем колонки, чтобы было удобно читать (Сравнение и TAG в начале)
  # Примечание: если в группе 1 образец, колонка 'sd' может отсутствовать или быть NA, 
  # поэтому берем только те колонки, которые реально есть
  cols_order <- c("Comparison", "TAG", "average", "sd", "ratio", "ava", "avb", "cumsum", "p")
  cols_existing <- intersect(cols_order, colnames(comp_data))
  comp_data <- comp_data[, c("Comparison", "TAG", cols_existing)]
  
  # Присоединяем к общей таблице
  simper_results <- rbind(simper_results, comp_data)
}

# Сохраняем итоговую таблицу в CSV
write.csv(simper_results, "simper_results.csv", row.names = FALSE)

cat("Анализ SIMPER завершен! Результаты сохранены в файл 'simper_results.csv'\n")
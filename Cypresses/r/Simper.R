# source("/mnt/d/g/git/kgv/utils/Cypresses/r/Simper.R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
# "Genus"
# "Species"
# "Variety"
TARGET_GROUP <- "Species"

# Укажите здесь метрику расстояния 
# ("bray", "jaccard", "euclidean", "manhattan")
TARGET_DISTANCE <- "bray"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink("Cypresses/_Simper.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(1234)

# Загрузка данных
mydata <- read.csv("Cypresses/_Wide.txt", check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 7-го столбца)
abund <- mydata[, 7:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
# abund <- as.data.frame(lapply(abund, as.numeric))
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

m_abund <- as.matrix(abund)

# group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
group_factor <- as.factor(mydata[[TARGET_GROUP]])

# ---------------------------------------------------------------------
# Процедура SIMPER (Оценка вклада компонентов в различия)
# ---------------------------------------------------------------------
cat("=== Результаты SIMPER ===\n")
cat("Анализируемые факторы:", paste(TARGET_GROUP, collapse = " и "), "\n")
cat("Метрика расстояния:", TARGET_DISTANCE, "\n")

sim <- simper(m_abund, group_factor)
sim_sum <- summary(sim)
print(sim_sum)

# for (comp_name in names(sim_sum)) {
#   cat("\n--------------------------------------------------\n")
#   cat("Сравнение:", comp_name, "\n")
#   cat("--------------------------------------------------\n")
  
#   df <- sim_sum[[comp_name]]
  
#   # Округляем длинные числа до 4 знаков после запятой
#   is_num <- sapply(df, is.numeric)
#   df[is_num] <- lapply(df[is_num], round, 4)
  
#   # Выводим красивую таблицу
#   print(kable(df, format = "markdown"))
#   cat("\n")
# }

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
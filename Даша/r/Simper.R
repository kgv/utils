# source("/mnt/d/g/git/kgv/utils/Даша/r/Simper.R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
# "Ni": Проверяет гипотезу, отличается ли в целом профиль жирных кислот у растений, которые росли без никеля (0), от тех, что росли с никелем (50, 250, 500, 750, 1000).
# "Week": Проверяет гипотезу, изменяется ли состав жирных кислот со временем (стал ли он другими к 5-й неделе по сравнению с 1-й).
# c("Ni", "Week"): Проверит гипотезу, есть ли разница в составе жирных кислот между этими 12 уникальными состояниями.
TARGET_GROUP <- "Ni"
# TARGET_GROUP <- "Week"
# TARGET_GROUP <- c("Ni", "Week")

# Укажите здесь метрику расстояния 
# ("bray", "jaccard", "euclidean", "manhattan")
TARGET_DISTANCE <- "bray"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink("Даша/_Simper.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(1234)

# Загрузка данных
mydata <- read.csv("Даша/_Wide.txt", check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 4-го столбца)
abund <- mydata[, 4:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
# abund <- as.data.frame(lapply(abund, as.numeric))
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

m_abund <- as.matrix(abund)

# group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# Создаем комбинированный фактор для графиков, SIMPER и IndVal
if (length(TARGET_GROUP) > 1) {
  # Функция interaction() склеит значения. Если Ni=50 и Week=1, получится группа "50.1"
  group_factor <- interaction(mydata[, TARGET_GROUP], drop = TRUE)
} else {
  # Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
  group_factor <- as.factor(mydata[[TARGET_GROUP]])
}

# ---------------------------------------------------------------------
# Процедура SIMPER (Оценка вклада компонентов в различия)
# ---------------------------------------------------------------------
cat("=== Результаты SIMPER ===\n")
cat("Анализируемые факторы:", paste(TARGET_GROUP, collapse = " и "), "\n")
cat("Метрика расстояния:", TARGET_DISTANCE, "\n")

sim <- simper(m_abund, group_factor)
sim_sum <- summary(sim)

for (comp_name in names(sim_sum)) {
  cat("\n--------------------------------------------------\n")
  cat("Сравнение:", comp_name, "\n")
  cat("--------------------------------------------------\n")
  
  df <- sim_sum[[comp_name]]
  
  # Округляем длинные числа до 4 знаков после запятой
  is_num <- sapply(df, is.numeric)
  df[is_num] <- lapply(df[is_num], round, 4)
  
  # Выводим красивую таблицу
  print(kable(df, format = "markdown"))
  cat("\n")
}

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
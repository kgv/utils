# source("/mnt/d/g/git/kgv/utils/Даша/r/Indval.R", encoding = "UTF-8")

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
sink("Даша/_Indval.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
mydata <- read.csv("Даша/_Wide.txt", check.names = FALSE, stringsAsFactors = FALSE)

# # Отделяем матрицу обилий (начиная с 4-го столбца)
# abund <- mydata[, 4:ncol(mydata)]

# # Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
# # abund <- as.data.frame(lapply(abund, as.numeric))
# abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

# m_abund <- as.matrix(abund)

# # group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# # Создаем комбинированный фактор для графиков, SIMPER и IndVal
# if (length(TARGET_GROUP) > 1) {
#   # Функция interaction() склеит значения. Если Ni=50 и Week=1, получится группа "50.1"
#   group_factor <- interaction(mydata[, TARGET_GROUP], drop = TRUE)
# } else {
#   # Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
#   group_factor <- as.factor(mydata[[TARGET_GROUP]])
# }

# # ---------------------------------------------------------------------
# # Процедура IndVal (Компоненты-индикаторы)
# # ---------------------------------------------------------------------
# cat("=== Результаты IndVal ===\n")
# cat("Анализируемые факторы:", paste(TARGET_GROUP, collapse = " и "), "\n")
# cat("Метрика расстояния:", TARGET_DISTANCE, "\n")

# # multipatt лучше работает с data.frame, передаем abund вместо m_abund
# ind_val <- multipatt(abund, group_factor, func = "r.g", control = how(nperm=999))
# ind_val_sum <- summary(ind_val)
# print(ind_val_sum)

mydata$Ni_binary <- ifelse(mydata$Ni == 0, "Control", "Treated")
mydata$Ni_binary <- as.factor(mydata$Ni_binary)

cat("\n=== Результаты IndVal: Контроль (0) vs Воздействие (50-1000) на 1-й неделе ===\n")
# Фильтруем данные только для 1-й недели
data_w1 <- subset(mydata, Week == 1)
abund_w1 <- data_w1[, 4:ncol(data_w1)]
# Используем наш новый бинарный фактор!
group_binary_w1 <- data_w1$Ni_binary 

# Запускаем IndVal
ind_val_w1_bin <- multipatt(abund_w1, group_binary_w1, func = "r.g", control = how(nperm=999))
print(summary(ind_val_w1_bin))


cat("\n=== Результаты IndVal: Контроль (0) vs Воздействие (50-1000) на 5-й неделе ===\n")
# Фильтруем данные только для 5-й недели
data_w5 <- subset(mydata, Week == 5)
abund_w5 <- data_w5[, 4:ncol(data_w5)]
# Используем наш новый бинарный фактор!
group_binary_w5 <- data_w5$Ni_binary 

# Запускаем IndVal
ind_val_w5_bin <- multipatt(abund_w5, group_binary_w5, func = "r.g", control = how(nperm=999))
print(summary(ind_val_w5_bin))

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
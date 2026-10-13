# source("/mnt/d/g/git/kgv/utils/Cypresses/r/Indval.R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
# "Genus"
# "Species"
# "Variety"
TARGET_GROUP <- "Species"

# Укажите здесь метрику расстояния 
# "bray"
# "jaccard"
# "euclidean"
# "manhattan"
TARGET_DISTANCE <- "bray"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink("Cypresses/_Indval.txt", split = FALSE)

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
# Процедура IndVal (Компоненты-индикаторы)
# ---------------------------------------------------------------------
cat("=== Результаты IndVal ===\n")
cat("Анализируемые факторы:", TARGET_GROUP, "\n")
cat("Метрика расстояния:", TARGET_DISTANCE, "\n")

# multipatt лучше работает с data.frame, передаем abund вместо m_abund
ind_val <- multipatt(abund, group_factor, func = "r.g", control = how(nperm=999))
ind_val_sum <- summary(ind_val)
print(ind_val_sum)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
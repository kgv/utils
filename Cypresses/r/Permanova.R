# source("/mnt/d/g/git/kgv/utils/Cypresses/r/Permanova.R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
# ("Species", "Variety", "Genus")
TARGET_GROUP <- "Species"

# Укажите здесь метрику расстояния 
# ("bray", "jaccard", "euclidean", "manhattan")
TARGET_DISTANCE <- "bray"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink("Cypresses/_Permanova.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(1234)

# Загрузка данных
mydata <- read.csv("Cypresses/_Wide.txt", check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 7-го столбца)
abund <- mydata[, 7:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric))

m_abund <- as.matrix(abund)

# group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
group_factor <- as.factor(mydata[[TARGET_GROUP]])

# Динамически создаем формулу. 
# Если TARGET_GROUP = "Species", то получится формула: m_abund ~ Species
perm_formula <- as.formula(paste("m_abund ~", TARGET_GROUP))

# ---------------------------------------------------------------------
# Тест PERMANOVA (Многофакторный дисперсионный анализ)
# ---------------------------------------------------------------------
cat("=== Результаты PERMANOVA ===\n")
cat("Фактор группировки:", TARGET_GROUP, "\n")
cat("Метрика расстояния:", TARGET_DISTANCE, "\n")

permanova_result <- adonis2(perm_formula, data = mydata, permutations = 9999, method = TARGET_DISTANCE)
print(permanova_result)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
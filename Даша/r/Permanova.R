# source("/mnt/d/g/git/kgv/utils/Даша/r/Permanova.R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
# "Ni": Проверяет гипотезу, отличается ли в целом профиль жирных кислот у растений, которые росли без никеля (0), от тех, что росли с никелем (50, 250, 500, 750, 1000).
# "Week": Проверяет гипотезу, изменяется ли состав жирных кислот со временем (стал ли он другими к 5-й неделе по сравнению с 1-й).
# c("Ni", "Week"): Проверит гипотезу, есть ли разница в составе жирных кислот между этими 12 уникальными состояниями.
TARGET_GROUP <- c("Ni", "Week")

# Укажите здесь метрику расстояния 
# ("bray", "jaccard", "euclidean", "manhattan")
TARGET_DISTANCE <- "bray"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink("Даша/_Permanova.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
# mydata <- read.csv("Даша/_Wide{Kind=Leaf}{Value=PartsPerMillion_DryWeight}.txt", check.names = FALSE, stringsAsFactors = FALSE)
# mydata <- read.csv("Даша/_Wide{Kind=Leaf}{Value=PartsPerMillion_DryWeight}{Week=1}.txt", check.names = FALSE, stringsAsFactors = FALSE)
# mydata <- read.csv("Даша/_Wide{Kind=Leaf}{Value=PartsPerMillion_DryWeight}{Week=5}.txt", check.names = FALSE, stringsAsFactors = FALSE)
mydata <- read.csv("Даша/_Wide{Kind=Root}{Value=PartsPerMillion_DryWeight}.txt", check.names = FALSE, stringsAsFactors = FALSE)
# mydata <- read.csv("Даша/_Wide{Kind=Root}{Value=PartsPerMillion_DryWeight}{Week=1}.txt", check.names = FALSE, stringsAsFactors = FALSE)
# mydata <- read.csv("Даша/_Wide{Kind=Root}{Value=PartsPerMillion_DryWeight}{Week=5}.txt", check.names = FALSE, stringsAsFactors = FALSE)
# mydata <- read.csv("Даша/_Wide.txt", check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 4-го столбца)
abund <- mydata[, 4:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric))

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

# Создаем формулу для PERMANOVA
# Если указано c("Ni", "Week"), получится формула: m_abund ~ Ni * Week
# Знак * означает, что мы проверяем влияние Ni, влияние Week и их совместное влияние (Ni:Week)
formula_str <- paste("m_abund ~", paste(TARGET_GROUP, collapse = " * "))
perm_formula <- as.formula(formula_str)

# ---------------------------------------------------------------------
# Тест PERMANOVA (Многофакторный дисперсионный анализ)
# ---------------------------------------------------------------------
cat("=== Результаты PERMANOVA ===\n")
cat("Анализируемые факторы:", paste(TARGET_GROUP, collapse = " и "), "\n")
cat("Метрика расстояния:", TARGET_DISTANCE, "\n")

permanova_result <- adonis2(perm_formula, data = mydata, permutations = 9999, method = TARGET_DISTANCE)
print(permanova_result)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
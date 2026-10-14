# source("/mnt/d/g/git/kgv/utils/Даша/r/Indval.R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
# "Ni": Проверяет гипотезу, отличается ли в целом профиль жирных кислот у растений, которые росли без никеля (0), от тех, что росли с никелем (50, 250, 500, 750, 1000).
# "Week": Проверяет гипотезу, изменяется ли состав жирных кислот со временем (стал ли он другими к 5-й неделе по сравнению с 1-й).
# c("Ni", "Week"): Проверит гипотезу, есть ли разница в составе жирных кислот между этими 12 уникальными состояниями.
# GROUP <- "Ni"
# GROUP <- "Week"
GROUP <- c("Ni", "Week")

# Укажите здесь метрику расстояния 
# ("bray", "jaccard", "euclidean", "manhattan")
DISTANCE <- "bray"

FUNCTION <- "IndVal.g"
# FUNCTION <- "r.g"

PERMUTATIONS <- 999

KIND = "Leaf"
# KIND = "Root"

VALUE = "PartsPerMillion_DryWeight"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
output_file <- paste0("Даша/_{Type=IndVal}{kind=", KIND, "}{Group=", paste(GROUP, collapse = ","), "}{Permutations=", PERMUTATIONS, "}{Value=", VALUE, "}.txt")
sink(output_file, split = FALSE)
# sink("Даша/_Indval.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
input_file <- paste0("Даша/csv/_{Type=Wide}{kind=", KIND, "}{Value=", VALUE, "}.txt")
mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 4-го столбца)
abund <- mydata[, 4:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
# abund <- as.data.frame(lapply(abund, as.numeric))
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

m_abund <- as.matrix(abund)

# group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# Создаем комбинированный фактор для графиков, SIMPER и IndVal
if (length(GROUP) > 1) {
  # Функция interaction() склеит значения. Если Ni=50 и Week=1, получится группа "50.1"
  group_factor <- interaction(mydata[, GROUP], drop = TRUE)
} else {
  # Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
  group_factor <- as.factor(mydata[[GROUP]])
}

# ---------------------------------------------------------------------
# Процедура IndVal (Компоненты-индикаторы)
# ---------------------------------------------------------------------
cat("=== IndVal ===\n")
cat("distance:", DISTANCE, "\n")
cat("function:", FUNCTION, "\n")
cat("group:", paste(GROUP, collapse = ", "), "\n")
cat("kind:", KIND, "\n")
cat("permutations:", PERMUTATIONS, "\n")
cat("value:", VALUE, "\n")

# multipatt лучше работает с data.frame, передаем abund вместо m_abund
ind_val <- multipatt(abund, group_factor, func = FUNCTION, control = how(nperm=PERMUTATIONS))
ind_val_sum <- summary(ind_val)
print(ind_val_sum)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
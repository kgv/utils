# source("/mnt/d/git/kgv/utils/Cypresses/r/Permanova.R", encoding = "UTF-8")

library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
# GROUP <- "Genus"
GROUP <- "Species"
# GROUP <- "Variety"

# Укажите здесь метрику расстояния
# https://www.rdocumentation.org/packages/vegan/topics/vegdist
# https://vegandevs.github.io/vegan/reference/designdist.html
DISTANCE <- "bray"
# DISTANCE <- "euclidean"
# DISTANCE <- "hellinger"

# PERMUTATIONS <- 9999
PERMUTATIONS <- 9999

COMPONENT = "Terpene"
# COMPONENT = "Monoterpene"
# COMPONENT = "Sesquiterpene"

VALUE = "PartsPerMillion_Mean"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
output_file <- paste0("Cypresses/_{Type=PERMANOVA}{Group=", GROUP, "}{Distance=", DISTANCE, "}{Permutations=", PERMUTATIONS, "}{Component=", COMPONENT, "}{Value=", VALUE, "}.txt")
sink(output_file, split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
input_file <- paste0("Cypresses/_{Type=Wide}{Component=", COMPONENT, "}{Value=", VALUE, "}.txt")
mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 7-го столбца)
abund <- mydata[, 7:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric))

m_abund <- as.matrix(abund)

# group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
group_factor <- as.factor(mydata[[GROUP]])

# Динамически создаем формулу. 
# Если GROUP = "Species", то получится формула: m_abund ~ Species
perm_formula <- as.formula(paste("m_abund ~", GROUP))

# ---------------------------------------------------------------------
# Тест PERMANOVA (Многофакторный дисперсионный анализ)
# ---------------------------------------------------------------------
cat("=== PERMANOVA ===\n")
cat("group:", GROUP, "\n")
cat("method:", DISTANCE, "\n")
cat("permutations:", PERMUTATIONS, "\n\n")

# https://www.rdocumentation.org/packages/vegan/topics/adonis
permanova_result <- adonis2(perm_formula, data = mydata, permutations = PERMUTATIONS, method = DISTANCE)
print(permanova_result)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
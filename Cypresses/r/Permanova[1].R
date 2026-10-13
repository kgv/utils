# source("/mnt/d/git/kgv/utils/Cypresses/r/permanova[1].R", encoding = "UTF-8")

library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
GROUP <- "Genus"
# GROUP <- "Species"
# GROUP <- "Variety"

# Укажите здесь метрику расстояния
# 
# https://www.rdocumentation.org/packages/vegan/topics/vegdist
# https://vegandevs.github.io/vegan/reference/designdist.html
# 
# DISTANCE <- "manhattan"
# DISTANCE <- "euclidean"
# DISTANCE <- "canberra"
# DISTANCE <- "clark"
DISTANCE <- "bray"
# DISTANCE <- "kulczynski"
# DISTANCE <- "jaccard"
# DISTANCE <- "gower"
# DISTANCE <- "altGower"
# DISTANCE <- "morisita"
# DISTANCE <- "horn"
# DISTANCE <- "mountford"
# DISTANCE <- "raup"
# DISTANCE <- "binomial"
# DISTANCE <- "chao"
# DISTANCE <- "cao"
# DISTANCE <- "mahalanobis"
# DISTANCE <- "chisq"
# DISTANCE <- "chord"
# DISTANCE <- "hellinger"
# DISTANCE <- "aitchison"
# DISTANCE <- "robust.aitchison"
# 
# DISTANCE <- "cosine"

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

# Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
group_factor <- as.factor(mydata[[GROUP]])

# Вычисление матрицы расстояний
if (DISTANCE == "cosine") {
  # Formula for 1 - Cosine Similarity
  dist_matrix <- designdist(m_abund, method = "1 - J/sqrt(A*B)", terms = "quadratic")
} else {
  # Для стандартных метрик
  dist_matrix <- vegdist(m_abund, method = DISTANCE)
}

# Динамически создаем формулу. 
# Теперь мы используем готовую матрицу расстояний, поэтому формула: dist_matrix ~ GROUP
perm_formula <- as.formula(paste("dist_matrix ~", GROUP))

# ---------------------------------------------------------------------
# Тест PERMANOVA (Многофакторный дисперсионный анализ)
# ---------------------------------------------------------------------
cat("=== PERMANOVA ===\n")
cat("group:", GROUP, "\n")
cat("method:", DISTANCE, "\n")
cat("permutations:", PERMUTATIONS, "\n\n")

# https://www.rdocumentation.org/packages/vegan/topics/adonis
# Аргумент method убран из adonis2, так как мы передаем уже вычисленную матрицу расстояний
permanova_result <- adonis2(perm_formula, data = mydata, permutations = PERMUTATIONS)
print(permanova_result)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
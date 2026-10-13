# source("/mnt/d/git/kgv/utils/Cypresses/r/anosim.R", encoding = "UTF-8")

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
output_file <- paste0("Cypresses/_{Type=ANOSIM}{Group=", GROUP, "}{Distance=", DISTANCE, "}{Permutations=", PERMUTATIONS, "}{Component=", COMPONENT, "}{Value=", VALUE, "}.txt")
sink(output_file, split = FALSE)
# sink("Cypresses/_Anosim.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

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

# ---------------------------------------------------------------------
# Тест ANOSIM (Анализ сходства)
# ---------------------------------------------------------------------
cat("=== ANOSIM ===\n")
cat("Фактор группировки:", TARGET_GROUP, "\n")
cat("Метрика расстояния:", TARGET_DISTANCE, "\n")

anosim_result <- anosim(m_abund, group_factor, distance = TARGET_DISTANCE, permutations = 9999)
print(summary(anosim_result))

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
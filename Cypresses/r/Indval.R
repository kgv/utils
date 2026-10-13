# source("/mnt/d/git/kgv/utils/Cypresses/r/Indval.R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
GROUP <- "Genus"
# GROUP <- "Species"
# GROUP <- "Variety"

# Индекс ассоциации
#
# - Если у вас разное количество образцов в группах (что бывает почти всегда) — выбирайте строго варианты с точкой: "IndVal.g" или "r.g".
#
# FUNCTION <- "IndVal"
# FUNCTION <- "r"
# Модифицированный индекс Дюфрена-Лежандра, скорректированный на разное количество сайтов в группах.
FUNCTION <- "IndVal.g"
# Коэффициент корреляции для бинарных или количественных данных.
# FUNCTION <- "r.g"

# COUNT <- 999
COUNT <- 999

COMPONENT = "Terpene"
# COMPONENT = "Monoterpene"
# COMPONENT = "Sesquiterpene"

VALUE = "PartsPerMillion_Mean"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
output_file <- paste0("Cypresses/_{Type=IndVal}{Group=", GROUP, "}{Function=", FUNCTION, "}{Count=", COUNT, "}{Component=", COMPONENT, "}{Value=", VALUE, "}.txt")

sink(output_file, split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
input_file <- paste0("Cypresses/_{Type=Wide}{Component=", COMPONENT, "}{Value=", VALUE, "}.txt")
mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)
# mydata <- read.csv("Cypresses/_{Type=Wide}{Monoterpene}{Value=PartsPerMillion_Mean}.txt", check.names = FALSE, stringsAsFactors = FALSE)
# mydata <- read.csv("Cypresses/_{Type=Wide}{Sesquiterpene}{Value=PartsPerMillion_Mean}.txt", check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 7-го столбца)
abund <- mydata[, 7:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

m_abund <- as.matrix(abund)

# group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
group_factor <- as.factor(mydata[[GROUP]])

# ---------------------------------------------------------------------
# Процедура IndVal (Компоненты-индикаторы)
# ---------------------------------------------------------------------
cat("=== Результаты IndVal ===\n")
cat("cluster:", GROUP, "\n")
cat("func:", FUNCTION, "\n")
cat("control:", COUNT, "\n")

# This function studies the association between species patterns and combinations of groups of sites.
# https://www.rdocumentation.org/packages/indicspecies/topics/multipatt
ind_val <- multipatt(abund, group_factor, func = FUNCTION, control = how(nperm=COUNT))
ind_val_sum <- summary(ind_val)
print(ind_val_sum)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()

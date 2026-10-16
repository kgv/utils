# source("/mnt/d/g/git/kgv/utils/D/r/multipatt[1].R", encoding = "UTF-8")

library(indicspecies)

FUNCTION <- "r.g"
# FUNCTION <- "IndVal.g"

# Укажите здесь название столбца, по которому нужно группировать данные
# "Ni": Проверяет гипотезу, отличается ли в целом профиль жирных кислот у растений, которые росли без никеля (0), от тех, что росли с никелем (50, 250, 500, 750, 1000).
# "Week": Проверяет гипотезу, изменяется ли состав жирных кислот со временем (стал ли он другими к 5-й неделе по сравнению с 1-й).
# c("Ni", "Week"): Проверит гипотезу, есть ли разница в составе жирных кислот между этими 12 уникальными состояниями.
# GROUP <- "Ni"
# GROUP <- "Week"
GROUP <- c("Ni", "Week")

# KIND = "Leaf"
KIND = "Root"

PERMUTATIONS <- 9999

VALUE = "PartsPerMillion_DryWeight"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
output_file <- paste0("D/_{Type=multipatt}{Kind=", KIND, "}{Function=", FUNCTION, "}{Group=", paste(GROUP, collapse = ","), "}{Permutations=", PERMUTATIONS, "}{Value=", VALUE, "}.txt")
sink(output_file, split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
input_file <- paste0("D/csv/_{Type=Wide}{Kind=", KIND, "}{Value=", VALUE, "}.txt")
mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)

# Оставляем только те строки, где Week равно 5
mydata <- mydata[mydata$Week == 5, ]

# Отделяем матрицу обилий (начиная с 4-го столбца)
abund <- mydata[, 4:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

Ni <- as.numeric(mydata$Ni)
Week <- as.numeric(mydata$Week)

# Создаем пустой вектор для новых групп
macro_groups <- character(length(Ni))

# macro_groups[Ni == 0 & Week == 1] <- "Control_Week1"
# macro_groups[Ni == 50 & Week == 1] <- "Ni50_Week1"
# macro_groups[Ni == 250 & Week == 1] <- "Ni250_Week1"
# macro_groups[Ni == 500 & Week == 1] <- "Ni500_Week1"
# macro_groups[Ni == 750 & Week == 1] <- "Ni750_Week1"
# macro_groups[Ni == 1000 & Week == 1] <- "Ni1000_Week1"
# macro_groups[Ni == 0 & Week == 5] <- "Control_Week5"
# macro_groups[Ni == 50 & Week == 5] <- "Ni50_Week5"
# macro_groups[Ni == 250 & Week == 5] <- "Ni250_Week5"
# macro_groups[Ni == 500 & Week == 5] <- "Ni500_Week5"
# macro_groups[Ni == 750 & Week == 5] <- "Ni750_Week5"
# macro_groups[Ni == 1000 & Week == 5] <- "Ni1000_Week5"

# Control/Low/Medium/High
# macro_groups[Ni == 0 & Week == 1] <- "Control_Week1"
# macro_groups[Ni == 0 & Week == 5] <- "Control_Week5"
# macro_groups[Ni == 50 & Week == 1] <- "NiLow_Week1"
# macro_groups[Ni == 50 & Week == 5] <- "NiLow_Week5"
# macro_groups[Ni == 250 | Ni == 500 & Week == 1] <- "NiMedium_Week1"
# macro_groups[Ni == 250 | Ni == 500 & Week == 5] <- "NiMedium_Week5"
# macro_groups[Ni == 750 | Ni == 1000 & Week == 1] <- "NiHigh_Week1"
# macro_groups[Ni == 750 | Ni == 1000 & Week == 5] <- "NiHigh_Week5"

# Control/Low/Medium/High
# macro_groups[Ni == 0 & Week == 1] <- "Control_Week1"
# macro_groups[Ni == 0 & Week == 5] <- "Control_Week5"
# macro_groups[Ni > 0 & Week == 1] <- "Ni_Week1"
# macro_groups[Ni > 0 & Week == 5] <- "Ni_Week5"

# Week
macro_groups[Ni == 0] <- "Control"
macro_groups[Ni == 50] <- "Ni50"
macro_groups[Ni == 250] <- "Ni250"
macro_groups[Ni == 500] <- "Ni500"
macro_groups[Ni == 750] <- "Ni750"
macro_groups[Ni == 1000] <- "Ni1000"

# Превращаем в фактор
macro_groups <- as.factor(macro_groups)

# ---------------------------------------------------------------------
# Процедура IndVal (Компоненты-индикаторы)
# ---------------------------------------------------------------------
cat("=== IndVal ===\n")
cat("function:", FUNCTION, "\n")
cat("group:", paste(GROUP, collapse = ", "), "\n")
cat("kind:", KIND, "\n")
cat("permutations:", PERMUTATIONS, "\n")
cat("value:", VALUE, "\n")

# multipatt лучше работает с data.frame, передаем abund вместо m_abund
multipatt <- multipatt(x = abund,
                       cluster = macro_groups,
                       func = FUNCTION,
                      #  max.order = 2,
                       allow.negative = TRUE,
                       control = how(nperm=PERMUTATIONS))
multipatt_sum <- summary(multipatt)
print(multipatt_sum)

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
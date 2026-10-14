# source("/mnt/d/g/git/kgv/utils/Cypresses/r/simper.R", encoding = "UTF-8")

library(knitr)
library(vegan)

# Укажите здесь название столбца, по которому нужно группировать данные
GROUP <- "Genus"
# GROUP <- "Species"
# GROUP <- "Variety"

PERMUTATIONS <- 9999

COMPONENT = "Terpene"
COMPONENT = "Monoterpene"
COMPONENT = "Sesquiterpene"

VALUE = "PartsPerMillion_Mean"

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
output_file <- paste0("Cypresses/_{Type=SIMPER}{Group=", GROUP, "}{Permutations=", PERMUTATIONS, "}{Component=", COMPONENT, "}{Value=", VALUE, "}.txt")
sink(output_file, split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
input_file <- paste0("Cypresses/csv/_{Type=Wide}{Component=", COMPONENT, "}{Value=", VALUE, "}.txt")
mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 7-го столбца)
abund <- mydata[, 7:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

m_abund <- as.matrix(abund)

# group_factor <- as.factor(mydata$Species) # Явно делаем фактором
# Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
group_factor <- as.factor(mydata[[GROUP]])

# ---------------------------------------------------------------------
# Процедура SIMPER (Оценка вклада компонентов в различия)
# ---------------------------------------------------------------------
cat("=== SIMPER ===\n")
cat("group:", GROUP, "\n")
cat("permutations:", PERMUTATIONS, "\n")

# какие именно виды (или признаки) вносят наибольший вклад в различия между двумя группами образцов
# https://www.rdocumentation.org/packages/vegan/topics/simper
sim <- simper(m_abund, group_factor, permutations=PERMUTATIONS)
sim_sum <- summary(sim)

# print(sim_sum)

for (comp_name in names(sim_sum)) {
    cat("## Comparison:", comp_name)

    df <- sim_sum[[comp_name]]

    # ФИЛЬТРАЦИЯ
    # Оставляем только те строки, где значение в колонке average больше 0.1
    df <- df[df$average > 0.1, ]

    # Проверяем, остались ли строки после фильтрации. 
    # Если нет, выводим сообщение и переходим к следующему сравнению
    if (nrow(df) == 0) {
        cat("Нет видов с average > 0.1 для этого сравнения.\n\n")
        next 
    }

    # Функция symnum автоматически разобьет p-value на нужные интервалы
    df$signif <- symnum(df$p, corr = FALSE, na = FALSE, cutpoints = c(0, 0.001, 0.01, 0.05, 0.1, 1), symbols = c("***", "**", "*", ".", " "))

    # Округляем длинные числа до 4 знаков после запятой
    is_num <- sapply(df, is.numeric)
    df[is_num] <- lapply(df[is_num], round, 4)

    # Выводим красивую таблицу
    print(kable(df, format = "markdown"))
    cat("\n")
}

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
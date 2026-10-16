# source("/mnt/d/g/git/kgv/utils/D/r/simper[1].R", encoding = "UTF-8")

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

# KIND = "Leaf"
KIND <- "Root"

PERMUTATIONS <- 9999

VALUE <- "PartsPerMillion_DryWeight"

# Укажите нужную неделю (1 или 5).
# Если хотите проанализировать всё без фильтров, укажите NULL
# TARGET_WEEK <- NULL
TARGET_WEEK <- 1
# TARGET_WEEK <- 5

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
output_file <- paste0(
    "D/_{Type=SIMPER}{Kind=",
    KIND,
    "}{Group=",
    paste(GROUP, collapse = ","),
    "}{Permutations=",
    PERMUTATIONS,
    "}{Value=",
    VALUE,
    "}.txt"
)
sink(output_file, split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(42)

# Загрузка данных
input_file <- paste0(
    "D/csv/_{Type=Wide}{Kind=",
    KIND,
    "}{Value=",
    VALUE,
    "}.txt"
)
mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)

if (!is.null(TARGET_WEEK)) {
    # Оставляем только те строки, где Week равно TARGET_WEEK
    mydata <- mydata[mydata$Week == TARGET_WEEK, ]
}

# Отделяем матрицу обилий (начиная с 4-го столбца)
abund <- mydata[, 4:ncol(mydata)]

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)

# Применить трансформацию log1p к матрице сообщества
abund <- log1p(abund)

m_abund <- as.matrix(abund)

# Создаем комбинированный фактор для графиков, SIMPER и IndVal
if (length(GROUP) > 1) {
  # Функция interaction() склеит значения. Если Ni=50 и Week=1, получится группа "50.1"
  macro_groups <- interaction(mydata[, GROUP], drop = TRUE)
} else {
  # Динамически получаем фактор (используем двойные скобки [[ ]] для текста)
  macro_groups <- as.factor(mydata[[GROUP]])
}

# Ni <- as.numeric(mydata$Ni)
# Week <- as.numeric(mydata$Week)

# # Создаем пустой вектор для новых групп
# macro_groups <- character(nrow(mydata))

# # macro_groups[Ni == 0 & Week == 1] <- "Control_Week1"
# # macro_groups[Ni == 50 & Week == 1] <- "Ni50_Week1"
# # macro_groups[Ni == 250 & Week == 1] <- "Ni250_Week1"
# # macro_groups[Ni == 500 & Week == 1] <- "Ni500_Week1"
# # macro_groups[Ni == 750 & Week == 1] <- "Ni750_Week1"
# # macro_groups[Ni == 1000 & Week == 1] <- "Ni1000_Week1"
# # macro_groups[Ni == 0 & Week == 5] <- "Control_Week5"
# # macro_groups[Ni == 50 & Week == 5] <- "Ni50_Week5"
# # macro_groups[Ni == 250 & Week == 5] <- "Ni250_Week5"
# # macro_groups[Ni == 500 & Week == 5] <- "Ni500_Week5"
# # macro_groups[Ni == 750 & Week == 5] <- "Ni750_Week5"
# # macro_groups[Ni == 1000 & Week == 5] <- "Ni1000_Week5"

# # Control/Low/Medium/High
# # macro_groups[Ni == 0 & Week == 1] <- "Control_Week1"
# # macro_groups[Ni == 0 & Week == 5] <- "Control_Week5"
# # macro_groups[Ni == 50 & Week == 1] <- "NiLow_Week1"
# # macro_groups[Ni == 50 & Week == 5] <- "NiLow_Week5"
# # macro_groups[Ni == 250 | Ni == 500 & Week == 1] <- "NiMedium_Week1"
# # macro_groups[Ni == 250 | Ni == 500 & Week == 5] <- "NiMedium_Week5"
# # macro_groups[Ni == 750 | Ni == 1000 & Week == 1] <- "NiHigh_Week1"
# # macro_groups[Ni == 750 | Ni == 1000 & Week == 5] <- "NiHigh_Week5"

# # Control/Low/Medium/High
# # macro_groups[Ni == 0 & Week == 1] <- "Control_Week1"
# # macro_groups[Ni == 0 & Week == 5] <- "Control_Week5"
# # macro_groups[Ni > 0 & Week == 1] <- "Ni_Week1"
# # macro_groups[Ni > 0 & Week == 5] <- "Ni_Week5"

# # # Week
# # macro_groups[Ni == 0] <- "Control"
# # macro_groups[Ni == 50] <- "Ni50"
# # macro_groups[Ni == 250] <- "Ni250"
# # macro_groups[Ni == 500] <- "Ni500"
# # macro_groups[Ni == 750] <- "Ni750"
# # macro_groups[Ni == 1000] <- "Ni1000"

# if (!is.null(TARGET_WEEK)) {
#     macro_groups[Ni == 0 & Week == TARGET_WEEK] <- paste0(
#         "Control_Week",
#         TARGET_WEEK
#     )
#     macro_groups[Ni == 50 & Week == TARGET_WEEK] <- paste0(
#         "Ni50_Week",
#         TARGET_WEEK
#     )
#     macro_groups[Ni == 250 & Week == TARGET_WEEK] <- paste0(
#         "Ni250_Week",
#         TARGET_WEEK
#     )
#     macro_groups[Ni == 500 & Week == TARGET_WEEK] <- paste0(
#         "Ni500_Week",
#         TARGET_WEEK
#     )
#     macro_groups[Ni == 750 & Week == TARGET_WEEK] <- paste0(
#         "Ni750_Week",
#         TARGET_WEEK
#     )
#     macro_groups[Ni == 1000 & Week == TARGET_WEEK] <- paste0(
#         "Ni1000_Week",
#         TARGET_WEEK
#     )
#     # ВАЖНО: Строки с ДРУГОЙ неделей останутся пустыми.
#     # Чтобы SIMPER не сошел с ума, назовем их "Ignore" (мы их потом отфильтруем)
#     # macro_groups[Week != TARGET_WEEK] <- "Ignore"
# } else {
#     macro_groups[Ni == 0 & Week == 1] <- "Control_Week1"
#     macro_groups[Ni == 50 & Week == 1] <- "Ni50_Week1"
#     macro_groups[Ni == 250 & Week == 1] <- "Ni250_Week1"
#     macro_groups[Ni == 500 & Week == 1] <- "Ni500_Week1"
#     macro_groups[Ni == 750 & Week == 1] <- "Ni750_Week1"
#     macro_groups[Ni == 1000 & Week == 1] <- "Ni1000_Week1"
#     macro_groups[Ni == 0 & Week == 5] <- "Control_Week5"
#     macro_groups[Ni == 50 & Week == 5] <- "Ni50_Week5"
#     macro_groups[Ni == 250 & Week == 5] <- "Ni250_Week5"
#     macro_groups[Ni == 500 & Week == 5] <- "Ni500_Week5"
#     macro_groups[Ni == 750 & Week == 5] <- "Ni750_Week5"
#     macro_groups[Ni == 1000 & Week == 5] <- "Ni1000_Week5"
# }

# # Превращаем в фактор
# macro_groups <- as.factor(macro_groups)

# ---------------------------------------------------------------------
# Процедура SIMPER (Оценка вклада компонентов в различия)
# ---------------------------------------------------------------------
cat("=== SIMPER ===\n")
cat("group:", paste(GROUP, collapse = ", "), "\n")
cat("kind:", KIND, "\n")
cat("permutations:", PERMUTATIONS, "\n")
cat("value:", VALUE, "\n\n")

sim <- simper(m_abund, macro_groups)
sim_sum <- summary(sim)

# print(sim_sum)

for (comp_name in names(sim_sum)) {
    # if (!grepl("*\\.5_.*\\.5$", comp_name)) {
    #     next
    # }
    # Если константа задана, применяем фильтр
    if (!is.null(TARGET_WEEK)) {
        # Динамически создаем регулярное выражение.
        # Если TARGET_WEEK = 5, pattern станет "Week5_.*Week5$"
        # pattern <- paste0(".*Week", TARGET_WEEK, "_.*Week", TARGET_WEEK, "$")
        pattern <- paste0(".*\\.", TARGET_WEEK, "_.*\\.", TARGET_WEEK, "$")
        if (!grepl(pattern, comp_name)) {
            next
        }
    }

    cat("## Comparison:", comp_name)

    df <- sim_sum[[comp_name]]

    # ФИЛЬТРАЦИЯ
    # Оставляем только те строки, где значение в колонке average больше 0.1
    # df <- df[df$average > 0.1, ]

    # Проверяем, остались ли строки после фильтрации.
    # Если нет, выводим сообщение и переходим к следующему сравнению
    # if (nrow(df) == 0) {
    #     cat("Нет видов с average > 0.1 для этого сравнения.\n\n")
    #     next
    # }

    # Функция symnum автоматически разобьет p-value на нужные интервалы
    df$signif <- symnum(
        df$p,
        corr = FALSE,
        na = FALSE,
        cutpoints = c(0, 0.001, 0.01, 0.05, 0.1, 1),
        symbols = c("***", "**", "*", ".", " ")
    )

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

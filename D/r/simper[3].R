# source("/mnt/d/g/git/kgv/utils/D/r/simper[3].R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# =====================================================================
# НАСТРОЙКИ
# =====================================================================
GROUP <- c("Ni", "Week")
PERMUTATIONS <- 9999
VALUE <- "PartsPerMillion_DryWeight"

# Массивы для перебора
TARGET_ORGANS <- c(
    "Leaf",
    "Root"
)
TARGET_TRANSFORMS <- c(
    "None",
    # "log1p",
    "log2"
)
TARGET_WEEKS <- c(
    "All",
    "1",
    "5"
)

# =====================================================================
# ОСНОВНОЙ ЦИКЛ ПО ВСЕМ КОМБИНАЦИЯМ
# =====================================================================
for (current_organ in TARGET_ORGANS) {
    # Загрузка данных для текущего типа (Leaf или Root)
    input_file <- paste0(
        "D/csv/_{Type=Wide}{Organ=",
        current_organ,
        "}{Value=",
        VALUE,
        "}.txt"
    )
    mydata_raw <- read.csv(
        input_file,
        check.names = FALSE,
        stringsAsFactors = FALSE
    )

    for (current_week in TARGET_WEEKS) {
        for (current_transform in TARGET_TRANSFORMS) {
            # Формируем уникальное имя файла
            output_file <- paste0(
                "D/_{Type=SIMPER}{Organ=",
                current_organ,
                "}{Value=",
                VALUE,
                "}{Week=",
                current_week,
                "}{Group=",
                paste(GROUP, collapse = ","),
                "}{Permutations=",
                PERMUTATIONS,
                "}{Transform=",
                current_transform,
                "}.txt"
            )

            # НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
            sink(output_file, split = FALSE)

            # Копируем исходные данные для текущей итерации
            mydata <- mydata_raw

            # Фильтрация по неделе
            if (current_week != "All") {
                mydata <- mydata[mydata$Week == as.numeric(current_week), ]
            }

            # Отделяем матрицу обилий (начиная с 4-го столбца)
            abund <- mydata[, 4:ncol(mydata)]
            abund <- as.data.frame(
                lapply(abund, as.numeric),
                check.names = FALSE
            )

            # Применение трансформации
            if (current_transform == "log1p") {
                abund <- log1p(abund)
            } else if (current_transform == "log2") {
                # Примечание: если в данных есть нули, log2(0) даст -Inf.
                # Убедитесь, что данные это позволяют, либо используйте log2(abund + 1)
                abund <- log2(abund + 1)
            }

            m_abund <- as.matrix(abund)

            # Создаем комбинированный фактор
            if (length(GROUP) > 1) {
                macro_groups <- interaction(mydata[, GROUP], drop = TRUE)
            } else {
                macro_groups <- as.factor(mydata[[GROUP]])
            }

            # ---------------------------------------------------------------------
            # Процедура SIMPER
            # ---------------------------------------------------------------------
            cat("# SIMPER\n\n")
            cat("- **group**:", paste(GROUP, collapse = ", "), "\n")
            cat("- **organ**:", current_organ, "\n")
            cat("- **permutations**:", PERMUTATIONS, "\n")
            cat("- **transform**:", current_transform, "\n")
            cat("- **value**:", VALUE, "\n")
            cat("- **week**:", current_week, "\n\n")

            # Фиксируем генератор случайных чисел
            set.seed(42)

            sim <- simper(comm = m_abund, group = macro_groups)
            sim_sum <- summary(sim)

            for (comp_name in names(sim_sum)) {
                cat("## Comparison:", comp_name)

                df <- sim_sum[[comp_name]]

                df$signif <- symnum(
                    df$p,
                    corr = FALSE,
                    na = FALSE,
                    cutpoints = c(0, 0.001, 0.01, 0.05, 0.1, 1),
                    symbols = c("***", "**", "*", ".", " ")
                )

                is_num <- sapply(df, is.numeric)
                df[is_num] <- lapply(df[is_num], round, 4)

                print(kable(df, format = "markdown"))
                cat("\n")
            }

            # КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
            sink()

            # Вывод в консоль для отслеживания прогресса
            message(sprintf(
                "Finished: Organ=%s, Week=%s, Transform=%s",
                current_organ,
                current_week,
                current_transform
            ))
        }
    }
}

# source("/mnt/d/git/kgv/utils/D/r/simper[4].R", encoding = "UTF-8")

library(indicspecies)
library(knitr)
library(vegan)

# =====================================================================
# НАСТРОЙКИ
# =====================================================================
GROUP <- c("Ni", "Week")

TARGET_ORGANS <- c(
    "Leaf",
    "Root"
)
TARGET_VALUES <- c(
    # "Percent_Area",
    "PartsPerMillion_DryWeight"
)
TARGET_WEEKS <- c(
    # "[1]",
    # "[5]",
    "[1,5]"
)

TARGET_PERMUTATIONS <- c(
    9999
)
TARGET_TRANSFORMATIONS <- c(
    # "[log1p]",
    # "[log2]",
    "[]"
)

# =====================================================================
# ОСНОВНОЙ ЦИКЛ ПО ВСЕМ КОМБИНАЦИЯМ
# =====================================================================
for (current_organ in TARGET_ORGANS) {
    for (current_value in TARGET_VALUES) {
        for (current_weeks in TARGET_WEEKS) {
            # Загрузка входных данных
            input_file <- paste0(
                "D/csv/_{Type=Wide}{Organ=",
                current_organ,
                "}{Value=",
                current_value,
                "}{Weeks=",
                current_weeks,
                "}.txt"
            )
            mydata_raw <- read.csv(
                input_file,
                check.names = FALSE,
                stringsAsFactors = FALSE
            )
            for (current_permutations in TARGET_PERMUTATIONS) {
                for (current_transformation in TARGET_TRANSFORMATIONS) {
                    # Формируем уникальное имя файла
                    output_file <- paste0(
                        "D/csv/_{Type=SIMPER}{Organ=",
                        current_organ,
                        "}{Value=",
                        current_value,
                        "}{Weeks=",
                        current_weeks,
                        "}{Permutations=",
                        current_permutations,
                        "}{Transformations=",
                        current_transformation,
                        "}.txt"
                    )

                    # НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
                    sink(output_file, split = FALSE)

                    # Копируем исходные данные для текущей итерации
                    mydata <- mydata_raw

                    # Отделяем матрицу обилий (начиная с 4-го столбца)
                    abund <- mydata[, 4:ncol(mydata)]
                    abund <- as.data.frame(
                        lapply(abund, as.numeric),
                        check.names = FALSE
                    )

                    # Применение трансформации
                    if (current_transformation == "[log1p]") {
                        abund <- log1p(abund)
                    } else if (current_transformation == "[log2]") {
                        # Примечание: если в данных есть нули, log2(0) даст -Inf.
                        # Убедитесь, что данные это позволяют, либо используйте log2(abund + 1)
                        abund <- log2(abund + 1)
                    }

                    m_abund <- as.matrix(abund)

                    # Создаем комбинированный фактор
                    if (length(GROUP) > 1) {
                        macro_groups <- interaction(
                            mydata[, GROUP],
                            drop = TRUE
                        )
                    } else {
                        macro_groups <- as.factor(mydata[[GROUP]])
                    }

                    # ---------------------------------------------------------------------
                    # Процедура SIMPER
                    # ---------------------------------------------------------------------
                    cat("# SIMPER\n\n")
                    cat("- **group**:", paste(GROUP, collapse = ", "), "\n")
                    cat("- **organ**:", current_organ, "\n")
                    cat("- **permutation**:", current_permutations, "\n")
                    cat("- **transformation**:", current_transformation, "\n")
                    cat("- **value**:", current_value, "\n")
                    cat("- **weeks**:", current_weeks, "\n\n")

                    # Фиксируем генератор случайных чисел
                    set.seed(42)

                    sim <- simper(comm = m_abund, group = macro_groups)
                    sim_sum <- summary(sim)

                    sim_all <- dplyr::bind_rows(
                        lapply(sim_sum, as.data.frame),
                        .id = "groups"
                    )
                    write.csv(
                        sim_all,
                        file = output_file,
                        row.names = TRUE
                    )

                    # for (comp_name in names(sim_sum)) {
                    #     cat("## Comparison:", comp_name)

                    #     df <- sim_sum[[comp_name]]

                    #     df$significance <- symnum(
                    #         df$p,
                    #         corr = FALSE,
                    #         na = FALSE,
                    #         cutpoints = c(0, 0.001, 0.01, 0.05, 0.1, 1),
                    #         symbols = c("***", "**", "*", ".", " ")
                    #     )
                    #     # Add contribution
                    #     df$cumsum_diff <- c(df$cumsum[1], diff(df$cumsum)) * 100
                    #     df <- df[, c(
                    #         names(df)[0],
                    #         "average",
                    #         "sd",
                    #         "ratio",
                    #         "ava",
                    #         "avb",
                    #         "cumsum_diff",
                    #         "cumsum",
                    #         "p",
                    #         "significance"
                    #     )]

                    #     is_num <- sapply(df, is.numeric)
                    #     df[is_num] <- lapply(df[is_num], round, 4)

                    #     # print(kable(df, format = "markdown"))
                    #     print(kable(df, format = "markdown"))
                    #     cat("\n")
                    # }

                    # КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
                    sink()

                    # Вывод в консоль для отслеживания прогресса
                    message(sprintf(
                        "Finished: Organ=%s, Weeks=%s, Transformation=%s",
                        current_organ,
                        current_weeks,
                        current_transformation
                    ))
                }
            }
        }
    }
}

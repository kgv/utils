# source("/mnt/d/g/git/kgv/utils/Cypresses/r/indval[1].R", encoding = "UTF-8")

library(indicspecies)

# =====================================================================
# Settings
# =====================================================================
TARGET_COMPONENTS <- c(
    # "Monoterpene",
    # "Sesquiterpene",
    "Terpene"
)
TARGET_VALUES <- c(
    "Percent_Mean",
    "PartsPerMillion_Mean"
)

TARGET_ADJUSTS <- c(
    "BH",
    # "BY",
    "none"
)
# Индекс ассоциации
#
# - Если у вас разное количество образцов в группах (что бывает почти всегда) — выбирайте строго варианты с точкой: "IndVal.g" или "r.g".
#
# FUNCTION <- "IndVal"
# FUNCTION <- "r"
# Модифицированный индекс Дюфрена-Лежандра, скорректированный на разное количество сайтов в группах.
# FUNCTION <- "IndVal.g"
# Коэффициент корреляции для бинарных или количественных данных.
# FUNCTION <- "r.g"
TARGET_FUNCTIONS <- c(
    "IndVal.g",
    "r.g"
)
TARGET_GROUPS <- c(
    # "Genus"
    "Species"
    # "Variety"
)
TARGET_PERMUTATIONS <- c(
    999
    # 9999
)
TARGET_TRANSFORMATIONS <- c(
    # "[log1p]",
    # "[log2]",
    "[]"
)

# =====================================================================
# Main loop
# =====================================================================
for (current_component in TARGET_COMPONENTS) {
    for (current_value in TARGET_VALUES) {
        # Загрузка входных данных
        input_file <- paste0(
            "Cypresses/csv/_{Type=Wide}{Component=",
            current_component,
            "}{Value=",
            current_value,
            "}.txt"
        )
        mydata_raw <- read.csv(
            input_file,
            check.names = FALSE,
            stringsAsFactors = FALSE
        )
        for (current_adjust in TARGET_ADJUSTS) {
            for (current_function in TARGET_FUNCTIONS) {
                for (current_group in TARGET_GROUPS) {
                    for (current_permutations in TARGET_PERMUTATIONS) {
                        for (current_transformations in TARGET_TRANSFORMATIONS) {
                            # Формируем уникальное имя файла
                            output_file <- paste0(
                                "Cypresses/txt/_{Type=IndVal}{Component=",
                                current_component,
                                "}{Value=",
                                current_value,
                                "}{Adjust=",
                                current_adjust,
                                "}{Function=",
                                current_function,
                                "}{Group=",
                                current_group,
                                "}{Permutations=",
                                current_permutations,
                                "}{Transformations=",
                                current_transformations,
                                "}.txt"
                            )

                            # Копируем исходные данные для текущей итерации
                            mydata <- mydata_raw

                            # Отделяем матрицу обилий (начиная с 7-го столбца)
                            abund <- mydata[, 7:ncol(mydata)]

                            # Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
                            abund <- as.data.frame(
                                lapply(abund, as.numeric),
                                check.names = FALSE
                            )

                            # Применение трансформации
                            if (current_transformations == "[log1p]") {
                                abund <- log1p(abund)
                            } else if (current_transformations == "[log2]") {
                                # Примечание: если в данных есть нули, log2(0) даст -Inf.
                                # Убедитесь, что данные это позволяют, либо используйте log2(abund + 1)
                                abund <- log2(abund + 1)
                            }

                            m_abund <- as.matrix(abund)

                            # Создаем комбинированный фактор
                            group <- as.factor(mydata[[current_group]])

                            # Фиксируем генератор случайных чисел
                            set.seed(42)

                            sink(output_file, split = FALSE)
                            tryCatch(
                                {
                                    # IndVal (Компоненты-индикаторы)
                                    # This function studies the association between species patterns and combinations of groups of sites.
                                    # https://www.rdocumentation.org/packages/indicspecies/topics/multipatt
                                    multipatt_result <- multipatt(
                                        abund,
                                        cluster = group,
                                        func = current_function,
                                        control = how(
                                            nperm = current_permutations
                                        ),
                                        allow.negative = TRUE,
                                    )
                                    # print(multipatt_result)

                                    # Коррекция на множественное тестирование (bonferroni, fdr)
                                    multipatt_result$sign$p.value <- p.adjust(
                                        multipatt_result$sign$p.value,
                                        method = current_adjust
                                    )

                                    multipatt_summary <- summary(
                                        multipatt_result
                                    )
                                    print(multipatt_summary)
                                },
                                error = function(e) {
                                    cat("Error:\n")
                                    print(e)
                                },
                                finally = {
                                    sink()
                                }
                            )

                            # Вывод в консоль для отслеживания прогресса
                            message(paste0("Finished:", output_file))
                        }
                    }
                }
            }
        }
    }
}

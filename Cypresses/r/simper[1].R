# source("/mnt/d/g/git/kgv/utils/Cypresses/r/simper[1].R", encoding = "UTF-8")

library(vegan)

# =====================================================================
# Settings
# =====================================================================
TARGET_COMPONENTS <- c(
    "Monoterpene",
    "Sesquiterpene",
    "Terpene"
)
TARGET_VALUES <- c(
    "Percent_Mean",
    "PartsPerMillion_Mean"
)

TARGET_GROUPS <- c(
    "Genus",
    "Species",
    "Variety"
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
        for (current_group in TARGET_GROUPS) {
            for (current_permutations in TARGET_PERMUTATIONS) {
                for (current_transformations in TARGET_TRANSFORMATIONS) {
                    # Формируем уникальное имя файла
                    output_file <- paste0(
                        "Cypresses/csv/_{Type=SIMPER}{Component=",
                        current_component,
                        "}{Value=",
                        current_value,
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
                            # simper

                            sim <- simper(comm = m_abund, group = group)
                            sim_sum <- summary(sim)

                            sim_all <- dplyr::bind_rows(
                                lapply(sim_sum, as.data.frame),
                                .id = "id"
                            )
                            write.csv(
                                sim_all,
                                file = output_file,
                                row.names = TRUE
                            )
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

# source("/mnt/d/git/kgv/utils/Cypresses/r/anosim[1].R", encoding = "UTF-8")

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
    # "Percent_Mean",
    "PartsPerMillion_Mean"
)

# https://www.rdocumentation.org/packages/vegan/topics/vegdist
# https://vegandevs.github.io/vegan/reference/designdist.html
TARGET_DISTANCES <- c(
    # "manhattan",
    # "euclidean",
    # "canberra",
    # "clark",
    "bray"
    # "kulczynski",
    # "jaccard",
    # "gower",
    # "altGower",
    # "morisita",
    # "horn",
    # "mountford",
    # "raup",
    # "binomial",
    # "chao",
    # "cao",
    # "mahalanobis",
    # "chisq",
    # "chord",
    # "hellinger",
    # "aitchison",
    # "robust.aitchison",
    # "cosine"
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
        for (current_distance in TARGET_DISTANCES) {
            for (current_group in TARGET_GROUPS) {
                for (current_permutations in TARGET_PERMUTATIONS) {
                    for (current_transformations in TARGET_TRANSFORMATIONS) {
                        # Формируем уникальное имя файла
                        output_file <- paste0(
                            "Cypresses/txt/_{Type=ANOSIM}{Component=",
                            current_component,
                            "}{Value=",
                            current_value,
                            "}{Distance=",
                            current_distance,
                            "}{Group=",
                            current_group,
                            "}{Permutations=",
                            current_permutations,
                            "}{Transformations=",
                            current_transformations,
                            "}.txt"
                        )

                        # НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
                        sink(output_file, split = FALSE)

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

                        # Вычисление матрицы расстояний
                        if (current_distance == "cosine") {
                            # Formula for 1 - Cosine Similarity
                            dist_matrix <- designdist(
                                m_abund,
                                method = "1 - J/sqrt(A*B)",
                                terms = "quadratic"
                            )
                        } else {
                            # Для стандартных метрик
                            dist_matrix <- vegdist(
                                m_abund,
                                method = current_distance
                            )
                        }

                        # Фиксируем генератор случайных чисел
                        set.seed(42)

                        # https://www.rdocumentation.org/packages/vegan/topics/anosim
                        anosim_result <- anosim(
                            dist_matrix,
                            grouping = group,
                            permutations = 9999
                        )
                        print(summary(anosim_result))

                        # КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
                        sink()

                        # Вывод в консоль для отслеживания прогресса
                        message(paste0("Finished:", output_file))
                    }
                }
            }
        }
    }
}

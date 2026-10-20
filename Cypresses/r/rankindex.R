# source("/mnt/d/git/kgv/utils/Cypresses/r/rankindex.R", encoding = "UTF-8")

library(cluster)
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
TARGET_TRANSFORMATIONS <- c(
    # "[log1p]",
    # "[log2]",
    "[]"
)

INDICES <- list(
    # Стандартные дистанции из vegdist оборачиваем в функции
    Bray = function(x) vegdist(x, method = "bray"),
    Euclidean = function(x) vegdist(x, method = "euclidean"),
    Manhattan = function(x) vegdist(x, method = "manhattan"),
    Canberra = function(x) vegdist(x, method = "canberra"),
    Kulczynski = function(x) vegdist(x, method = "kulczynski"),
    Jaccard = function(x) vegdist(x, method = "jaccard"),
    Gower = function(x) cluster:::daisy(x, "gower"),
    AltGower = function(x) vegdist(x, method = "altGower"),
    Chord = function(x) vegdist(x, method = "chord"),
    Hellinger = function(x) vegdist(x, method = "hellinger"),
    # Cosine Distance
    Cosine = function(x) {
        designdist(x, method = "1-J/sqrt(A*B)", terms = "quadratic")
    }
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
            for (current_transformations in TARGET_TRANSFORMATIONS) {
                # Формируем уникальное имя файла
                output_file <- paste0(
                    "Cypresses/txt/_{Type=rankindex}{Component=",
                    current_component,
                    "}{Value=",
                    current_value,
                    "}{Group=",
                    current_group,
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
                # Проверяем, не появились ли NA после конвертации
                if (any(is.na(abund))) {
                    cat(
                        "ВНИМАНИЕ: В матрице abund есть пропущенные значения (NA)! Заменяем их на 0.\n"
                    )
                    abund[is.na(abund)] <- 0
                }

                # Применение трансформации
                if (current_transformations == "[log1p]") {
                    abund <- log1p(abund)
                } else if (current_transformations == "[log2]") {
                    # Примечание: если в данных есть нули, log2(0) даст -Inf.
                    # Убедитесь, что данные это позволяют, либо используйте log2(abund + 1)
                    abund <- log2(abund + 1)
                }

                m_abund <- as.matrix(abund)

                # Создаем фактор
                group <- as.factor(mydata[[current_group]])
                # Превращаем категориальный фактор в матрицу дистанций (0 - одна
                # группа, 1 - разные) daisy с метрикой gower идеально
                # справляется с факторами
                group_dist <- cluster::daisy(
                    data.frame(group = group),
                    metric = "gower"
                )

                # Фиксируем генератор случайных чисел
                set.seed(42)

                sink(output_file, split = FALSE)
                tryCatch(
                    {
                        # https://www.rdocumentation.org/packages/vegan/topics/rankindex
                        rankindex_result <- rankindex(
                            grad = group,
                            veg = abund,
                            indices = INDICES,
                            method = "spearman"
                        )

                        # Сортируем результаты по убыванию (от лучшей к худшей)
                        sorted_distances <- sort(
                            rankindex_result,
                            decreasing = TRUE
                        )
                        print(sorted_distances)
                    },
                    error = function(e) {
                        cat("Произошла ошибка при вычислении:\n")
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

# mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)

# # Подготавливаем "градиент среды" (ваши факторы) Поскольку Ni измеряется в
# # сотнях (0-1000), а Week в единицах (1-5), их ОБЯЗАТЕЛЬНО нужно
# # стандартизировать (scale), иначе Ni "задавит" Week.
# env_data <- scale(mydata[, c("Ni", "Week")])

# # Отделяем матрицу обилий (начиная с 7-го столбца)
# abund <- mydata[, 7:ncol(mydata)]
# abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)
# # Проверяем, не появились ли NA после конвертации
# if (any(is.na(abund))) {
#   cat(
#     "ВНИМАНИЕ: В матрице abund есть пропущенные значения (NA)! Заменяем их на 0.\n"
#   )
#   abund[is.na(abund)] <- 0
# }

# # dist_candidates <- c(
# #     "bray",        # Брей-Куртис (классика для экологии и биохимии)
# #     "euclidean",   # Евклидово расстояние
# #     "manhattan",   # Манхэттенское расстояние
# #     "canberra",    # Канберра (хорошо улавливает изменения в редких ЖК)
# #     "kulczynski",  # Кульчинский (отличная альтернатива Брею)
# #     "jaccard",     # Жаккар (в vegan он адаптирован для количественных данных)
# #     "gower",       # Гауэр
# #     "altGower",    # Альтернативный Гауэр
# #     "chord",       # Хордовое расстояние
# #     "hellinger",   # Хеллинджер (очень рекомендуется для композиционных данных!)
# #     # "aitchison",
# #     "binomial",
# #     # "cao",
# #     # "chao",
# #     "chisq",
# #     "chord",
# #     "clark",
# #     "horn",
# #     "mahalanobis",
# #     # "morisita",
# #     # "mountford",
# #     "raup"
# # )
# # Gower=function(x) cluster:::daisy(x, "gower"),
# dist_functions <- list(
#   # Стандартные дистанции из vegdist оборачиваем в функции
#   Bray = function(x) vegdist(x, method = "bray"),
#   Euclidean = function(x) vegdist(x, method = "euclidean"),
#   Manhattan = function(x) vegdist(x, method = "manhattan"),
#   Canberra = function(x) vegdist(x, method = "canberra"),
#   Kulczynski = function(x) vegdist(x, method = "kulczynski"),
#   Jaccard = function(x) vegdist(x, method = "jaccard"),
#   Gower = function(x) cluster:::daisy(x, "gower"),
#   AltGower = function(x) vegdist(x, method = "altGower"),
#   Chord = function(x) vegdist(x, method = "chord"),
#   Hellinger = function(x) vegdist(x, method = "hellinger"),
#   # Cosine Distance
#   Cosine = function(x) {
#     designdist(x, method = "1-J/sqrt(A*B)", terms = "quadratic")
#   }
# )

# # Запускаем rankindex
# # - grad - наши факторы среды
# # - veg - наша матрица обилий (ЖК)
# # - indices - список дистанций
# cat("=== rankindex ===\n")
# best_distances <- rankindex(
#   grad = env_data,
#   veg = abund,
#   indices = dist_functions,
#   method = "spearman"
# )

# # Сортируем результаты по убыванию (от лучшей к худшей)
# sorted_distances <- sort(best_distances, decreasing = TRUE)

# # Выводим на экран
# print(sorted_distances)

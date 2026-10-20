# source("/mnt/d/g/git/kgv/utils/Cypresses/r/nmds[0].R", encoding = "UTF-8")

# =====================================================================
# НАСТРОЙКИ
# =====================================================================
TARGET_COMPONENTS <- c(
    # "Monoterpene",
    "Sesquiterpene"
    # "Terpene"
)
TARGET_VALUES <- c(
    # "Percent_Mean",
    "PartsPerMillion_Mean"
)

TARGET_GROUPS <- c(
    # "Genus",
    "Species"
    # "Variety"
)
TARGET_PERMUTATIONS <- c(
    9999
)
TARGET_TRANSFORMATIONS <- c(
    # "[log1p]",
    # "[log2]",
    "[]"
)

for (current_component in TARGET_COMPONENTS) {
    for (current_value in TARGET_VALUES) {
        for (current_group in TARGET_GROUPS) {
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

            # Копируем исходные данные для текущей итерации
            mydata <- mydata_raw

            # Отделяем матрицу обилий (начиная с 4-го столбца)
            abund <- mydata[, 7:ncol(mydata)]

            # ИСПРАВЛЕНИЕ: Заменяем все пропущенные значения (NA) на 0.
            # Пакет vegan не работает с NA при расчете дистанции Брея-Кертиса.
            abund[is.na(abund)] <- 0

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

            # group_factor <- as.factor(mydata$Variety) # Явно делаем фактором
            # Создаем комбинированный фактор
            group_factor <- as.factor(mydata[[current_group]])

            nmds <- metaMDS(
                m_abund,
                distance = "bray",
                k = 2,
                autotransform = FALSE,
                trymax = 100
            )

            num_groups <- length(levels(group_factor))
            my_colors <- 1:num_groups

            # ВАЖНО: Увеличиваем правое поле графика (mar), чтобы влезла легенда,
            # и разрешаем рисовать за пределами осей (xpd = TRUE)
            par(mar = c(5, 4, 4, 10), xpd = TRUE)

            plot(nmds, type = "n", main = "NMDS Ordination of TAGs")
            points(
                nmds,
                display = "sites",
                pch = 16,
                col = my_colors[as.numeric(group_factor)]
            )
            ordihull(
                nmds,
                groups = group_factor,
                label = FALSE,
                col = my_colors
            )

            # Размещаем легенду справа за пределами графика (inset = c(-0.4, 0) сдвигает её вправо)
            legend(
                "topright",
                inset = c(-0.6, 0),
                legend = levels(group_factor),
                col = my_colors,
                pch = 16,
                lty = 1,
                title = "Variety",
                bty = "n",
                cex = 0.8
            )
        }
    }
}

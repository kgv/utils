# source("/mnt/d/g/git/kgv/utils/Cypresses/r/Analyze[1].R", encoding = "UTF-8")

# install.packages("indicspecies")
# install.packages("ggplot2")
# install.packages("plotly")

library(dplyr)
library(ggplot2)
library(indicspecies)
library(knitr)
library(plotly)
library(vegan)

# =====================================================================
# ШАГ 2: СТАТИСТИЧЕСКИЙ АНАЛИЗ
# =====================================================================

# =====================================================================
# НАЧАЛО ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink("Cypresses/_Output.txt", split = FALSE)

# Фиксируем генератор случайных чисел
set.seed(1234)

# 2.1 Загрузка данных
mydata <- read.csv("Cypresses/_Wide.txt", check.names = FALSE, stringsAsFactors = FALSE)

# Отделяем матрицу обилий (начиная с 7-го столбца)
abund <- mydata[, 7:ncol(mydata)]

# ИСПРАВЛЕНИЕ: Заменяем все пропущенные значения (NA) на 0.
# Пакет vegan не работает с NA при расчете дистанции Брея-Кертиса.
abund[is.na(abund)] <- 0

# Убедимся, что все данные числовые (на случай скрытых ошибок в файле)
abund <- as.data.frame(lapply(abund, as.numeric))

m_abund <- as.matrix(abund)
group_factor <- as.factor(mydata$Variety) # Явно делаем фактором

# ---------------------------------------------------------------------
# 2.2 Тест ANOSIM (Анализ сходства)
# ---------------------------------------------------------------------
cat("=== Результаты ANOSIM ===\n")
ano <- anosim(m_abund, group_factor, distance = "bray", permutations = 9999)
print(summary(ano))

# ---------------------------------------------------------------------
# 2.3 Тест PERMANOVA (Многофакторный дисперсионный анализ)
# ---------------------------------------------------------------------
cat("\n=== Результаты PERMANOVA ===\n")
perm <- adonis2(m_abund ~ Variety, data = mydata, permutations = 999, method = "bray")
print(perm)

# ---------------------------------------------------------------------
# 2.4 Интерактивная ординация NMDS (ggplot2 + plotly)
# ---------------------------------------------------------------------

# Вычисляем NMDS
nmds <- metaMDS(m_abund, distance = "bray", k = 2, autotransform = FALSE, trymax = 100)

# 1. Извлекаем координаты точек из NMDS в удобный формат (data.frame)
nmds_coords <- as.data.frame(scores(nmds, display = "sites"))
nmds_coords$Variety <- group_factor
nmds_coords$Sample <- mydata$Tree # или mydata$Identifier, чтобы видеть имя образца при наведении

# 2. Вычисляем координаты для многоугольников (аналог ordihull)
hulls <- nmds_coords %>%
  group_by(Variety) %>%
  slice(chull(NMDS1, NMDS2))

# 3. Строим красивый график через ggplot2
p <- ggplot(nmds_coords, aes(x = NMDS1, y = NMDS2, color = Variety)) +
  geom_polygon(data = hulls, aes(fill = Variety), alpha = 0.2, show.legend = FALSE) +
  geom_point(aes(text = paste("Образец:", Sample)), size = 3) +
  theme_bw() +
  labs(title = "NMDS Ordination of TAGs")

# 4. Превращаем его в интерактивный!
interactive_plot <- ggplotly(p, tooltip = c("text", "Variety"))

# Выводим график (он откроется во вкладке Viewer в RStudio или в браузере)
print(interactive_plot)
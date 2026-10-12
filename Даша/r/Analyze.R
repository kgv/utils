# source("/mnt/d/g/git/kgv/utils/Cypresses/r/Analyze.R", encoding = "UTF-8")

# install.packages("indicspecies")

library(indicspecies)
library(knitr)
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
# 2.4 Ординация NMDS (Неметрическое многомерное шкалирование)
# ---------------------------------------------------------------------
# Вычисляем NMDS
# Примечание: если k=2 не сходится, можно попробовать k=3
nmds <- metaMDS(m_abund, distance = "bray", k = 2, autotransform = FALSE, trymax = 100)

# Задаем цвета для наших групп (по количеству уникальных значений Variety)
num_groups <- length(levels(group_factor))
my_colors <- 1:num_groups

# Визуализация
plot(nmds, type = "n", main = "NMDS Ordination of TAGs")
points(nmds, display = "sites", pch = 16, col = as.numeric(group_factor))
ordihull(nmds, groups = group_factor, label = FALSE, col = 1:length(levels(group_factor)))
# Добавляем легенду (например, в правый верхний угол)
legend("topright",                     # Позиция легенды ("topleft", "bottomright" и т.д.)
       legend = levels(group_factor),  # Текст легенды (имена групп)
       col = my_colors,                # Цвета, соответствующие группам
       pch = 16,                       # Форма точек (как в функции points)
       lty = 1,                        # Добавляем линии в легенду (как у ordihull)
       title = "Variety",              # Заголовок легенды
       bty = "n",                      # Убираем рамку вокруг легенды (для красоты)
       cex = 0.9)                      # Размер шрифта легенды (0.9 = 90% от стандартного)

# # ---------------------------------------------------------------------
# # 2.5 Процедура IndVal (Виды-индикаторы)
# # ---------------------------------------------------------------------
# cat("\n=== Результаты IndVal ===\n")
# # multipatt лучше работает с data.frame, передаем abund вместо m_abund
# inv <- multipatt(abund, group_factor, func = "r.g", control = how(nperm=999))
# inv_sum <- summary(inv)
# print(inv_sum)

# # ---------------------------------------------------------------------
# # 2.6 Процедура SIMPER (Оценка вклада видов в различия)
# # ---------------------------------------------------------------------
# cat("\n=== Результаты SIMPER ===\n")
# sim <- simper(m_abund, group_factor)
# sim_sum <- summary(sim)

# for (comp_name in names(sim_sum)) {
#   cat("\n--------------------------------------------------\n")
#   cat("Сравнение:", comp_name, "\n")
#   cat("--------------------------------------------------\n")
  
#   df <- sim_sum[[comp_name]]
  
#   # Округляем длинные числа до 4 знаков после запятой
#   is_num <- sapply(df, is.numeric)
#   df[is_num] <- lapply(df[is_num], round, 4)
  
#   # Выводим красивую таблицу
#   print(kable(df, format = "markdown"))
#   cat("\n")
# }

# =====================================================================
# КОНЕЦ ПЕРЕНАПРАВЛЕНИЯ ВЫВОДА
# =====================================================================
sink()
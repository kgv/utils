# source("/mnt/d/g/git/kgv/utils/D/r/rankindex.R", encoding = "UTF-8")

library(vegan)


# KIND = "Leaf"
KIND = "Root"

VALUE = "PartsPerMillion_DryWeight"

# Загрузка данных
input_file <- paste0("D/csv/_{Type=Wide}{Kind=", KIND, "}{Value=", VALUE, "}.txt")
mydata <- read.csv(input_file, check.names = FALSE, stringsAsFactors = FALSE)

# Подготавливаем "градиент среды" (ваши факторы) Поскольку Ni измеряется в
# сотнях (0-1000), а Week в единицах (1-5), их ОБЯЗАТЕЛЬНО нужно
# стандартизировать (scale), иначе Ni "задавит" Week.
env_data <- scale(mydata[, c("Ni", "Week")])

# Отделяем матрицу обилий (начиная с 4-го столбца)
abund <- mydata[, 4:ncol(mydata)]
abund <- as.data.frame(lapply(abund, as.numeric), check.names = FALSE)
# Проверяем, не появились ли NA после конвертации
if(any(is.na(abund))) {
  cat("ВНИМАНИЕ: В матрице abund есть пропущенные значения (NA)! Заменяем их на 0.\n")
  abund[is.na(abund)] <- 0 
}

# dist_candidates <- c(
#     "bray",        # Брей-Куртис (классика для экологии и биохимии)
#     "euclidean",   # Евклидово расстояние
#     "manhattan",   # Манхэттенское расстояние
#     "canberra",    # Канберра (хорошо улавливает изменения в редких ЖК)
#     "kulczynski",  # Кульчинский (отличная альтернатива Брею)
#     "jaccard",     # Жаккар (в vegan он адаптирован для количественных данных)
#     "gower",       # Гауэр
#     "altGower",    # Альтернативный Гауэр
#     "chord",       # Хордовое расстояние
#     "hellinger",   # Хеллинджер (очень рекомендуется для композиционных данных!)
#     # "aitchison",
#     "binomial",
#     # "cao",
#     # "chao",
#     "chisq",
#     "chord",
#     "clark",
#     "horn",
#     "mahalanobis",
#     # "morisita",
#     # "mountford",
#     "raup"
# )
# Gower=function(x) cluster:::daisy(x, "gower"),
dist_functions <- list(
  # Стандартные дистанции из vegdist оборачиваем в функции
  Bray       = function(x) vegdist(x, method = "bray"),
  Euclidean  = function(x) vegdist(x, method = "euclidean"),
  Manhattan  = function(x) vegdist(x, method = "manhattan"),
  Canberra   = function(x) vegdist(x, method = "canberra"),
  Kulczynski = function(x) vegdist(x, method = "kulczynski"),
  Jaccard    = function(x) vegdist(x, method = "jaccard"),
  Gower      = function(x) cluster:::daisy(x, "gower"),
  AltGower   = function(x) vegdist(x, method = "altGower"),
  Chord      = function(x) vegdist(x, method = "chord"),
  Hellinger  = function(x) vegdist(x, method = "hellinger"),
  # Cosine Distance
  Cosine     = function(x) designdist(x, method = "1-J/sqrt(A*B)", terms = "quadratic")
)

# Запускаем rankindex
# - grad - наши факторы среды
# - veg - наша матрица обилий (ЖК)
# - indices - список дистанций
cat("=== rankindex ===\n")
best_distances <- rankindex(grad = env_data, 
                            veg = abund, 
                            indices = dist_functions, 
                            method = "spearman")

# Сортируем результаты по убыванию (от лучшей к худшей)
sorted_distances <- sort(best_distances, decreasing = TRUE)

# Выводим на экран
print(sorted_distances)

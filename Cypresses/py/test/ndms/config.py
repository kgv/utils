"""
Модуль конфигурации приложения.
Содержит все константы, пути к файлам и настройки по умолчанию.
"""

from typing import Final, List, Tuple

# --- Настройки данных ---
DATA_FILE_PATH: Final[str] = "Cypresses/_Wide.txt"

SCHEMA_OVERRIDES: Final[dict[str, type]] = {
    "Genus": str,
    "Species": str,
    "Variety": str,
    "Identifier": str,
    "Tree": int,
    "Vial": str,
}

META_COLUMNS: Final[List[str]] = [
    "Genus",
    "Species",
    "Variety",
    "Identifier",
    "Tree",
    "Vial",
]

# --- Настройки GUI (значения для Combobox) ---
TRANSFORM_METHODS: Final[List[str]] = ["None", "log1p"]
DISTANCE_METRICS: Final[List[str]] = [
    "braycurtis",
    "canberra",
    "chebyshev",
    "cityblock",
    "correlation",
    "cosine",
    "euclidean",
    "jensenshannon",
    "mahalanobis",
    "minkowski",
    "seuclidean",
    "sqeuclidean",
]
TAXONOMY_LEVELS: Final[List[str]] = ["Genus", "Species", "Variety"]
N_INIT_VALUES: Final[List[str]] = ["10", "100", "1000"]
MAX_ITER_VALUES: Final[List[str]] = ["10", "100", "1000"]
SEED_VALUES: Final[List[str]] = ["42", "1234"]

# --- Настройки анализа ---
PERMUTATIONS_COUNT: Final[int] = 999
NMDS_COMPONENTS: Final[int] = 2
NMDS_EPSILON: Final[float] = 1e-9

# --- Настройки визуализации ---
PLOT_FIGSIZE: Final[Tuple[int, int]] = (10, 8)
SCATTER_SIZE: Final[int] = 50
HULL_LINE_WIDTH: Final[int] = 2
HULL_LINE_ALPHA: Final[float] = 0.6
HULL_FILL_ALPHA: Final[float] = 0.1
COLORMAP_NAME: Final[str] = "tab20"

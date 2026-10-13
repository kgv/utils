"""
Модуль для визуализации результатов анализа.
Отвечает за построение графиков NMDS и интерактивные подсказки.
"""

from scipy.spatial import ConvexHull
from typing import Any, List, Tuple, Optional
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

import Cypresses.py.ndms.config as config


class Visualizer:
    """
    Класс для отрисовки 2D графиков ординации с интерактивными элементами.
    """

    def __init__(self) -> None:
        self.fig: Optional[plt.Figure] = None
        self.ax: Optional[plt.Axes] = None
        self.scatters: List[Tuple[Any, np.ndarray]] = []
        self.annot: Optional[Any] = None

    def plot_nmds(
        self,
        coords: np.ndarray,
        taxonomy_labels: np.ndarray,
        hover_labels: np.ndarray,
        taxonomy_name: str,
        distance_metric: str,
        transform_method: str,
        stress: float,
    ) -> None:
        """
        Строит график NMDS с выпуклыми оболочками (Convex Hull) для каждой группы.

        :param coords: Координаты точек после NMDS (2D массив).
        :param taxonomy_labels: Метки классов для раскраски.
        :param hover_labels: Текст для всплывающих подсказок.
        :param taxonomy_name: Название выбранной таксономии (для заголовка).
        :param distance_metric: Использованная метрика (для заголовка).
        :param transform_method: Использованный метод трансформации (для заголовка).
        :param stress: Значение stress после NMDS (для заголовка).
        """
        self.fig, self.ax = plt.subplots(figsize=config.PLOT_FIGSIZE)
        unique_species = np.unique(taxonomy_labels)
        colors = matplotlib.colormaps.get_cmap(config.COLORMAP_NAME)

        self.scatters = []

        for i, species in enumerate(unique_species):
            idx = np.where(taxonomy_labels == species)[0]
            pts = coords[idx]
            lbls = hover_labels[idx]

            # Отрисовка точек
            sc = self.ax.scatter(
                pts[:, 0],
                pts[:, 1],
                label=species,
                color=colors(i),
                s=config.SCATTER_SIZE,
            )
            self.scatters.append((sc, lbls))

            # Отрисовка ConvexHull (выпуклой оболочки)
            if len(pts) > 2:
                hull = ConvexHull(pts)
                for simplex in hull.simplices:
                    self.ax.plot(
                        pts[simplex, 0],
                        pts[simplex, 1],
                        color=colors(i),
                        lw=config.HULL_LINE_WIDTH,
                        alpha=config.HULL_LINE_ALPHA,
                    )
                self.ax.fill(
                    pts[hull.vertices, 0],
                    pts[hull.vertices, 1],
                    color=colors(i),
                    alpha=config.HULL_FILL_ALPHA,
                )
            elif len(pts) == 2:
                # Если точек всего две, рисуем просто линию
                self.ax.plot(
                    pts[:, 0],
                    pts[:, 1],
                    color=colors(i),
                    lw=config.HULL_LINE_WIDTH,
                    alpha=config.HULL_LINE_ALPHA,
                )

        # Настройка осей и заголовка
        title = (
            f"NMDS Ordination\n"
            f"Taxonomy: {taxonomy_name}; Distance: {distance_metric}; Transform: {transform_method}\n"
            f"Stress: {stress:.2f}"
        )
        self.ax.set_title(title)
        self.ax.set_xlabel("NMDS1")
        self.ax.set_ylabel("NMDS2")
        self.ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.tight_layout()

        # Настройка интерактивности
        self._setup_annotations()
        plt.show()

    def _setup_annotations(self) -> None:
        """
        Инициализирует объект аннотации и привязывает событие движения мыши.
        """
        if self.ax is None or self.fig is None:
            return

        self.annot = self.ax.annotate(
            "",
            xy=(0, 0),
            xytext=(10, 10),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.9, ec="gray"),
            arrowprops=dict(arrowstyle="-", connectionstyle="arc3,rad=0"),
            zorder=100,
        )
        self.annot.set_visible(False)
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_hover)

    def _on_hover(self, event: Any) -> None:
        """
        Обработчик события наведения мыши на график.
        """
        if event.inaxes == self.ax:
            for sc, lbls in self.scatters:
                cont, ind = sc.contains(event)
                if cont:
                    point_idx = ind["ind"][0]
                    pos = sc.get_offsets()[point_idx]

                    self.annot.xy = pos
                    self.annot.set_text(lbls[point_idx])
                    self.annot.set_visible(True)
                    self.fig.canvas.draw_idle()
                    return

            # Если мышь не на точке, скрываем подсказку
            if self.annot.get_visible():
                self.annot.set_visible(False)
                self.fig.canvas.draw_idle()
        else:
            # Если мышь вне осей графика
            if self.annot and self.annot.get_visible():
                self.annot.set_visible(False)
                self.fig.canvas.draw_idle()

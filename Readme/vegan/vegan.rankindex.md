# vegan/rankindex

- [rdocumentation.org](https://www.rdocumentation.org/packages/vegan/topics/rankindex)
- [Faith, F.P., Minchin, P.R. and Belbin, L. (1987). Compositional dissimilarity as a robust measure of ecological distance. Vegetatio 69, 57-68](https://doi.org/10.1007/BF00038687)

Используется чтоб найти оптимальное расстояние.

Отвечает на вопрос: "Какая из мер дистанций по жирнокислотному составу (матрица abund) лучше всего коррелирует с реальным биохимическим градиентом (Ni и Week)?"

Алгоритм считает ранговую корреляцию Спирмена между матрицей дистанций по ЖК и матрицей дистанций по факторам среды. Чем выше значение, тем лучше эта дистанция отражает влияние вашего эксперимента.
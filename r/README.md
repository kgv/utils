```
WARNING: Rtools is required to build R packages but is not currently installed. Please download and install the appropriate version of Rtools before proceeding:
https://cran.rstudio.com/bin/windows/Rtools/
```

## Install

[Install R](https://cran.r-project.org/bin/linux/ubuntu/fullREADME.html)

- `sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu noble-cran40/"`
- `sudo add-apt-repository "deb https://cloud.r-project.org/bin/linux/ubuntu jammy-cran40/"`

- `sudo apt update`
- `sudo apt install r-base`
- `sudo apt install r-base-dev`

- `sudo apt install libuv1-dev`
- `sudo apt install libcurl4-openssl-dev`

- `install.packages(c("languageserver"))`
- `install.packages(c("httpgd"))`

- `install.packages(c("vegan"))`
- `install.packages(c("tidyverse"))`
- `install.packages(c("indicspecies"))`

## Use

Данные должны быть представлены в виде матрицы, где строки — это образцы
(повторности/биотопы), а столбцы — это виды (в вашем случае — триацилглицерины,
TAG). Первые столбцы обычно отводятся под название образца и его группирующую
переменную (фактор).

Установлен ли конкретный пакет?

`rownames(installed.packages())`
`View(installed.packages())`
`"vegan" %in% rownames(installed.packages())`

```json
    // Путь к самому R (нужен для работы Language Server и автодополнения)
    "r.rpath.linux": "/usr/bin/R",
    // Путь к терминалу R (то, что запускается при отправке кода в консоль)
    "r.rterm.linux": "/usr/bin/R",
    // Рекомендуется, чтобы код отправлялся в активный терминал
    "r.alwaysUseActiveTerminal": true,
    // Включаем поддержку просмотра графиков внутри VS Code
    "r.plot.useHttpgd": true
```

`sudo apt install python3-pip`
`pip3 install radian --break-system-packages`
```json
    "r.rpath.linux": "/usr/bin/R",
    "r.rterm.linux": "/home/g/.local/bin/radian",
    "r.rterm.option": [], // Обязательно очистить опции для radian
    "r.alwaysUseActiveTerminal": true,
    "r.plot.useHttpgd": true
```

source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/test.R", encoding = "UTF-8")

source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/Convert.R", encoding = "UTF-8")
source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/Analyze.R", encoding = "UTF-8")
source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/Dendrogram.R", encoding = "UTF-8")

source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/PERMANOVA.R", encoding = "UTF-8")
source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/ANOSIM.R", encoding = "UTF-8")
source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/NMDS.R", encoding = "UTF-8")
source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/SIMPER.R", encoding = "UTF-8")
source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/0/IndVal.R", encoding = "UTF-8")


source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/1/Convert.R", encoding = "UTF-8")
source("/mnt/d/git/ippras/calculations_of_fatty_acids/r/1/Analyze.R", encoding = "UTF-8")
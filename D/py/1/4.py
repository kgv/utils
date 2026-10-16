import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import io
import re
import tkinter as tk

# Добавляем импорт NavigationToolbar2Tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# 1. Исходные данные
raw_data = """
## Comparison: 0.5_50.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0044| 0.0030| 1.4501|  8.4406|  8.7891| 0.2129| 1.000|       |
|18:0                                                                       |  0.0029| 0.0020| 1.4975|  9.7353|  9.2250| 0.3561| 0.467|       |
|11-18:1                                                                    |  0.0023| 0.0016| 1.4700| 10.5203| 10.3477| 0.4706| 0.660|       |
|9,12,15-18:3                                                               |  0.0021| 0.0015| 1.4476| 12.9068| 12.6394| 0.5737| 0.987|       |
|9-16:1                                                                     |  0.0019| 0.0014| 1.3402| 10.7363| 10.5789| 0.6658| 0.699|       |
|11-Me-12-18:1                                                              |  0.0018| 0.0013| 1.3569| 10.5587| 10.4758| 0.7525| 0.837|       |
|16:0                                                                       |  0.0017| 0.0013| 1.3078| 12.0926| 11.9538| 0.8375| 0.764|       |
|Minors                                                                     |  0.0017| 0.0011| 1.5248| 10.6026| 10.4462| 0.9221| 0.975|       |
|9,12-18:2                                                                  |  0.0016| 0.0012| 1.3560| 12.3909| 12.5203| 1.0000| 0.899|       |

## Comparison: 0.5_250.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0064| 0.0036| 1.8091|  8.4406|  9.6901| 0.2585| 0.940|       |
|18:0                                                                       |  0.0035| 0.0019| 1.8391|  9.7353|  9.0737| 0.3980| 0.181|       |
|9,12,15-18:3                                                               |  0.0033| 0.0017| 1.9801| 12.9068| 12.2924| 0.5299| 0.594|       |
|Minors                                                                     |  0.0029| 0.0017| 1.7201| 10.6026| 10.0444| 0.6456| 0.329|       |
|16:0                                                                       |  0.0023| 0.0011| 2.0156| 12.0926| 11.7100| 0.7361| 0.427|       |
|9-16:1                                                                     |  0.0019| 0.0011| 1.6230| 10.7363| 10.6195| 0.8107| 0.690|       |
|11-Me-12-18:1                                                              |  0.0018| 0.0013| 1.4384| 10.5587| 10.3787| 0.8844| 0.792|       |
|11-18:1                                                                    |  0.0015| 0.0010| 1.4676| 10.5203| 10.5234| 0.9433| 0.986|       |
|9,12-18:2                                                                  |  0.0014| 0.0011| 1.2492| 12.3909| 12.4855| 1.0000| 0.952|       |

## Comparison: 0.5_500.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0127| 0.0039| 3.2635|  8.4406| 10.9436| 0.3544| 0.002|**     |
|18:0                                                                       |  0.0050| 0.0024| 2.1048|  9.7353|  8.7581| 0.4942| 0.004|**     |
|9,12,15-18:3                                                               |  0.0048| 0.0021| 2.3365| 12.9068| 11.9654| 0.6281| 0.129|       |
|9,12-18:2                                                                  |  0.0033| 0.0018| 1.8807| 12.3909| 13.0365| 0.7205| 0.286|       |
|Minors                                                                     |  0.0030| 0.0023| 1.2829| 10.6026| 10.0646| 0.8040| 0.264|       |
|11-18:1                                                                    |  0.0024| 0.0017| 1.3635| 10.5203| 10.9204| 0.8697| 0.652|       |
|16:0                                                                       |  0.0018| 0.0012| 1.5288| 12.0926| 11.8580| 0.9194| 0.731|       |
|11-Me-12-18:1                                                              |  0.0016| 0.0011| 1.4236| 10.5587| 10.5497| 0.9642| 0.953|       |
|9-16:1                                                                     |  0.0013| 0.0011| 1.2177| 10.7363| 10.9242| 1.0000| 0.975|       |

## Comparison: 0.5_750.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0151| 0.0045| 3.3845|  8.4406| 11.4156| 0.4029| 0.001|***    |
|9,12,15-18:3                                                               |  0.0054| 0.0022| 2.4118| 12.9068| 11.8437| 0.5468| 0.029|*      |
|18:0                                                                       |  0.0047| 0.0020| 2.3504|  9.7353|  8.8120| 0.6713| 0.002|**     |
|Minors                                                                     |  0.0026| 0.0017| 1.5387| 10.6026| 10.1061| 0.7393| 0.524|       |
|9,12-18:2                                                                  |  0.0023| 0.0016| 1.4827| 12.3909| 12.8461| 0.8018| 0.566|       |
|11-18:1                                                                    |  0.0023| 0.0014| 1.6218| 10.5203| 10.7513| 0.8628| 0.704|       |
|16:0                                                                       |  0.0022| 0.0013| 1.7617| 12.0926| 11.7227| 0.9221| 0.471|       |
|11-Me-12-18:1                                                              |  0.0016| 0.0011| 1.4054| 10.5587| 10.5423| 0.9651| 0.939|       |
|9-16:1                                                                     |  0.0013| 0.0010| 1.2590| 10.7363| 10.8410| 1.0000| 0.964|       |

## Comparison: 0.5_1000.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0158| 0.0059| 2.6935|  8.4406| 11.5116| 0.3010| 0.001|***    |
|9,12,15-18:3                                                               |  0.0081| 0.0044| 1.8584| 12.9068| 11.3578| 0.4556| 0.001|***    |
|18:0                                                                       |  0.0063| 0.0030| 2.0875|  9.7353|  8.5333| 0.5750| 0.001|***    |
|16:0                                                                       |  0.0048| 0.0034| 1.4147| 12.0926| 11.1834| 0.6676| 0.001|***    |
|Minors                                                                     |  0.0040| 0.0032| 1.2474| 10.6026|  9.9490| 0.7445| 0.017|*      |
|9,12-18:2                                                                  |  0.0037| 0.0037| 0.9858| 12.3909| 12.0379| 0.8148| 0.178|       |
|11-Me-12-18:1                                                              |  0.0033| 0.0025| 1.3376| 10.5587|  9.9553| 0.8785| 0.023|*      |
|11-18:1                                                                    |  0.0032| 0.0019| 1.7036| 10.5203| 10.8058| 0.9395| 0.092|.      |
|9-16:1                                                                     |  0.0032| 0.0030| 1.0682| 10.7363| 10.4415| 1.0000| 0.118|       |

## Comparison: 50.5_250.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0048| 0.0039| 1.2317|  8.7891|  9.6901| 0.2380| 0.998|       |
|Minors                                                                     |  0.0023| 0.0016| 1.4009| 10.4462| 10.0444| 0.3496| 0.695|       |
|11-18:1                                                                    |  0.0022| 0.0013| 1.6651| 10.3477| 10.5234| 0.4595| 0.733|       |
|9-16:1                                                                     |  0.0021| 0.0016| 1.3619| 10.5789| 10.6195| 0.5636| 0.517|       |
|9,12,15-18:3                                                               |  0.0020| 0.0013| 1.5330| 12.6394| 12.2924| 0.6643| 0.983|       |
|11-Me-12-18:1                                                              |  0.0020| 0.0014| 1.3839| 10.4758| 10.3787| 0.7619| 0.585|       |
|16:0                                                                       |  0.0018| 0.0012| 1.5003| 11.9538| 11.7100| 0.8503| 0.725|       |
|18:0                                                                       |  0.0017| 0.0011| 1.4990|  9.2250|  9.0737| 0.9323| 0.985|       |
|9,12-18:2                                                                  |  0.0014| 0.0010| 1.3680| 12.5203| 12.4855| 1.0000| 0.955|       |

## Comparison: 50.5_500.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0110| 0.0044| 2.5067|  8.7891| 10.9436| 0.3449| 0.016|*      |
|9,12,15-18:3                                                               |  0.0035| 0.0018| 1.9756| 12.6394| 11.9654| 0.4546| 0.522|       |
|11-18:1                                                                    |  0.0034| 0.0021| 1.5626| 10.3477| 10.9204| 0.5594| 0.043|*      |
|18:0                                                                       |  0.0028| 0.0018| 1.5186|  9.2250|  8.7581| 0.6465| 0.552|       |
|9,12-18:2                                                                  |  0.0028| 0.0016| 1.7571| 12.5203| 13.0365| 0.7332| 0.401|       |
|Minors                                                                     |  0.0028| 0.0019| 1.4576| 10.4462| 10.0646| 0.8197| 0.380|       |
|9-16:1                                                                     |  0.0022| 0.0016| 1.3470| 10.5789| 10.9242| 0.8880| 0.453|       |
|11-Me-12-18:1                                                              |  0.0019| 0.0013| 1.4395| 10.4758| 10.5497| 0.9486| 0.652|       |
|16:0                                                                       |  0.0016| 0.0011| 1.4755| 11.9538| 11.8580| 1.0000| 0.814|       |

## Comparison: 50.5_750.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0134| 0.0049| 2.7247|  8.7891| 11.4156| 0.4127| 0.003|**     |
|9,12,15-18:3                                                               |  0.0041| 0.0020| 2.0487| 12.6394| 11.8437| 0.5381| 0.325|       |
|11-18:1                                                                    |  0.0030| 0.0019| 1.5638| 10.3477| 10.7513| 0.6311| 0.168|       |
|18:0                                                                       |  0.0023| 0.0015| 1.5118|  9.2250|  8.8120| 0.7015| 0.827|       |
|Minors                                                                     |  0.0021| 0.0014| 1.4758| 10.4462| 10.1061| 0.7660| 0.817|       |
|9-16:1                                                                     |  0.0021| 0.0015| 1.3472| 10.5789| 10.8410| 0.8300| 0.540|       |
|11-Me-12-18:1                                                              |  0.0019| 0.0014| 1.3608| 10.4758| 10.5423| 0.8886| 0.693|       |
|16:0                                                                       |  0.0018| 0.0013| 1.4231| 11.9538| 11.7227| 0.9445| 0.713|       |
|9,12-18:2                                                                  |  0.0018| 0.0014| 1.2813| 12.5203| 12.8461| 1.0000| 0.790|       |

## Comparison: 50.5_1000.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0141| 0.0063| 2.2408|  8.7891| 11.5116| 0.3019| 0.002|**     |
|9,12,15-18:3                                                               |  0.0068| 0.0042| 1.6049| 12.6394| 11.3578| 0.4470| 0.001|***    |
|16:0                                                                       |  0.0042| 0.0035| 1.2168| 11.9538| 11.1834| 0.5372| 0.002|**     |
|11-18:1                                                                    |  0.0038| 0.0023| 1.6572| 10.3477| 10.8058| 0.6193| 0.007|**     |
|9,12-18:2                                                                  |  0.0038| 0.0041| 0.9337| 12.5203| 12.0379| 0.7008| 0.137|       |
|18:0                                                                       |  0.0038| 0.0026| 1.4179|  9.2250|  8.5333| 0.7814| 0.093|.      |
|Minors                                                                     |  0.0036| 0.0030| 1.2172| 10.4462|  9.9490| 0.8596| 0.052|.      |
|9-16:1                                                                     |  0.0034| 0.0027| 1.2501| 10.5789| 10.4415| 0.9330| 0.047|*      |
|11-Me-12-18:1                                                              |  0.0031| 0.0026| 1.2147| 10.4758|  9.9553| 1.0000| 0.045|*      |

## Comparison: 250.5_500.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0064| 0.0023| 2.8308|  9.6901| 10.9436| 0.2763| 0.929|       |
|9,12-18:2                                                                  |  0.0029| 0.0015| 1.8934| 12.4855| 13.0365| 0.4003| 0.410|       |
|Minors                                                                     |  0.0023| 0.0013| 1.7953| 10.0444| 10.0646| 0.4983| 0.698|       |
|18:0                                                                       |  0.0022| 0.0014| 1.5288|  9.0737|  8.7581| 0.5928| 0.844|       |
|9-16:1                                                                     |  0.0021| 0.0014| 1.5215| 10.6195| 10.9242| 0.6826| 0.565|       |
|11-18:1                                                                    |  0.0021| 0.0017| 1.2289| 10.5234| 10.9204| 0.7719| 0.837|       |
|9,12,15-18:3                                                               |  0.0020| 0.0013| 1.6149| 12.2924| 11.9654| 0.8595| 0.991|       |
|11-Me-12-18:1                                                              |  0.0020| 0.0013| 1.4678| 10.3787| 10.5497| 0.9445| 0.634|       |
|16:0                                                                       |  0.0013| 0.0010| 1.3069| 11.7100| 11.8580| 1.0000| 0.980|       |

## Comparison: 250.5_750.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0088| 0.0031| 2.7959|  9.6901| 11.4156| 0.3792| 0.330|       |
|9,12,15-18:3                                                               |  0.0025| 0.0016| 1.5611| 12.2924| 11.8437| 0.4863| 0.935|       |
|11-18:1                                                                    |  0.0021| 0.0011| 1.8592| 10.5234| 10.7513| 0.5779| 0.794|       |
|9-16:1                                                                     |  0.0020| 0.0013| 1.5799| 10.6195| 10.8410| 0.6650| 0.585|       |
|9,12-18:2                                                                  |  0.0019| 0.0013| 1.4344| 12.4855| 12.8461| 0.7465| 0.768|       |
|11-Me-12-18:1                                                              |  0.0019| 0.0015| 1.2520| 10.3787| 10.5423| 0.8270| 0.743|       |
|18:0                                                                       |  0.0015| 0.0011| 1.3598|  9.0737|  8.8120| 0.8937| 0.992|       |
|Minors                                                                     |  0.0014| 0.0010| 1.3706| 10.0444| 10.1061| 0.9527| 0.997|       |
|16:0                                                                       |  0.0011| 0.0009| 1.2824| 11.7100| 11.7227| 1.0000| 0.995|       |

## Comparison: 250.5_1000.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0094| 0.0048| 1.9450|  9.6901| 11.5116| 0.2597| 0.188|       |
|9,12,15-18:3                                                               |  0.0050| 0.0040| 1.2604| 12.2924| 11.3578| 0.3985| 0.081|.      |
|9,12-18:2                                                                  |  0.0037| 0.0040| 0.9167| 12.4855| 12.0379| 0.4998| 0.205|       |
|9-16:1                                                                     |  0.0034| 0.0027| 1.2428| 10.6195| 10.4415| 0.5939| 0.055|.      |
|16:0                                                                       |  0.0031| 0.0031| 0.9832| 11.7100| 11.1834| 0.6783| 0.209|       |
|11-18:1                                                                    |  0.0030| 0.0018| 1.7044| 10.5234| 10.8058| 0.7617| 0.155|       |
|18:0                                                                       |  0.0030| 0.0024| 1.2383|  9.0737|  8.5333| 0.8439| 0.436|       |
|Minors                                                                     |  0.0030| 0.0023| 1.2654| 10.0444|  9.9490| 0.9257| 0.296|       |
|11-Me-12-18:1                                                              |  0.0027| 0.0025| 1.0859| 10.3787|  9.9553| 1.0000| 0.248|       |

## Comparison: 500.5_750.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0037| 0.0021| 1.7237| 10.9436| 11.4156| 0.2176| 1.000|       |
|Minors                                                                     |  0.0022| 0.0014| 1.6320| 10.0646| 10.1061| 0.3491| 0.766|       |
|11-18:1                                                                    |  0.0018| 0.0018| 1.0190| 10.9204| 10.7513| 0.4570| 0.928|       |
|11-Me-12-18:1                                                              |  0.0018| 0.0012| 1.5133| 10.5497| 10.5423| 0.5640| 0.830|       |
|9,12,15-18:3                                                               |  0.0017| 0.0013| 1.2610| 11.9654| 11.8437| 0.6634| 1.000|       |
|18:0                                                                       |  0.0016| 0.0012| 1.4168|  8.7581|  8.8120| 0.7608| 0.983|       |
|9,12-18:2                                                                  |  0.0015| 0.0009| 1.6809| 13.0365| 12.8461| 0.8504| 0.936|       |
|16:0                                                                       |  0.0014| 0.0010| 1.4871| 11.8580| 11.7227| 0.9357| 0.958|       |
|9-16:1                                                                     |  0.0011| 0.0009| 1.1521| 10.9242| 10.8410| 1.0000| 0.994|       |

## Comparison: 500.5_1000.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0055| 0.0025| 2.1670| 10.9436| 11.5116| 0.1639| 0.988|       |
|9,12-18:2                                                                  |  0.0053| 0.0048| 1.1097| 13.0365| 12.0379| 0.3236| 0.001|***    |
|9,12,15-18:3                                                               |  0.0038| 0.0035| 1.0742| 11.9654| 11.3578| 0.4375| 0.384|       |
|16:0                                                                       |  0.0037| 0.0032| 1.1389| 11.8580| 11.1834| 0.5480| 0.016|*      |
|Minors                                                                     |  0.0034| 0.0026| 1.3154| 10.0646|  9.9490| 0.6495| 0.127|       |
|9-16:1                                                                     |  0.0034| 0.0033| 1.0192| 10.9242| 10.4415| 0.7503| 0.048|*      |
|11-Me-12-18:1                                                              |  0.0033| 0.0026| 1.2553| 10.5497|  9.9553| 0.8487| 0.013|*      |
|11-18:1                                                                    |  0.0027| 0.0022| 1.2153| 10.9204| 10.8058| 0.9296| 0.357|       |
|18:0                                                                       |  0.0024| 0.0020| 1.1627|  8.7581|  8.5333| 1.0000| 0.781|       |

## Comparison: 750.5_1000.5

|                                                                           | average|     sd|  ratio|     ava|     avb| cumsum|     p|signif |
|:--------------------------------------------------------------------------|-------:|------:|------:|-------:|-------:|------:|-----:|:------|
|9-18:1                                                                     |  0.0048| 0.0034| 1.3961| 11.4156| 11.5116| 0.1575| 0.997|       |
|9,12-18:2                                                                  |  0.0044| 0.0047| 0.9189| 12.8461| 12.0379| 0.3011| 0.039|*      |
|9,12,15-18:3                                                               |  0.0036| 0.0033| 1.0765| 11.8437| 11.3578| 0.4188| 0.479|       |
|11-Me-12-18:1                                                              |  0.0033| 0.0026| 1.2964| 10.5423|  9.9553| 0.5283| 0.018|*      |
|9-16:1                                                                     |  0.0033| 0.0032| 1.0455| 10.8410| 10.4415| 0.6370| 0.079|.      |
|16:0                                                                       |  0.0031| 0.0031| 0.9917| 11.7227| 11.1834| 0.7394| 0.174|       |
|Minors                                                                     |  0.0030| 0.0024| 1.2458| 10.1061|  9.9490| 0.8375| 0.274|       |
|11-18:1                                                                    |  0.0029| 0.0023| 1.2661| 10.7513| 10.8058| 0.9317| 0.250|       |
|18:0                                                                       |  0.0021| 0.0020| 1.0473|  8.8120|  8.5333| 1.0000| 0.878|       |


"""

# 2. Парсинг данных (Polars)
blocks = raw_data.strip().split("## Comparison: ")
all_data = []

for block in blocks[1:]:
    lines = block.strip().split("\n")
    comp_name = lines[0].strip()

    cleaned_lines = []
    for line in lines[1:]:
        line = line.strip()
        if not line or re.match(r"^\|[:\-]+", line):
            continue
        if line.startswith("|"):
            line = line[1:]
        if line.endswith("|"):
            line = line[:-1]
        cleaned_lines.append(line)

    table_str = "\n".join(cleaned_lines)

    df = pl.read_csv(io.StringIO(table_str), separator="|", null_values=[""])
    df.columns = [c.strip() for c in df.columns]
    df = df.rename({df.columns[0]: "Feature"})

    df = df.with_columns([pl.col(pl.String).str.strip_chars()])
    df = df.with_columns(pl.lit(comp_name).alias("Comparison"))
    all_data.append(df)

full_df = pl.concat(all_data)
full_df = full_df.with_columns(pl.col("signif").fill_null(""))
full_df = full_df.with_columns(
    [
        pl.col("average").cast(pl.Float64),
        pl.col("sd").cast(pl.Float64),
        pl.col("ratio").cast(pl.Float64),
        pl.col("ava").cast(pl.Float64),
        pl.col("avb").cast(pl.Float64),
        pl.col("cumsum").cast(pl.Float64) * 100,
        pl.col("p").cast(pl.Float64),
    ]
)

# 3. Подготовка данных
df_control = full_df.filter(pl.col("Comparison").str.starts_with("0.5_"))
df_control = df_control.with_columns(
    pl.col("Comparison")
    .str.split("_")
    .list.get(1)
    .str.split(".")
    .list.get(0)
    .cast(pl.Int32)
    .alias("Ni")
)
df_control = df_control.with_columns(
    ava_percent=(pl.col("ava") / pl.col("ava").sum() * 100).over("Ni"),
    avb_percent=(pl.col("avb") / pl.col("avb").sum() * 100).over("Ni"),
)

df_control = df_control.with_columns(
    [
        pl.col("average").rank(method="min", descending=True).over("Ni").alias("Rank"),
        pl.col("cumsum")
        .diff()
        .over("Ni")
        .fill_null(pl.col("cumsum"))
        .alias("cumsum_diff"),
    ]
)

feature_importance = (
    df_control.group_by("Feature")
    .agg(pl.col("average").mean().alias("mean_avg"))
    .sort("mean_avg", descending=True)
)
all_features = feature_importance.get_column("Feature").to_list()

# Глобальная переменная для окна с графиками
plot_window = None


# 4. Функция отрисовки графиков во встроенном окне Tkinter
def draw_plots(selected_features, row_height):
    global plot_window

    if not selected_features:
        print("Нет выбранных кислот для отображения.")
        return

    # Создаем или очищаем окно для графиков
    if plot_window is None or not tk.Toplevel.winfo_exists(plot_window):
        plot_window = tk.Toplevel(root)
        plot_window.title("Графики SIMPER")
        plot_window.geometry("1400x800")
    else:
        # Очищаем старые виджеты, если окно уже открыто
        for widget in plot_window.winfo_children():
            widget.destroy()

    # --- Фрейм для панели инструментов (сверху, не прокручивается) ---
    toolbar_frame = tk.Frame(plot_window)
    toolbar_frame.pack(side=tk.TOP, fill=tk.X)

    # --- Фрейм для холста с прокруткой (занимает оставшееся место) ---
    main_frame = tk.Frame(plot_window)
    main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    # Настраиваем Canvas и Scrollbar для прокрутки
    canvas = tk.Canvas(main_frame)
    scrollbar = tk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Привязка колесика мыши для прокрутки
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    plot_window.bind("<MouseWheel>", _on_mousewheel)
    plot_window.bind(
        "<Button-4>", lambda e: canvas.yview_scroll(-1, "units")
    )  # Для Linux
    plot_window.bind(
        "<Button-5>", lambda e: canvas.yview_scroll(1, "units")
    )  # Для Linux

    # Построение графиков Matplotlib
    n_features = len(selected_features)
    sns.set_theme(style="whitegrid")

    fig, axes = plt.subplots(
        nrows=n_features, ncols=4, figsize=(20, row_height * n_features)
    )
    axes = np.atleast_2d(axes)

    fig.suptitle(
        f"Профиль SIMPER: {n_features} выбранных жирных кислот",
        fontsize=22,
        weight="bold",
        y=0.99 if n_features > 1 else 1.05,
    )

    metric_titles = [
        "Концентрация (ava / avb)",
        "Собственный вклад (Average ± SD)",
        "Относительный вклад (%)",
        "p-value (Значимость)",
    ]

    for row_idx, feature in enumerate(selected_features):
        feat_df = df_control.filter(pl.col("Feature") == feature).sort("Ni").to_pandas()

        # --- 1. Концентрация (ava и avb) + avb_percent (вторая ось) ---
        ax0 = axes[row_idx, 0]
        line1 = ax0.plot(
            feat_df["Ni"],
            feat_df["ava"],
            color="#2b7bba",
            marker="o",
            markersize=8,
            linewidth=2,
            label="ava (Контроль)",
        )
        line2 = ax0.plot(
            feat_df["Ni"],
            feat_df["avb"],
            color="#f0ad4e",
            marker="s",
            markersize=8,
            linewidth=2,
            label="avb (Опыт)",
        )
        ax0.set_xticks([0, 50, 250, 500, 750, 1000])
        ax0.set_ylabel(f"{feature}\nКонцентрация", fontsize=12, weight="bold")

        ax0_twin = ax0.twinx()
        line3 = ax0_twin.plot(
            feat_df["Ni"],
            feat_df["avb_percent"],
            color="#8e44ad",
            marker="^",
            markersize=8,
            linewidth=2,
            linestyle="--",
            label="avb_percent (%)",
        )
        ax0_twin.set_ylabel(
            "avb_percent (%)", color="#8e44ad", fontsize=10, weight="bold"
        )
        ax0_twin.tick_params(axis="y", labelcolor="#8e44ad")
        ax0_twin.grid(False)

        if row_idx == 0:
            lines = line1 + line2 + line3
            labels = [l.get_label() for l in lines]
            ax0.legend(lines, labels, fontsize=10, loc="best")

        # --- 2. Собственный вклад (Average + SD) ---
        ax1 = axes[row_idx, 1]
        ax1.bar(
            feat_df["Ni"],
            feat_df["average"],
            yerr=feat_df["sd"],
            width=80,
            capsize=5,
            color="#d9534f",
            alpha=0.8,
            edgecolor="black",
        )
        ax1.set_xticks([0, 50, 250, 500, 750, 1000])
        ax1.set_ylabel("")

        # --- 3. Позиция (Ранг) ---
        ax2 = axes[row_idx, 2]
        ax2.plot(
            feat_df["Ni"],
            feat_df["cumsum_diff"],
            color="#5cb85c",
            marker="v",
            markersize=8,
            linewidth=2,
        )
        ax2.set_xticks([0, 50, 250, 500, 750, 1000])
        ax2.set_ylabel("")

        # --- 4. p-value ---
        ax3 = axes[row_idx, 3]
        ax3.plot(
            feat_df["Ni"],
            feat_df["p"],
            color="#9b59b6",
            marker="D",
            markersize=8,
            linewidth=2,
        )
        ax3.axhline(0.05, ls="--", color="red", alpha=0.7)

        for _, row in feat_df.iterrows():
            if row["signif"] and str(row["signif"]).strip() not in ["", "."]:
                ax3.text(
                    row["Ni"],
                    row["p"] + 0.02,
                    row["signif"],
                    color="red",
                    fontsize=14,
                    ha="center",
                    va="bottom",
                    weight="bold",
                )

        ax3.set_xticks([0, 50, 250, 500, 750, 1000])
        ax3.set_ylabel("")

        if row_idx == 0:
            for col_idx in range(4):
                axes[row_idx, col_idx].set_title(
                    metric_titles[col_idx], fontsize=14, weight="bold", pad=15
                )

        for col_idx in range(4):
            if row_idx == n_features - 1:
                axes[row_idx, col_idx].set_xlabel("Доза Ni", fontsize=12, weight="bold")
            else:
                axes[row_idx, col_idx].set_xlabel("")

    plt.tight_layout(rect=[0, 0, 1, 0.98])

    # Встраиваем график в Tkinter
    canvas_tk = FigureCanvasTkAgg(fig, master=scrollable_frame)
    canvas_tk.draw()
    canvas_tk.get_tk_widget().pack(fill="both", expand=True)

    # --- ДОБАВЛЯЕМ ПАНЕЛЬ ИНСТРУМЕНТОВ (С КНОПКОЙ СОХРАНЕНИЯ) ---
    toolbar = NavigationToolbar2Tk(canvas_tk, toolbar_frame)
    toolbar.update()

    # Закрываем фигуру в pyplot, чтобы не утекала память
    plt.close(fig)


# 5. Создание окна настроек (GUI)
def on_redraw_click():
    selected_indices = listbox.curselection()
    selected_features = [listbox.get(i) for i in selected_indices]

    try:
        row_height = float(row_height_var.get())
    except ValueError:
        row_height = 3.5

    draw_plots(selected_features, row_height)


root = tk.Tk()
root.title("Настройки отображения ЖК")
root.geometry("380x500")

lbl = tk.Label(
    root,
    text="Выберите ЖК для отображения\n(Зажмите Ctrl для выбора нескольких):",
    font=("Arial", 10, "bold"),
)
lbl.pack(pady=10)

frame_list = tk.Frame(root)
frame_list.pack(pady=5, fill=tk.BOTH, expand=True, padx=20)

scrollbar_list = tk.Scrollbar(frame_list)
scrollbar_list.pack(side=tk.RIGHT, fill=tk.Y)

listbox = tk.Listbox(
    frame_list,
    selectmode=tk.EXTENDED,
    yscrollcommand=scrollbar_list.set,
    font=("Arial", 11),
)
listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar_list.config(command=listbox.yview)

for feature in all_features:
    listbox.insert(tk.END, feature)

listbox.select_set(0, tk.END)

frame_settings = tk.Frame(root)
frame_settings.pack(pady=10, fill=tk.X, padx=20)

tk.Label(frame_settings, text="Высота строки графиков:", font=("Arial", 10)).pack(
    side=tk.LEFT
)
row_height_var = tk.StringVar(value="3.5")
spinbox_height = tk.Spinbox(
    frame_settings,
    from_=1.0,
    to=10.0,
    increment=0.5,
    textvariable=row_height_var,
    width=5,
    font=("Arial", 10),
)
spinbox_height.pack(side=tk.RIGHT)

btn_redraw = tk.Button(
    root,
    text="Перерисовать графики",
    command=on_redraw_click,
    font=("Arial", 12, "bold"),
    bg="#4CAF50",
    fg="white",
)
btn_redraw.pack(pady=15, fill=tk.X, padx=20)

on_redraw_click()

root.mainloop()

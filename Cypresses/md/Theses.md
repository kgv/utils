# Тезисы

У нас до сих пор неопределенность с таксономией объектов.

Файлы с таксономией (они одинаковые - pdf для удобства чтения):

- {Kind=Input}{Fields=Identifier,Genus,Species,Variety,Url}.txt
- {Kind=Input}{Fields=Identifier,Genus,Species,Variety,Url}.pdf

Если допустить что таксономия у нас точная:

> По монотерпенам виды достоверно не различаются (PERMANOVA: R2 = 0,43; p = 0,11), по сесквитерпенам — разделяются полностью (R2 = 0,78; p = 0,029, минимально возможное при 4 и 3 деревьях).

У меня PERMANOVA по Species (видам) для наших биологических повторностей (деревьев) всегда значима - и по Monoterpene и по Sesquiterpene (как для ppm, так и для %):

Файлы с расчетом PERMANOVA (смотреть в строчку где ***):

- _{Type=PERMANOVA}{Group=Species}{Distance=bray}{Permutations=9999}{Component=Monoterpene}{Value=PartsPerMillion_Mean}.txt
- _{Type=PERMANOVA}{Group=Species}{Distance=bray}{Permutations=9999}{Component=Monoterpene}{Value=Percent_Mean}.txt
- _{Type=PERMANOVA}{Group=Species}{Distance=bray}{Permutations=9999}{Component=Sesquiterpene}{Value=PartsPerMillion_Mean}.txt
- _{Type=PERMANOVA}{Group=Species}{Distance=bray}{Permutations=9999}{Component=Sesquiterpene}{Value=Percent_Mean}.txt
- _{Type=PERMANOVA}{Group=Species}{Distance=bray}{Permutations=9999}{Component=Terpene}{Value=PartsPerMillion_Mean}.txt
- _{Type=PERMANOVA}{Group=Species}{Distance=bray}{Permutations=9999}{Component=Terpene}{Value=Percent_Mean}.txt

Файлы с данными:

- _{Type=Wide}{Component=Monoterpene}{Value=PartsPerMillion_Mean}.txt
- _{Type=Wide}{Component=Monoterpene}{Value=Percent_Mean}.txt
- _{Type=Wide}{Component=Sesquiterpene}{Value=PartsPerMillion_Mean}.txt
- _{Type=Wide}{Component=Sesquiterpene}{Value=Percent_Mean}.txt
- _{Type=Wide}{Component=Terpene}{Value=PartsPerMillion_Mean}.txt
- _{Type=Wide}{Component=Terpene}{Value=Percent_Mean}.txt

import pandas as pd
from functools import reduce

def merge_chromatography_data(data_dict, rt_col='rt', value_col='A,%', name_col='Название'):
    """
    Объединяет несколько таблиц хроматографии по столбцу rt.
    
    :param data_dict: Словарь вида {'Имя образца': DataFrame}
    :param rt_col: Название столбца с временем удерживания
    :param value_col: Название столбца со значениями (которые пойдут в ячейки)
    :param name_col: Название столбца с именами веществ
    :return: Объединенный DataFrame
    """
    processed_dfs = []
    name_mapping = {}
    
    for sample_name, df in data_dict.items():
        # Оставляем только нужные столбцы
        temp_df = df[[name_col, rt_col, value_col]].copy()
        
        # Удаляем строки, где rt не указано (например, итоговая строка 100%)
        temp_df = temp_df.dropna(subset=[rt_col])
        
        # Приводим rt к числу (float), чтобы 0.7 и 0.70 считались одним значением
        temp_df[rt_col] = temp_df[rt_col].astype(float).round(3)
        
        # Собираем известные названия (например, Triolein)
        for _, row in temp_df.iterrows():
            name = str(row[name_col]).strip()
            # Если имя не пустое и не NaN
            if name and name.lower() != 'nan':
                name_mapping[row[rt_col]] = name
                
        # Переименовываем столбец со значениями, добавляя имя образца
        temp_df = temp_df.rename(columns={value_col: f"{sample_name} ({value_col})"})
        
        # Удаляем столбец с названием, мы восстановим его в самом конце
        temp_df = temp_df.drop(columns=[name_col])
        
        processed_dfs.append(temp_df)
        
    # Объединяем все таблицы по столбцу rt (Outer Join)
    merged_df = reduce(lambda left, right: pd.merge(left, right, on=rt_col, how='outer'), processed_dfs)
    
    # Сортируем по времени удерживания
    merged_df = merged_df.sort_values(rt_col).reset_index(drop=True)
    
    # Генерируем итоговый столбец "Название"
    final_names = []
    peak_counter = 1
    
    for rt in merged_df[rt_col]:
        if rt in name_mapping:
            final_names.append(name_mapping[rt])
        else:
            final_names.append(f"Пик {peak_counter}")
            peak_counter += 1
            
    # Вставляем столбец "Название" на первое место
    merged_df.insert(0, name_col, final_names)
    
    # Заполняем пустые значения (NaN) прочерком
    merged_df = merged_df.fillna('-')
    
    return merged_df
# ==========================================
# ПРИМЕР ИСПОЛЬЗОВАНИЯ
# ==========================================
if __name__ == "__main__":
    # Создаем тестовые данные (имитация ваших входных таблиц)
    data_B = pd.DataFrame({
        'Название': [
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
' Triolein ',
'          ',
        ],
        'rt': [
            0.571,
            0.621,
            0.682,
            0.697,
            0.732,
            0.746,
            0.756,
            0.773,
            0.794,
            0.812,
            0.823,
            0.835,
            0.866,
            0.884,
            0.904,
            0.954,
            0.975,
            1    ,
            1.042,
        ],
        'A,%': [
            0.25,
            0.42,
            4.2,
            0.31,
            0.64,
            0.61,
            0.87,
            5.02,
            18.21,
            1.75,
            0.44,
            0.63,
            6.48,
            38.96,
            1.81,
            6.02,
            12.84,
            6.79,
            0.54,
        ]
    })
    
    data_C70 = pd.DataFrame({
        'Название': [
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
' Triolein ',
'          ',
        ],
        'rt': [
            0.682,
            0.746,
            0.755,
            0.773,
            0.794,
            0.812,
            0.865,
            0.884,
            0.905,
            0.932,
            0.953,
            0.976,
            1    ,
            1.02 ,
        ],
        'A,%': [
            3.68,
            1.47,
            0.36,
            0.89,
            9.35,
            2.05,
            12.17,
            33.22,
            0.36,
            0.42,
            33.96,
            1.53,
            5.28,
            0.54,
        ]
    })

    data_H150 = pd.DataFrame({
        'Название': [
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
'          ',
' Triolein ',
        ],
        'rt': [
0.682,
0.697,
0.723,
0.732,
0.746,
0.757,
0.772,
0.794,
0.81 ,
0.823,
0.828,
0.835,
0.866,
0.882,
0.901,
0.954,
0.973,
1    ,
        ],
        'A,%': [
1.43 ,
0.31 ,
0.31 ,
0.17 ,
0.4  ,
0.7  ,
4.43 ,
5.79 ,
11.81,
1.19 ,
1.26 ,
0.51 ,
0.52 ,
41.43,
16.37,
1.46 ,
11.93,
4.71 ,
        ]
    })

    # Упаковываем их в словарь
    samples = {
        'B': data_B,
        'C-70': data_C70,
        'H-150': data_H150
    }

    # Вызываем функцию
    result_table = merge_chromatography_data(samples, rt_col='rt', value_col='A,%')

    # Выводим результат
    print(result_table.to_markdown(index=False))
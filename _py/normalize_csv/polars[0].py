import polars as pl
import tkinter as tk
from tkinter import filedialog
import logging

# Настраиваем логирование в консоль
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

def main():
    root = tk.Tk()
    root.withdraw()

    logging.info("Ожидание выбора исходного файла...")
    input_file = filedialog.askopenfilename(
        title="Выберите CSV файл", 
        filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
    )
    
    if not input_file: 
        logging.warning("Файл не выбран. Операция отменена.")
        return

    logging.info(f"Выбран файл: {input_file}")

    try:
        # Читаем файл (разделитель ';' и без заголовков)
        df = pl.read_csv(input_file, separator=';', has_header=False)
        
        if len(df.columns) < 2:
            logging.error("В файле меньше двух столбцов! Проверьте структуру файла.")
            return

        col_name = df.columns[1] 
        logging.info(f"Обработка второго столбца: '{col_name}'")
        
        # Проверяем, прочитался ли столбец как текст
        if df.schema[col_name] in [pl.String, getattr(pl, 'Utf8', None)]:
            logging.info("Столбец распознан как текст. Очищаем от мусора и конвертируем в числа...")
            
            # --- ИСПРАВЛЕНИЕ ЗДЕСЬ ---
            # Агрессивно удаляем все пробелы, табуляции и скрытые символы перед конвертацией
            df = df.with_columns(
                pl.col(col_name)
                .str.replace_all(",", ".")       # Меняем запятые на точки
                .str.replace_all(" ", "")        # Удаляем обычные пробелы
                .str.replace_all("\r", "")       # Удаляем скрытые символы возврата каретки (Windows)
                .str.replace_all("\t", "")       # Удаляем табуляцию
                .cast(pl.Float64, strict=False)  # Превращаем в числа
            )
        else:
            df = df.with_columns(
                pl.col(col_name).cast(pl.Float64, strict=False)
            )

        # Считаем сумму
        total_sum = df[col_name].sum()
        
        if total_sum == 0 or total_sum is None:
            logging.error("Сумма значений равна нулю или столбец не содержит чисел! Деление невозможно.")
            return
            
        logging.info(f"Сумма столбца: {total_sum}. Выполняем нормализацию...")
        
        # Нормализуем столбец
        df = df.with_columns(
            (pl.col(col_name) / total_sum).alias(col_name)
        )

        logging.info("Ожидание выбора места для сохранения...")
        output_file = filedialog.asksaveasfilename(
            title="Сохранить нормализованный файл как...", 
            defaultextension=".csv", 
            filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
        )
        
        if not output_file: 
            logging.warning("Место для сохранения не выбрано. Операция отменена.")
            return

        # Сохраняем файл
        df.write_csv(output_file, separator=';', include_header=False)
        logging.info(f"УСПЕХ! Файл сохранен по пути: {output_file}")

    except Exception as e:
        logging.error(f"Произошла непредвиденная ошибка: {e}", exc_info=True)

if __name__ == "__main__":
    main()
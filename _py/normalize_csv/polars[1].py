import polars as pl
import tkinter as tk
from tkinter import filedialog
import logging
from pathlib import Path

# Настраиваем логирование в консоль
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

def main():
    root = tk.Tk()
    root.withdraw()

    logging.info("Ожидание выбора исходных файлов...")
    
    # 1. ПОЗВОЛЯЕМ ВЫБРАТЬ НЕСКОЛЬКО ФАЙЛОВ (askopenfilenames)
    input_files = filedialog.askopenfilenames(
        title="Выберите CSV файлы для обработки (можно выделить несколько)", 
        filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
    )
    
    if not input_files: 
        logging.warning("Файлы не выбраны. Операция отменена.")
        return

    logging.info(f"Выбрано файлов для обработки: {len(input_files)}")

    # 2. ЗАПУСКАЕМ ЦИКЛ ПО ВСЕМ ВЫБРАННЫМ ФАЙЛАМ
    for file_path in input_files:
        logging.info(f"--- Начинаем обработку: {file_path} ---")
        
        # Блок try-except теперь внутри цикла. 
        # Если один файл с ошибкой, скрипт не упадет, а перейдет к следующему.
        try:
            df = pl.read_csv(file_path, separator=';', has_header=False)
            
            if len(df.columns) < 2:
                logging.error(f"Пропуск файла: В нем меньше двух столбцов!")
                continue # Переходим к следующему файлу

            col_name = df.columns[1] 
            
            # Очистка и конвертация
            if df.schema[col_name] in [pl.String, getattr(pl, 'Utf8', None)]:
                df = df.with_columns(
                    pl.col(col_name)
                    .str.replace_all(",", ".")       
                    .str.replace_all(" ", "")        
                    .str.replace_all("\r", "")       
                    .str.replace_all("\t", "")       
                    .cast(pl.Float64, strict=False)  
                )
            else:
                df = df.with_columns(
                    pl.col(col_name).cast(pl.Float64, strict=False)
                )

            # Считаем сумму
            total_sum = df[col_name].sum()
            
            if total_sum == 0 or total_sum is None:
                logging.error(f"Пропуск файла: Сумма значений равна нулю или нет чисел!")
                continue
                
            # Нормализуем столбец
            df = df.with_columns(
                (pl.col(col_name) / total_sum).alias(col_name)
            )

            # 3. АВТОМАТИЧЕСКИ ФОРМИРУЕМ ИМЯ НОВОГО ФАЙЛА
            p = Path(file_path)
            # p.parent - папка, p.stem - имя без расширения, p.suffix - расширение (.csv)
            output_file = p.parent / f"{p.stem}{{Normalized}}{p.suffix}"

            # Сохраняем файл
            df.write_csv(output_file, separator=';', include_header=False)
            logging.info(f"УСПЕХ! Сохранено как: {output_file.name}")

        except Exception as e:
            logging.error(f"Ошибка при обработке файла {file_path}: {e}", exc_info=True)

    logging.info("=== Все выбранные файлы обработаны! ===")

if __name__ == "__main__":
    main()
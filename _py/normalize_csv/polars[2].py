import polars as pl
import tkinter as tk
from tkinter import filedialog
import logging
from pathlib import Path

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)

def main():
    root = tk.Tk()
    root.withdraw()

    logging.info("Ожидание выбора исходных файлов...")
    
    input_files = filedialog.askopenfilenames(
        title="Выберите CSV файлы для подготовки к DTW", 
        filetypes=[("CSV файлы", "*.csv"), ("Все файлы", "*.*")]
    )
    
    if not input_files: 
        logging.warning("Файлы не выбраны. Операция отменена.")
        return

    logging.info(f"Выбрано файлов для обработки: {len(input_files)}")

    for file_path in input_files:
        logging.info(f"--- Начинаем обработку: {file_path} ---")
        
        try:
            df = pl.read_csv(file_path, separator=';', has_header=False)
            
            if len(df.columns) < 2:
                logging.error(f"Пропуск файла: В нем меньше двух столбцов!")
                continue

            col_name = df.columns[1] 
            
            # 1. Очистка и конвертация в числа
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

            # Проверка, что данные не пустые и стандартное отклонение не равно нулю
            col_std = df[col_name].std()
            if col_std is None or col_std == 0:
                logging.error(f"Пропуск файла: Стандартное отклонение равно 0 (нет вариации данных)!")
                continue
                
            # 2. КОРРЕКЦИЯ БАЗОВОЙ ЛИНИИ (Baseline Correction)
            # Вычитаем минимальное значение, чтобы "дно" хроматограммы стало нулем
            df = df.with_columns(
                (pl.col(col_name) - pl.col(col_name).min()).alias(col_name)
            )

            # 3. Z-SCORE СТАНДАРТИЗАЦИЯ
            # Формула: (y - mean(y)) / std(y)
            df = df.with_columns(
                ((pl.col(col_name) - pl.col(col_name).mean()) / pl.col(col_name).std()).alias(col_name)
            )

            # Формируем имя нового файла с пометкой {Z-scored}
            p = Path(file_path)
            output_file = p.parent / f"{p.stem}{{Z-scored}}{p.suffix}"

            # Сохраняем файл
            df.write_csv(output_file, separator=';', include_header=False)
            logging.info(f"УСПЕХ! Сохранено как: {output_file.name}")

        except Exception as e:
            logging.error(f"Ошибка при обработке файла {file_path}: {e}", exc_info=True)

    logging.info("=== Все выбранные файлы подготовлены для DTW! ===")

if __name__ == "__main__":
    main()
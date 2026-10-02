import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os

class ConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Конвертер названий")
        self.root.geometry("900x500")
        
        self.mapping_dict = {}
        
        # Пытаемся загрузить JSON по умолчанию при старте
        self.default_json = 'mapping.json'
        self.load_json(self.default_json, show_info=False)

        self.setup_ui()

    def load_json(self, filepath, show_info=True):
        """Загружает JSON и создает словарь для быстрого поиска"""
        if not os.path.exists(filepath):
            if show_info:
                messagebox.showwarning("Ошибка", f"Файл {filepath} не найден!")
            return

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.mapping_dict = {}
            for short_name, long_names in data.items():
                for name in long_names:
                    self.mapping_dict[name.strip()] = short_name.strip()
                    
            if show_info:
                messagebox.showinfo("Успех", f"Загружено правил: {len(self.mapping_dict)}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось прочитать JSON:\n{e}")

    def setup_ui(self):
        # Верхняя панель с кнопкой загрузки JSON
        top_frame = tk.Frame(self.root, pady=5)
        top_frame.pack(fill=tk.X)
        
        btn_load_json = tk.Button(top_frame, text="Выбрать другой JSON файл", command=self.choose_json)
        btn_load_json.pack(side=tk.LEFT, padx=10)
        
        self.lbl_status = tk.Label(top_frame, text=f"Словарь: {'Загружен' if self.mapping_dict else 'Не загружен'}", fg="green" if self.mapping_dict else "red")
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        # Основной контейнер для текстовых полей
        main_frame = tk.Frame(self.root, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Левая часть (Ввод)
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(left_frame, text="Исходный список (вставьте сюда):").pack(anchor=tk.W)
        self.text_in = tk.Text(left_frame, wrap=tk.NONE)
        self.text_in.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_in_y = tk.Scrollbar(left_frame, command=self.text_in.yview)
        scroll_in_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_in.config(yscrollcommand=scroll_in_y.set)

        # Центральная часть (Кнопка)
        center_frame = tk.Frame(main_frame, padx=10)
        center_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        btn_convert = tk.Button(center_frame, text="Конвертировать\n>>", font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", command=self.convert_text)
        # Размещаем кнопку по центру по вертикали
        btn_convert.pack(expand=True)

        # Правая часть (Вывод)
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="Результат:").pack(anchor=tk.W)
        self.text_out = tk.Text(right_frame, wrap=tk.NONE)
        self.text_out.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll_out_y = tk.Scrollbar(right_frame, command=self.text_out.yview)
        scroll_out_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_out.config(yscrollcommand=scroll_out_y.set)

    def choose_json(self):
        filepath = filedialog.askopenfilename(
            title="Выберите JSON файл",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filepath:
            self.load_json(filepath)
            self.lbl_status.config(text="Словарь: Загружен", fg="green")

    def convert_text(self):
        if not self.mapping_dict:
            messagebox.showwarning("Внимание", "Словарь конвертации не загружен!")
            return

        # Получаем текст из левого поля
        input_data = self.text_in.get("1.0", tk.END).strip('\n')
        if not input_data:
            return

        lines = input_data.split('\n')
        output_lines = []

        for line in lines:
            clean_line = line.strip()
            # Если строка пустая, оставляем её пустой (чтобы сохранить структуру)
            if not clean_line:
                output_lines.append("")
                continue
            
            # Ищем в словаре. Если нет - оставляем оригинал
            converted = self.mapping_dict.get(clean_line, clean_line)
            output_lines.append(converted)

        # Очищаем правое поле и вставляем результат
        self.text_out.delete("1.0", tk.END)
        self.text_out.insert(tk.END, '\n'.join(output_lines))

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop()
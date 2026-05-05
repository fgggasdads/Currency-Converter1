import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os
from datetime import datetime


class CurrencyConverter:
    """Приложение для конвертации валют с сохранением истории."""
    
    # Список популярных валют
    CURRENCIES = ["USD", "EUR", "RUB", "GBP", "CNY", "JPY", "CHF", "CAD", "AUD", "TRY"]
    
    def __init__(self):
        """Инициализация приложения."""
        self.root = tk.Tk()
        self.root.title("Currency Converter")
        self.root.geometry("600x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")
        
        # API ключ (зарегистрируйтесь на https://app.exchangerate-api.com/sign-up)
        self.api_key = "ВАШ_API_КЛЮЧ"  # Замените на свой ключ
        self.base_url = "https://v6.exchangerate-api.com/v6"
        
        # Загрузка истории
        self.history = self.load_history()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление курсов при старте
        self.update_rates()
        
        self.root.mainloop()
    
    def create_widgets(self):
        """Создаёт все элементы интерфейса."""
        # Заголовок
        title = tk.Label(
            self.root,
            text="💱 Currency Converter",
            font=("Arial", 18, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        title.pack(pady=15)
        
        # Рамка для ввода
        input_frame = tk.Frame(self.root, bg="#ffffff", relief="groove", bd=2)
        input_frame.pack(pady=10, padx=20, fill="x")
        
        # Сумма
        tk.Label(input_frame, text="Сумма:", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.amount_entry = tk.Entry(input_frame, font=("Arial", 12), width=15)
        self.amount_entry.grid(row=0, column=1, padx=10, pady=10)
        
        # Валюта "из"
        tk.Label(input_frame, text="Из валюты:", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.from_currency = ttk.Combobox(input_frame, values=self.CURRENCIES, font=("Arial", 12), width=10)
        self.from_currency.grid(row=1, column=1, padx=10, pady=10)
        self.from_currency.set("USD")
        
        # Валюта "в"
        tk.Label(input_frame, text="В валюту:", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.to_currency = ttk.Combobox(input_frame, values=self.CURRENCIES, font=("Arial", 12), width=10)
        self.to_currency.grid(row=2, column=1, padx=10, pady=10)
        self.to_currency.set("EUR")
        
        # Курс
        tk.Label(input_frame, text="Текущий курс:", font=("Arial", 10, "bold"), bg="#ffffff").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.rate_label = tk.Label(input_frame, text="—", font=("Arial", 12), bg="#ffffff", fg="blue")
        self.rate_label.grid(row=3, column=1, padx=10, pady=10, sticky="w")
        
        # Кнопка конвертации
        self.convert_button = tk.Button(
            self.root,
            text="🔄 Конвертировать",
            command=self.convert,
            font=("Arial", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            cursor="hand2",
            width=20
        )
        self.convert_button.pack(pady=15)
        
        # Результат
        self.result_label = tk.Label(
            self.root,
            text="",
            font=("Arial", 14, "bold"),
            bg="#f0f0f0",
            fg="#333333"
        )
        self.result_label.pack(pady=5)
        
        # Рамка для истории
        history_frame = tk.Frame(self.root, bg="#ffffff", relief="groove", bd=2)
        history_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        tk.Label(history_frame, text="📜 История конвертаций:", font=("Arial", 10, "bold"), bg="#ffffff").pack(anchor="w", padx=10, pady=5)
        
        # Таблица истории (Treeview)
        columns = ("Дата", "Сумма", "Из", "В", "Результат")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=8)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=100)
        
        self.history_tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Кнопка очистки истории
        clear_btn = tk.Button(
            self.root,
            text="🗑️ Очистить историю",
            command=self.clear_history,
            font=("Arial", 10),
            bg="#f44336",
            fg="white",
            activebackground="#d32f2f",
            cursor="hand2"
        )
        clear_btn.pack(pady=5)
        
        # Обновление истории в таблице
        self.update_history_display()

    
    def update_rates(self):
        """Обновляет курс валют из API."""
        try:
            from_curr = self.from_currency.get()
            to_curr = self.to_currency.get()
            url = f"{self.base_url}/{self.api_key}/pair/{from_curr}/{to_curr}"
            response = requests.get(url, timeout=10)
            data = response.json()
            
            if data.get("result") == "success":
                rate = data["conversion_rate"]
                self.rate_label.config(text=f"1 {from_curr} = {rate} {to_curr}")
                return rate
            else:
                self.rate_label.config(text="Ошибка API")
                return None
        except Exception as e:
            self.rate_label.config(text="Нет соединения")
            return None
    
    def convert(self):
        """Выполняет конвертацию валюты."""
        # Проверка ввода суммы
        try:
            amount = float(self.amount_entry.get())
            if amount <= 0:
                messagebox.showwarning("Ошибка", "Сумма должна быть положительным числом!")
                return
        except ValueError:
            messagebox.showwarning("Ошибка", "Введите корректную сумму!")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        # Получение курса
        rate = self.update_rates()
        if rate is None:
            messagebox.showerror("Ошибка", "Не удалось получить курс валют")
            return
        
        # Конвертация
        result = amount * rate
        result_rounded = round(result, 2)
        
        # Отображение результата
        self.result_label.config(text=f"{amount} {from_curr} = {result_rounded} {to_curr}")
        
        # Сохранение в историю
        self.save_to_history(amount, from_curr, to_curr, result_rounded)
    
    def save_to_history(self, amount, from_curr, to_curr, result):
        """Сохраняет операцию в историю."""
        record = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "amount": amount,
            "from_currency": from_curr,
            "to_currency": to_curr,
            "result": result
        }
        self.history.append(record)
        self.save_history()
        self.update_history_display()
    
    def load_history(self):
        """Загружает историю из JSON-файла."""
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """Сохраняет историю в JSON-файл."""
        with open("history.json", "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def update_history_display(self):
        """Обновляет отображение истории в таблице."""
        # Очистка таблицы
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Добавление записей
        for record in reversed(self.history[-10:]):  # Показываем последние 10
            self.history_tree.insert("", "end", values=(
                record["date"],
                record["amount"],
                record["from_currency"],
                record["to_currency"],
                record["result"]
            ))
    
    def clear_history(self):
        """Очищает историю."""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю?"):
            self.history = []
            self.save_history()
            self.update_history_display()
            self.result_label.config(text="История очищена")


if __name__ == "__main__":
    CurrencyConverter()

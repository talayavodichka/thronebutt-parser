import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from src.race_parser import RaceParser

class RaceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ntrp")
        self.geometry("900x600")
        self.resizable(False, False)
        self.participants_data = []
        self.debug_mode = tk.BooleanVar(value=False)
        self.all_pages_mode = tk.BooleanVar(value=False)
        self.current_date = datetime.date.today()
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        input_frame = ttk.LabelFrame(main_frame, text="Параметры запроса")
        input_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(input_frame, text="Тип забега:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.race_type = ttk.Combobox(input_frame, values=["daily", "weekly"], state="readonly")
        self.race_type.current(0)
        self.race_type.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(input_frame, text="Год:").grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.year = ttk.Entry(input_frame, width=8)
        self.year.grid(row=0, column=3, padx=5, pady=5)
        self.year.insert(0, str(self.current_date.year))
        
        ttk.Label(input_frame, text="Месяц:").grid(row=0, column=4, padx=5, pady=5, sticky=tk.W)
        self.month = ttk.Entry(input_frame, width=5)
        self.month.grid(row=0, column=5, padx=5, pady=5)
        self.month.insert(0, f"{self.current_date.month:02d}")
        
        ttk.Label(input_frame, text="День:").grid(row=0, column=6, padx=5, pady=5, sticky=tk.W)
        self.day = ttk.Entry(input_frame, width=5)
        self.day.grid(row=0, column=7, padx=5, pady=5)
        self.day.insert(0, f"{self.current_date.day:02d}")
        
        ttk.Label(input_frame, text="Неделя:").grid(row=1, column=4, padx=5, pady=5, sticky=tk.W)
        self.week = ttk.Entry(input_frame, width=5)
        self.week.grid(row=1, column=5, padx=5, pady=5)
        week_num = self.current_date.isocalendar()[1]
        self.week.insert(0, str(week_num))
        
        ttk.Label(input_frame, text="Страница:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.page = ttk.Entry(input_frame, width=5)
        self.page.insert(0, "1")
        self.page.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(
            input_frame, 
            text="Загрузить данные", 
            command=self.load_data
        ).grid(row=1, column=8, padx=5, pady=5)

        ttk.Checkbutton(
            input_frame, 
            text="Режим отладки", 
            variable=self.debug_mode
        ).grid(row=1, column=9, padx=10, pady=5)

        ttk.Checkbutton(
            input_frame, 
            text="Все страницы", 
            variable=self.all_pages_mode
        ).grid(row=1, column=10, padx=10, pady=5)

        self.status_var = tk.StringVar(value="Готово")
        status_label = ttk.Label(input_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=11, sticky=tk.W, padx=5, pady=5)
        
        search_frame = ttk.Frame(main_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Поиск участника:").pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Найти", command=self.search_participant).pack(side=tk.LEFT, padx=5)
        
        columns = ("rank", "name", "distance", "kills")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        
        self.tree.heading("rank", text="Ранг")
        self.tree.heading("name", text="Участник")
        self.tree.heading("distance", text="Дистанция")
        self.tree.heading("kills", text="Убийства")
        
        self.tree.column("rank", width=50, anchor=tk.CENTER)
        self.tree.column("name", width=200)
        self.tree.column("distance", width=80, anchor=tk.CENTER)
        self.tree.column("kills", width=80, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.race_type.bind("<<ComboboxSelected>>", self.update_input_fields)
        self.update_input_fields()
    
    def update_input_fields(self, event=None):
        race_type = self.race_type.get()
        if race_type == "daily":
            self.week.config(state=tk.DISABLED)
            self.month.config(state=tk.NORMAL)
            self.day.config(state=tk.NORMAL)
        else:
            self.week.config(state=tk.NORMAL)
            self.month.config(state=tk.DISABLED)
            self.day.config(state=tk.DISABLED)
    
    def load_data(self):
        race_type = self.race_type.get()
        year = self.year.get().strip()
        page = self.page.get().strip()
        debug = self.debug_mode.get()
        all_pages = self.all_pages_mode.get()
        
        if debug:
            print("\n" + "="*50)
            print(f"Загрузка данных: {datetime.datetime.now()}")
            print(f"Режим всех страниц: {all_pages}")
        
        if not year:
            messagebox.showwarning("Ошибка", "Заполните обязательное поле: Год")
            return
        
        if race_type == "daily":
            month = self.month.get().strip()
            day = self.day.get().strip()
            if not month or not day:
                messagebox.showwarning("Ошибка", "Для ежедневного забега укажите месяц и день")
                return
            identifier = (month, day)
        else:
            week = self.week.get().strip()
            if not week:
                messagebox.showwarning("Ошибка", "Для еженедельного забега укажите номер недели")
                return
            identifier = week

        self.participants_data = []
        
        if all_pages:
            self.status_var.set("Загрузка всех страниц...")
            self.update_idletasks()
            
            page = 1
            total_participants = 0
            
            while True:
                if debug:
                    print(f"Загрузка страницы {page}...")
                
                self.status_var.set(f"Загрузка страницы {page}...")
                self.update_idletasks()
                
                participants = RaceParser.parse_race(race_type, year, identifier, page, debug)
                
                if participants is None:
                    break
                
                if not participants:
                    if debug:
                        print(f"Страница {page} пуста, завершение")
                    break
                
                self.participants_data.extend(participants)
                total_participants += len(participants)
                
                if debug:
                    print(f"Страница {page}: загружено {len(participants)} участников")
                
                page += 1
            
            self.status_var.set(f"Загружено {total_participants} участников с {page-1} страниц")
        else:
            if not page:
                messagebox.showwarning("Ошибка", "Укажите номер страницы")
                return
            
            self.status_var.set(f"Загрузка страницы {page}...")
            self.update_idletasks()
            
            participants = RaceParser.parse_race(race_type, year, identifier, page, debug)
            if participants is not None:
                self.participants_data = participants
                self.status_var.set(f"Загружено {len(participants)} участников")
        
        if self.participants_data:
            self.display_data(self.participants_data)
            
            if debug:
                print(f"Всего загружено участников: {len(self.participants_data)}")
        else:
            self.tree.delete(*self.tree.get_children())
            self.status_var.set("Участники не найдены")
    
    def display_data(self, data):
        self.tree.delete(*self.tree.get_children())
        for item in data:
            self.tree.insert("", tk.END, values=(
                item['rank'],
                item['name'],
                item['distance'],
                item['kills']
            ))
    
    def search_participant(self):
        query = self.search_entry.get().lower().strip()
        if not query:
            self.display_data(self.participants_data)
            return
        
        filtered = [p for p in self.participants_data if query in p['name'].lower()]
        self.display_data(filtered)
        
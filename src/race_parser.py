from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import re

class RaceParser:
    BASE_URL = "https://beta.thronebutt.com"
    
    @staticmethod
    def parse_race(race_type, year, identifier, page, debug=False):
        if debug:
            print(f"Начало парсинга: {race_type}, {year}, {identifier}, стр. {page}")
        
        if race_type == "daily":
            url = f"{RaceParser.BASE_URL}/daily/{year}/{identifier[0]}/{identifier[1]}/{page}"
        else:
            url = f"{RaceParser.BASE_URL}/weekly/{year}/{identifier}/{page}"
        
        if debug:
            print(f"Формирование URL: {url}")
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            if debug:
                print(f"HTTP статус: {response.status_code}")
                print(f"Размер ответа: {len(response.text)} байт")
            
            soup = BeautifulSoup(response.text, 'html.parser')

            no_scores = soup.find('div', class_=re.compile(r'text-center'))
            if no_scores and "No scores!" in no_scores.get_text():
                if debug:
                    print("Обнаружено 'No scores' - участников нет")
                return []
            
            participants = []
            score_plates = soup.find_all('div', class_='score_plate')

            if debug:
                print(f"Найдено записей: {len(score_plates)}")
                if score_plates:
                    print("Пример HTML записи:")
                    print(score_plates[0].prettify()[:500] + "...")
            
            for plate in score_plates:
                try:
                    rank = plate.get('data-rank', 'N/A')

                    name_div = plate.select_one('div.break-all, div.break-words')
                    name = name_div.get_text(strip=True) if name_div else "N/A"

                    level_spans = plate.select('div.flex.flex-col.gap-1 span')
                    distance = " ".join(span.get_text(strip=True) for span in level_spans) if level_spans else "N/A"

                    kills_div = plate.select_one('div.nt-text-shadow.text-right')
                    kills = kills_div.get_text(strip=True) if kills_div else "N/A"
                    
                    if debug:
                        print(f"  Участник: rank={rank}, name={name}, distance={distance}, kills={kills}")
                    
                    participants.append({
                        'rank': rank,
                        'name': name,
                        'distance': distance,
                        'kills': kills
                    })
                except Exception as e:
                    if debug:
                        print(f"Ошибка обработки элемента: {str(e)}")
                    continue
                
            return participants
        except Exception as e:
            if debug:
                print(f"Ошибка парсинга: {str(e)}")
                import traceback
                traceback.print_exc()
            messagebox.showerror("Ошибка", f"Ошибка при получении данных: {str(e)}")
            return None
        
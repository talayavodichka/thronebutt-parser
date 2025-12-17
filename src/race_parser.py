import aiohttp
from bs4 import BeautifulSoup
import re

class RaceParser:
    BASE_URL = "https://thronebutt.com"
    
    @staticmethod
    async def get_participants(url, debug):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                response.raise_for_status()
                text = await response.text()
    
        if debug:
            print(f"HTTP status: {response.status}")
            print(f"Response size: {len(text)} байт")
        
        soup = BeautifulSoup(text, 'html.parser')

        no_scores = soup.find('div', class_=re.compile(r'text-center'))
        if no_scores and "No scores!" in no_scores.get_text():
            if debug:
                print("No scores detected - no participants")
            return []
        
        participants = []
        score_plates = soup.find_all('div', class_='score_plate')

        if debug:
            print(f"Records found: {len(score_plates)}")
        
        for plate in score_plates:
            try:
                rank = plate.get('data-rank', 'N/A')

                name_div = plate.select_one('div.break-all, div.break-words')
                name = name_div.get_text(strip=True) if name_div else "N/A"

                level_spans = plate.select('div.flex.flex-col.gap-1 span')
                distance = " ".join(span.get_text(strip=True) for span in level_spans) if level_spans else "N/A"

                kills_div = plate.select_one('div.hidden.sm\\:flex div.nt-text-shadow.text-right')

                if not kills_div:
                    kills_div = plate.select_one('div.flex.sm\\:hidden div.nt-text-shadow')
                
                kills = kills_div.get_text(strip=True).replace(',', '') if kills_div else "N/A"
                
                if debug:
                    print(f"Participant: rank={rank}, name={name}, distance={distance}, kills={kills}")
                
                participants.append({
                    'rank': rank,
                    'name': name,
                    'distance': distance,
                    'kills': kills
                })
            except Exception as e:
                if debug:
                    print(f"Error processing element: {str(e)}")
                continue
            
        return participants

    @staticmethod
    async def parse_race(race_type, year, identifier, page, debug=False):
        if debug:
            print(f"Start of parsing: {race_type}, {year}, {identifier}, page {page}")
        
        if race_type == "daily":
            url = f"{RaceParser.BASE_URL}/daily/{year}/{identifier[0]}/{identifier[1]}/{page}"
        else:
            url = f"{RaceParser.BASE_URL}/weekly/{year}/{identifier}/{page}"
        
        if debug:
            print(f"URL generation: {url}")
        
        try:
            return await RaceParser.get_participants(url, debug)
        except Exception as e:
            if debug:
                print(f"Parsing error: {str(e)}")
                import traceback
                traceback.print_exc()
            raise
    
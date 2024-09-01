import requests
from bs4 import BeautifulSoup
import json
import time
import concurrent.futures

def get_player_details(player_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(player_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {player_url}: {e}")
        return {"birthdate": "N/A"}

    soup = BeautifulSoup(response.content, 'html.parser')

    # Coleta da data de nascimento
    birthdate = "N/A"
    birthdate_cell = soup.find('span', {"itemprop": "birthDate"})
    if birthdate_cell:
        birthdate = birthdate_cell.get_text(strip=True)

    return {"birthdate": birthdate}

def get_players_for_club_year(club_id, year):
    url = f"https://www.transfermarkt.com/real-madrid/startseite/verein/{club_id}/saison_id/{year}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', {"class": "items"})
    if not table:
        print(f"Tabela não encontrada para {year}")
        return []

    players = []
    rows = table.find_all('tr')[1:]  # Ignora o cabeçalho

    def process_row(row):
        name_cell = row.find('td', {"class": "hauptlink"})
        market_value_cell = row.find('td', {"class": "rechts hauptlink"})
        nationality_img = row.find('img', {"class": "flaggenrahmen"})

        if name_cell and market_value_cell and nationality_img:
            name = name_cell.get_text(strip=True)
            nationality = nationality_img.get('title', "N/A")
            market_value = market_value_cell.get_text(strip=True)

            # Extrair o link do jogador para acessar a página de detalhes
            player_link = name_cell.find('a', href=True)['href']
            player_url = f"https://www.transfermarkt.com{player_link}"

            # Obter a data de nascimento do jogador
            details = get_player_details(player_url)

            player = {
                "name": name,
                "birthdate": details["birthdate"],
                "nationality": nationality,
                "market_value": market_value
            }

            return player
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_row, row) for row in rows]
        for future in concurrent.futures.as_completed(futures):
            player = future.result()
            if player:
                players.append(player)

    return players

# IDs dos clubes no Transfermarkt
club_ids = {
    "Real Madrid": 418,
    "Barcelona": 131,
    "PSG": 583,
    "Manchester City": 281,
    "Manchester United": 985,
    "Juventus": 506,
    "Milan": 5,
    "Arsenal": 11,
    "Liverpool": 31,
    "Chelsea": 631,
    "Bayern de Munique": 27,
    "Borussia Dortmund": 16,
    "Inter de Milão": 46,
    "Olympique de Marseille": 244,
    "Ajax": 610,
    "Napoli": 6195,
    "Atlético de Madrid": 13,
    "Benfica": 294,
    "Porto": 720,
    "Lyon": 1041
}

# Anos de 2000 até 2023 (para evitar anos sem dados)
years = range(1995, 2024)

for club, club_id in club_ids.items():
    club_data = {}
    for year in years:
        print(f"Coletando dados para {club} - Ano {year}")
        players = get_players_for_club_year(club_id, year)
        club_data[str(year)] = players
        time.sleep(2)  # Pausa para evitar bloqueio

    filename = f"{club.lower().replace(' ', '_')}_2000_2023_com_dados_completos.json"
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(club_data, f, ensure_ascii=False, indent=4)

    print(f"Dados do {club} de 2000 até 2023 salvos em {filename}")
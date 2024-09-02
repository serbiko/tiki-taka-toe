import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

def get_player_info(player_name):
    search_url = f"https://www.google.com/search?q=Transfermarkt+{player_name.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o Google para {player_name}: {e}")
        return None, None

    soup = BeautifulSoup(response.content, 'html.parser')
    player_id = None
    formatted_name = None

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "transfermarkt" in href and "profil/spieler" in href:
            try:
                player_id = href.split("spieler/")[1].split("&")[0]
                formatted_name = href.split(".com.br/")[1].split("/")[0]
                break
            except IndexError:
                continue

    if not player_id or not formatted_name:
        print(f"Nenhum ID Transfermarkt encontrado para {player_name}.")
        return None, None

    return player_id, formatted_name

def extract_player_data(player_name, player_id, missing_seasons):
    url = f"https://www.transfermarkt.com.br/{player_name}/detaillierteleistungsdaten/spieler/{player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Não achei a URL certa para", player_name)
        return []

    soup = BeautifulSoup(response.content, 'html.parser')

    data = []
    for row in soup.find_all('tr', class_=['even', 'odd']):
        season = row.find('td', class_='zentriert').text.strip()

        if len(season) == 5:
            full_season = "20" + season
        else:
            full_season = season
        
        if full_season in missing_seasons:
            club_name_tag = row.find('a', title=True)
            if club_name_tag:
                club_name = club_name_tag['title']
                data.append(f"{season} {club_name}")

    return data

def process_player(player, missing_seasons):
    print(f"Processando {player}...")
    player_id, formatted_name = get_player_info(player)

    if player_id and formatted_name:
        player_data = extract_player_data(formatted_name, player_id, missing_seasons)
        if player_data:
            return player, player_data
        else:
            print(f"Não foram encontrados dados para as temporadas faltantes de {player}.")
            return player, []
    else:
        print(f"Não foi possível encontrar informações para {player}.")
        return player, []

def process_missing_data(missingdata_path, max_workers=10):
    with open(missingdata_path, 'r') as file:
        missing_data = json.load(file)

    # Processar apenas os primeiros 10 jogadores
    limited_missing_data = dict(list(missing_data.items())[:10])

    completed_data = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_player, player, seasons) for player, seasons in limited_missing_data.items()]
        
        for future in as_completed(futures):
            player, data = future.result()
            if data:
                completed_data[player] = data

    with open('completingdata_10.json', 'w') as outfile:
        json.dump(completed_data, outfile, indent=4, ensure_ascii=False)

    print("Processo concluído.")

# Processar apenas os primeiros 10 jogadores
process_missing_data('missingdata.json', max_workers=10)

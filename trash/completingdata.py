import json
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import unicodedata

# Função para normalizar o texto e lidar com caracteres especiais
def normalize_text(text):
    return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

# Função para obter informações do jogador
def get_player_info(player_name):
    search_url = f"https://www.google.com/search?q=Transfermarkt+{player_name.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Referer": "https://www.google.com",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
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

# Função para extrair dados do jogador
def extract_player_data(player_name, player_id, missing_seasons):
    url = f"https://www.transfermarkt.com.br/{player_name}/detaillierteleistungsdaten/spieler/{player_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Referer": "https://www.transfermarkt.com.br",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar {url}: {e}")
        return []

    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    data = []
    for row in soup.find_all('tr', class_=['even', 'odd']):
        season = row.find('td', class_='zentriert').text.strip()

        if len(season) == 5:
            full_season = "20" + season
        else:
            full_season = season
        
        if full_season in missing_seasons:
            club_td = row.find('td', class_='hauptlink no-border-rechts zentriert')
            if club_td:
                club_img = club_td.find('a').find('img')
                if club_img:
                    club_name = normalize_text(club_img['alt'])
                    data.append(f"{season} {club_name}")

    return data

# Função para processar cada jogador
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

# Função principal para processar os dados faltantes
def process_missing_data(missingdata_path, output_path, failures_path, max_workers=5):
    with open(missingdata_path, 'r', encoding='utf-8') as file:
        missing_data = json.load(file)

    completed_data = {}
    failures = {}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(process_player, player, seasons) for player, seasons in missing_data.items()]
        
        for future in as_completed(futures):
            player, data = future.result()
            if data:
                completed_data[player] = data
            else:
                failures[player] = missing_data[player]
            time.sleep(10)  # Pequeno delay para evitar bloqueios

    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(completed_data, outfile, indent=4, ensure_ascii=False)

    if failures:
        with open(failures_path, 'w', encoding='utf-8') as failure_file:
            json.dump(failures, failure_file, indent=4, ensure_ascii=False)

    print("Processo concluído.")

# Chamada da função principal para processar todos os jogadores
process_missing_data('missingdata.json', 'testingdata.json', 'failures.json', max_workers=1)

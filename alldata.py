import os
import requests
import json
from bs4 import BeautifulSoup
import time

# Função para buscar o ID do jogador e coletar seus dados de clubes no Transfermarkt
def get_player_id_and_clubs(player_name):
    # Buscar o perfil do jogador no Google
    search_url = f"https://www.google.com/search?q=Transfermarkt+{player_name.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o Google para {player_name}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    player_id = None

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "transfermarkt" in href and "profil/spieler" in href:
            try:
                player_id = href.split("spieler/")[1].split("&")[0]
                break
            except IndexError:
                continue

    if not player_id:
        print(f"Nenhum ID Transfermarkt encontrado para {player_name} no Google.")
        return None

    # Construir a URL da página de desempenho do jogador usando o ID
    performance_url = f"https://www.transfermarkt.com.br/{player_name.replace(' ', '-').lower()}/leistungsdatendetails/spieler/{player_id}/plus/1"

    max_retries = 10  # Número máximo de tentativas
    for attempt in range(max_retries):
        try:
            performance_response = requests.get(performance_url, headers=headers, timeout=30)
            performance_response.raise_for_status()
            break  # Sai do loop se a requisição for bem-sucedida
        except requests.exceptions.RequestException as e:
            print(f"Tentativa {attempt + 1} de acessar a página de desempenho de {player_name} falhou: {e}")
            time.sleep(10)  # Aguarda 10 segundos antes de tentar novamente
    else:
        print(f"Erro ao acessar a página de desempenho de {player_name} após {max_retries} tentativas.")
        return None

    performance_soup = BeautifulSoup(performance_response.content, 'html.parser')

    clubs = []
    current_club = None
    current_season = None

    # Procura pela tabela de desempenho
    table = performance_soup.find('table', class_='items')
    if not table:
        print(f"Tabela de desempenho não encontrada para {player_name}.")
        return []

    rows = table.find_all('tr')
    for row in reversed(rows):  # Itera de trás para frente
        season = row.find('td', class_='zentriert')  # Pega a temporada
        club_tag = row.find('img', class_='tiny_wappen')  # Pega o clube

        if season and club_tag:
            season_text = season.get_text(strip=True)
            club = club_tag['title']

            if season_text != current_season or club != current_club:
                clubs.append(f"{season_text} {club}")
                current_season = season_text
                current_club = club

    if not clubs:
        print(f"Nenhum clube encontrado para {player_name}.")
    
    return clubs

# Carrega o arquivo JSON com os jogadores
with open('dicionarios/allplayers.json', 'r', encoding='utf-8') as file:
    all_players = json.load(file)

# Processa todos os jogadores do arquivo
player_data = {}
failed_players = []  # Lista para armazenar jogadores que falharam

for player_name in all_players:  # Assumindo que all_players é uma lista de nomes
    print(f"Processando {player_name}...")
    clubs = get_player_id_and_clubs(player_name)
    if clubs:
        player_data[player_name] = clubs
    else:
        failed_players.append(player_name)  # Registra o jogador que falhou
    time.sleep(2)  # Pausa para evitar bloqueio por parte do Transfermarkt

# Salva os dados coletados no arquivo alldata.json
with open('dicionarios/alldata.json', 'w', encoding='utf-8') as outfile:
    json.dump(player_data, outfile, ensure_ascii=False, indent=4)

# Registra jogadores que falharam
if failed_players:
    with open('dicionarios/failed_players.json', 'w', encoding='utf-8') as failfile:
        json.dump(failed_players, failfile, ensure_ascii=False, indent=4)
    print(f"{len(failed_players)} jogadores falharam. Veja 'dicionarios/failed_players.json' para mais detalhes.")

print("Dados salvos em dicionarios/alldata.json.")

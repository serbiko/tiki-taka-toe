import requests
from bs4 import BeautifulSoup
import json

# Função para obter os dados de desempenho do jogador a partir do URL
def get_player_data(player_name, player_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(player_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar a página de desempenho de {player_name}: {e}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')
    player_data = []

    # Encontrar a tabela que contém a seção "Ligas nacionais"
    tables = soup.find_all('table', class_='items')
    if not tables:
        print(f"Não foi possível encontrar a tabela de Ligas nacionais para {player_name}.")
        return None

    for table in tables:
        previous_h2 = table.find_previous('h2')
        if previous_h2 and "Ligas nacionais" in previous_h2.text:
            rows = table.find_all('tr')
            for row in rows:
                season_cell = row.find("td", {"class": "zentriert"})
                club_cell = row.find("a", title=True)

                if season_cell and club_cell:
                    season_text = season_cell.get_text(strip=True)
                    club_name = club_cell.get("title").strip()

                    # Verifica se a combinação já existe
                    if len(player_data) == 0 or player_data[-1] != f"{season_text} {club_name}":
                        player_data.append(f"{season_text} {club_name}")
            break

    # Inverte a ordem para mostrar do último para o primeiro
    player_data.reverse()

    return player_data

# Função para atualizar o arquivo JSON com os novos dados
def update_json_file(player_name, player_data, json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}

    # Adiciona ou atualiza as informações do jogador
    data[player_name] = player_data

    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Links e nomes dos jogadores
players = {
    "Charly Musonda Jr.": "https://www.transfermarkt.com.br/charly-musonda-jr-/detaillierteleistungsdaten/spieler/177862",
    "Micah Richards": "https://www.transfermarkt.com.br/micah-richards/detaillierteleistungsdaten/spieler/32617",
    "N'Golo Kanté": "https://www.transfermarkt.com.br/ngolo-kante/detaillierteleistungsdaten/spieler/225083",
    "Samuel Eto'o": "https://www.transfermarkt.com.br/samuel-etoo/detaillierteleistungsdaten/spieler/4257"
}

# Caminho para o arquivo JSON
json_file = 'dicionarios/alldata.json'

# Processa cada jogador e atualiza o arquivo JSON
for player_name, player_url in players.items():
    print(f"Processando {player_name}...")
    player_data = get_player_data(player_name, player_url)
    if player_data:
        update_json_file(player_name, player_data, json_file)
        print(f"Dados de {player_name} atualizados com sucesso.")
    else:
        print(f"Não foi possível obter os dados de {player_name}.")

print("Processo concluído.")

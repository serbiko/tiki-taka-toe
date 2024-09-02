import os
import requests
import json
from bs4 import BeautifulSoup
import time

# Função para buscar e baixar a imagem de um jogador no Transfermarkt via Google
def get_player_id_and_download_image(player_name):
    # Buscar o perfil do jogador no Google
    search_url = f"https://www.google.com/search?q=Transfermarkt+{player_name.replace(' ', '+')}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o Google para {player_name}: {e}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    player_id = None

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        if "transfermarkt" in href and "profil/spieler" in href:
            # Extraindo o ID do jogador a partir do link
            try:
                player_id = href.split("spieler/")[1].split("&")[0]
                break
            except IndexError:
                continue

    if not player_id:
        print(f"Nenhum ID Transfermarkt encontrado para {player_name} no Google.")
        return

    # Construir a URL do perfil do jogador usando o ID
    player_profile_url = f"https://www.transfermarkt.com.br/{player_name.replace(' ', '-').lower()}/profil/spieler/{player_id}"

    try:
        profile_response = requests.get(player_profile_url, headers=headers, timeout=10)
        profile_response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao acessar o perfil do jogador {player_name}: {e}")
        return

    profile_soup = BeautifulSoup(profile_response.content, 'html.parser')

    # Tenta encontrar a imagem do jogador na página de perfil
    image_tag = profile_soup.find("img", {"class": "data-header__profile-image"})
    if not image_tag:
        print(f"Nenhuma imagem encontrada para {player_name} no perfil do Transfermarkt.")
        return

    image_url = image_tag["src"]
    image_filename = os.path.join("transfermarkt", f"{player_name}.jpg")

    try:
        img_data = requests.get(image_url).content
        with open(image_filename, 'wb') as handler:
            handler.write(img_data)
        print(f"Imagem de {player_name} baixada com sucesso como {image_filename}")
    except Exception as e:
        print(f"Erro ao baixar a imagem de {player_name}: {e}")

# Cria o diretório transfermarkt se não existir
if not os.path.exists("transfermarkt"):
    os.makedirs("transfermarkt")

# Carrega o arquivo JSON com os jogadores
with open('dicionarios/players_connections.json', 'r', encoding='utf-8') as file:
    players_data = json.load(file)

# Itera sobre os jogadores que são as chaves principais no arquivo e baixa as imagens
for player_name in players_data.keys():
    get_player_id_and_download_image(player_name)
    time.sleep(2)  # Pausa para evitar bloqueio por parte do Transfermarkt

print("Download de imagens concluído.")

import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configuração do Selenium WebDriver em modo headless
chrome_options = Options()
chrome_options.add_argument("--headless")  # Executa em modo headless (sem abrir a janela do navegador)
chrome_options.add_argument("--disable-gpu")  # Desativa o uso de GPU (para maior compatibilidade)
chrome_options.add_argument("--window-size=1920x1080")  # Define o tamanho da janela virtual

driver = webdriver.Chrome(options=chrome_options)

# Lista de frases proibidas que não devem ser incluídas no JSON
prohibited_phrases = [
    "What defines a link between players?",
    "Why don't national teams count?",
    "I think I found a mistake because I found a link but the game says it's wrong.",
    "How can I contact you?",
    "Why do I keep getting the same players?",
    "Can I share my game with others?",
    "I have an idea/feedback for this site. How can I get it to you?"
]

# Função para simular o jogo e pegar as respostas corretas
def play_game_and_get_correct_answers(page_number):
    correct_answers = []
    print(f"Processando página {page_number}")
    
    # Acessa o site do Link the Players
    driver.get('https://www.linktheplayers.com/')
    
    try:
        # Aguarda até que o botão "desistir" esteja presente e clicável
        give_up_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//button[text()="Give Up"]'))
        )
        
        # Clica no botão "desistir"
        give_up_button.click()
        
        time.sleep(1)  # Espera os resultados aparecerem após clicar em "desistir"
        
        # Pega os dois jogadores principais
        players = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.XPATH, '//h2[@class="chakra-heading css-us8mxz"]'))
        )
        player1 = players[0].text
        player2 = players[1].text
        
        # Pega as respostas corretas após o jogo
        correct_answer_elements = WebDriverWait(driver, 5).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'css-1eziwv'))
        )
        for element in correct_answer_elements:
            text = element.text
            if text not in prohibited_phrases:
                correct_answers.append(text)
        
        return player1, player2, correct_answers
    
    except Exception as e:
        print(f"Erro ao tentar pegar o elemento: {e}")
        return None, None, []

# Função para atualizar o JSON com as novas conexões
def update_json_with_connections(data, player1, player2, correct_answers):
    # Verifica se player1 já existe no JSON
    if player1 not in data:
        data[player1] = []
    if player2 not in data:
        data[player2] = []
    
    # Atualiza a lista de conexões de player1 e player2
    for answer in correct_answers:
        if answer not in data[player1]:
            data[player1].append(answer)
        if answer not in data[player2]:
            data[player2].append(answer)

# Função para registrar os jogadores em matches.json
def update_matches_json(matches, player1, player2):
    matches.append({"player1": player1, "player2": player2})
    
    # Salva em tempo real
    with open('matches.json', 'w', encoding='utf-8') as f:
        json.dump(matches, f, ensure_ascii=False, indent=4)

# Inicializa a lista de matches
matches = []

# Main loop para realizar 1000 jogos e salvar os resultados
data = {}
for page_number in range(1, 1001):
    player1, player2, correct_answers = play_game_and_get_correct_answers(page_number)
    if player1 and player2:
        update_json_with_connections(data, player1, player2, correct_answers)
        update_matches_json(matches, player1, player2)

        # Salvando o progresso a cada iteração para não perder os dados
        with open('players_connections.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

# Finalizando o WebDriver
driver.quit()

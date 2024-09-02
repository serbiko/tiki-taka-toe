import json

def extract_unique_names(json_file):
    with open(json_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    unique_names = set()  # Usamos um conjunto para evitar duplicatas

    for player, connections in data.items():
        unique_names.add(player)  # Adiciona o jogador "dono" da lista
        unique_names.update(connections)  # Adiciona todos os jogadores conectados

    return sorted(unique_names)  # Retorna uma lista ordenada com os nomes únicos

def save_to_json(data, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

# Especifique o caminho completo para o arquivo JSON de entrada
json_file = 'C:/Users/andre/OneDrive/Documentos/tiki-taka-toe/dicionarios/players_connections.json'

# Extraindo os nomes únicos
unique_names = extract_unique_names(json_file)

# Salvando os nomes únicos em um arquivo JSON
output_file = 'C:/Users/andre/OneDrive/Documentos/tiki-taka-toe/allplayers.json'
save_to_json(unique_names, output_file)

print(f"Nomes únicos salvos em {output_file}")

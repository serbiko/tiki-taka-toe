import json

# Função para extrair os anos de uma temporada no formato "XX/YY" ou "YYYY"
def extract_years_from_season(season):
    parts = season.split('/')
    if len(parts) == 2:
        try:
            start_year = int(parts[0][-2:])  # Pega os últimos dois dígitos do ano
            full_start_year = 2000 + start_year if start_year < 50 else 1900 + start_year
            print(f"Extraído ano {full_start_year} da temporada {season}")
        except ValueError:
            print(f"Erro ao tentar extrair o ano da temporada: {season}")
            return None
    else:
        try:
            full_start_year = int(season.split()[0])
            print(f"Extraído ano {full_start_year} da temporada {season}")
        except ValueError:
            print(f"Erro ao tentar extrair o ano da temporada: {season}")
            return None
    return full_start_year

# Função para identificar as temporadas faltantes
def identify_missing_seasons(player_data):
    seasons = []
    for entry in player_data:
        season_year = extract_years_from_season(entry.split(' ')[0])
        if season_year:
            seasons.append(season_year)
    
    print(f"Anos extraídos e ordenados: {seasons}")

    if not seasons:
        print("Nenhum ano válido encontrado.")
        return []

    seasons.sort()
    print(f"Temporadas após ordenação: {seasons}")
    
    missing_seasons = []

    for i in range(len(seasons) - 1):
        if seasons[i] + 1 < seasons[i + 1]:  # Verifica se há um salto
            for year in range(seasons[i] + 1, seasons[i + 1]):
                missing_season = f"{year}/{str(year+1)[-2:]}"
                missing_seasons.append(missing_season)
                print(f"Salto encontrado entre {seasons[i]} e {seasons[i + 1]}: Temporada {missing_season} está faltando.")

    return missing_seasons

# Função principal para verificar todos os jogadores e encontrar dados faltantes
def find_missing_data(all_players_data):
    missing_data = {}

    for player, career_data in all_players_data.items():
        print(f"Processando jogador: {player}")
        missing_seasons = identify_missing_seasons(career_data)
        if missing_seasons:
            missing_data[player] = missing_seasons
            print(f"Dados faltantes para {player}: {missing_seasons}")
        else:
            print(f"Nenhum dado faltante encontrado para {player}.")

    return missing_data

def main():
    with open('dicionarios/alldata.json', 'r', encoding='utf-8') as f:
        all_players_data = json.load(f)

    missing_data = find_missing_data(all_players_data)

    # Adicionando um log para verificar se os dados estão sendo preparados corretamente para gravação
    print(f"Dados faltantes preparados para gravação: {missing_data}")

    # Verifique se há dados para salvar antes de abrir o arquivo
    if missing_data:
        with open('missingdata.json', 'w', encoding='utf-8') as f:
            json.dump(missing_data, f, indent=4, ensure_ascii=False)
        print("Dados faltantes foram identificados e salvos em missingdata.json.")
    else:
        print("Nenhum dado faltante identificado, o arquivo não será salvo.")

if __name__ == "__main__":
    main()

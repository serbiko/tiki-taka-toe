let currentFocus = -1;
let attempts = []; // Armazena as tentativas do jogador
const maxAttempts = 5; // Número máximo de tentativas

// Função para carregar o arquivo JSON contendo todos os jogadores "encabeçadores"
function loadPlayersConnections(jsonFile, callback) {
    fetch(jsonFile)
        .then(response => response.json())
        .then(data => callback(data))
        .catch(error => console.error('Erro ao carregar o arquivo JSON:', error));
}

// Função para sortear uma dupla de jogadores "encabeçadores" com pelo menos um jogador em comum
function getRandomPair(playersConnections) {
    let player1, player2, commonPlayers;
    const playerKeys = Object.keys(playersConnections);
    do {
        player1 = playerKeys[Math.floor(Math.random() * playerKeys.length)];
        player2 = playerKeys[Math.floor(Math.random() * playerKeys.length)];
        commonPlayers = playersConnections[player1].filter(player => playersConnections[player2].includes(player));
    } while (player1 === player2 || commonPlayers.length === 0);
    return [player1, player2, commonPlayers];
}

// Função para filtrar jogadores com base no texto digitado
function filterPlayers(query, players) {
    return players.filter(player => player.toLowerCase().includes(query.toLowerCase()));
}

// Função para destacar as letras correspondentes na pesquisa
function highlightMatch(player, query) {
    const regex = new RegExp(`(${query})`, 'gi');
    return player.replace(regex, "<strong>$1</strong>");
}

// Função principal que configura o comportamento da barra de pesquisa
function setupSearchBar(players, commonPlayers) {
    const searchInput = document.getElementById('search');
    const suggestionsContainer = document.getElementById('suggestions');

    searchInput.addEventListener('input', function() {
        const query = this.value;
        suggestionsContainer.innerHTML = '';
        currentFocus = -1; // Reset the current focus
        if (query) {
            const suggestions = filterPlayers(query, players);
            suggestions.forEach((suggestion, index) => {
                const div = document.createElement('div');
                div.innerHTML = highlightMatch(suggestion, query);
                div.addEventListener('click', () => {
                    searchInput.value = suggestion;
                    suggestionsContainer.innerHTML = '';
                });
                suggestionsContainer.appendChild(div);
            });
            suggestionsContainer.style.display = 'block';
        } else {
            suggestionsContainer.style.display = 'none';
        }
    });

    searchInput.addEventListener('keydown', function(e) {
        const suggestions = suggestionsContainer.getElementsByTagName('div');
        if (e.key === 'ArrowDown') {
            currentFocus++;
            addActive(suggestions);
        } else if (e.key === 'ArrowUp') {
            currentFocus--;
            addActive(suggestions);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (currentFocus > -1 && suggestions.length) {
                suggestions[currentFocus].click();
            } else {
                document.getElementById('submit-btn').click(); // Simula um clique no botão "Chutar"
            }
        }
    });

    function addActive(suggestions) {
        if (!suggestions) return false;
        removeActive(suggestions);
        if (currentFocus >= suggestions.length) currentFocus = 0;
        if (currentFocus < 0) currentFocus = suggestions.length - 1;
        suggestions[currentFocus].classList.add('suggestion-active');
        suggestions[currentFocus].scrollIntoView({ block: "nearest" });
    }

    function removeActive(suggestions) {
        for (let i = 0; i < suggestions.length; i++) {
            suggestions[i].classList.remove('suggestion-active');
        }
    }

    // Verifica se o jogador digitado jogou com ambos os jogadores sorteados após "Chutar" ou "Enter"
    document.getElementById('submit-btn').addEventListener('click', function() {
        const player = searchInput.value;
        if (players.includes(player)) {
            checkPlayerMatch(player, commonPlayers);
            searchInput.value = ''; // Limpa o conteúdo da search bar
        } else {
            displayNoMatch();
            searchInput.value = ''; // Limpa o conteúdo da search bar
        }
    });

    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            const player = searchInput.value;
            if (currentFocus === -1) {
                if (players.includes(player)) {
                    checkPlayerMatch(player, commonPlayers); // Verifica se o jogador digitado jogou com ambos
                    searchInput.value = ''; // Limpa o conteúdo da search bar
                } else {
                    displayNoMatch();
                    searchInput.value = ''; // Limpa o conteúdo da search bar
                }
            }
        }
    });
}

// Função para verificar se o jogador digitado jogou com ambos os jogadores sorteados
function checkPlayerMatch(player, commonPlayers) {
    if (commonPlayers.includes(player)) {
        showTemporaryMessage("Parabéns! Você encontrou um jogador que jogou com ambos!");
        endGame(true, player, commonPlayers); // Chama a função para terminar o jogo
    } else {
        attempts.push(player);
        updateAttemptsDisplay(); // Atualiza a exibição das tentativas
        if (attempts.length >= maxAttempts) {
            showTemporaryMessage("Você usou todas as suas tentativas!");
            endGame(false, null, commonPlayers); // Chama a função para terminar o jogo
        } else {
            showTemporaryMessage("Este jogador não jogou com ambos. Tente novamente!");
        }
    }
}

// Função para exibir mensagem caso o jogador não conste nos dados
function displayNoMatch() {
    showTemporaryMessage("Este jogador não consta nos dados. Tente novamente!");
}

// Função para exibir a mensagem temporariamente
function showTemporaryMessage(message) {
    const resultContainer = document.getElementById('result');
    resultContainer.innerText = message;
    resultContainer.style.visibility = 'visible';
    setTimeout(() => {
        resultContainer.style.visibility = 'hidden';
    }, 3000); // Exibe a mensagem por 3 segundos
}

// Função para atualizar a exibição das tentativas
function updateAttemptsDisplay() {
    const attemptsContainer = document.getElementById('attempts-container');
    attemptsContainer.innerHTML = `
        <div>Seus chutes (${attempts.length}/${maxAttempts}):</div>
        ${attempts.map((attempt, index) => `<div>${index + 1}. ${attempt}</div>`).join('')}
    `;
}

// Função para terminar o jogo e exibir as respostas corretas
// Função para terminar o jogo e exibir as respostas corretas
function endGame(success, correctPlayer, commonPlayers) {
    const correctAnswersContainer = document.getElementById('correct-answers-container');
    correctAnswersContainer.innerHTML = ''; // Limpa o conteúdo anterior

    if (success) {
        correctAnswersContainer.innerHTML = `
            <div class="correct-answer">Você acertou: ${correctPlayer}</div>
            ${commonPlayers.filter(player => player !== correctPlayer).map(player => `<div class="other-answer">${player}</div>`).join('')}
        `;
    } else {
        correctAnswersContainer.innerHTML = `
            ${commonPlayers.map(player => `<div class="correct-answer">${player}</div>`).join('')}
        `;
    }

    correctAnswersContainer.style.visibility = 'visible';
}


// Função para inicializar o jogo
function initializeGame() {
    loadPlayersConnections('dicionarios/players_connections.json', function(playersConnections) {
        // Sorteia uma dupla de jogadores
        const [player1, player2, commonPlayers] = getRandomPair(playersConnections);

        // Atualiza a interface com as informações dos jogadores sorteados
        document.getElementById('player1-img').src = `transfermarkt/${player1}.jpg`;
        document.getElementById('player1-name').innerText = player1;
        document.getElementById('player2-img').src = `transfermarkt/${player2}.jpg`;
        document.getElementById('player2-name').innerText = player2;

        // Carrega o arquivo allplayers.json para a barra de pesquisa
        loadPlayersConnections('dicionarios/allplayers.json', function(allPlayers) {
            setupSearchBar(allPlayers, commonPlayers);
        });
    });
}

// Inicia o jogo ao carregar a página
window.onload = initializeGame;

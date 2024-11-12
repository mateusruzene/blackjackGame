import random

# Configuração do baralho
def create_deck():
    deck = []
    suits = ['♠', '♥', '♦', '♣']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    for suit in suits:
        for value in values:
            deck.append((value, suit))
    random.shuffle(deck)
    return deck

# Função para calcular o valor da mão
def calculate_hand_value(hand):
    value = 0
    aces = 0
    for card, _ in hand:
        if card in ['J', 'Q', 'K']:
            value += 10
        elif card == 'A':
            value += 11
            aces += 1
        else:
            value += int(card)
    
    while value > 21 and aces:
        value -= 10
        aces -= 1
    return value

# Função para exibir a mão
def display_hand(hand, player):
    hand_str = " ".join([f"{card}{suit}" for card, suit in hand])
    print(f"{player} mão: {hand_str} (valor: {calculate_hand_value(hand)})")

# Jogo principal
def play_blackjack_round(players, dealer_index):
    deck = create_deck()
    hands = {player: [] for player in players}
    
    dealer = players[dealer_index]
    print(f"\n--- Nova Rodada ---")
    print(f"{dealer} é o Dealer desta rodada!\n")
    
    # Distribuição inicial de cartas
    for _ in range(2):
        for player in players:
            hands[player].append(deck.pop())

    # Turno dos jogadores (incluindo o dealer)
    for player in players:
        while True:
            display_hand(hands[player], player)
            if calculate_hand_value(hands[player]) == 21:
                print(f"{player} tem Blackjack!")
                break
            elif calculate_hand_value(hands[player]) > 21:
                print(f"{player} estourou!")
                break

            action = input(f"{player}, deseja 'hit' (pedir carta) ou 'stand' (parar)? ").lower()
            if action == 'hit':
                hands[player].append(deck.pop())
            elif action == 'stand':
                break
            else:
                print("Ação inválida. Tente novamente.")

    # Exibir resultados
    dealer_value = calculate_hand_value(hands[dealer])
    print(f"\nResultados finais (Dealer: {dealer}):\n")
    for player in players:
        player_value = calculate_hand_value(hands[player])
        if player == dealer:
            print(f"{player} (Dealer): {dealer_value}")
        else:
            if player_value > 21:
                result = "perdeu (estourou)"
            elif dealer_value > 21 or player_value > dealer_value:
                result = "ganhou"
            elif player_value == dealer_value:
                result = "empatou com o dealer"
            else:
                result = "perdeu"
            print(f"{player} {result}.")

# Loop de rodadas com dealer rotativo
def play_blackjack():
    players = ["Jogador 1", "Jogador 2", "Jogador 3", "Jogador 4"]
    dealer_index = 0

    while True:
        play_blackjack_round(players, dealer_index)
        dealer_index = (dealer_index + 1) % 4  # Alterna o dealer para o próximo jogador

        next_round = input("\nDeseja jogar outra rodada? (s/n): ").lower()
        if next_round != 's':
            print("Encerrando o jogo.")
            break

# Iniciar o jogo
play_blackjack()

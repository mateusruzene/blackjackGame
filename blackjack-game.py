import random

# Configuração do baralho
def create_deck():
    suits = ['♠', '♥', '♦', '♣']
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    deck = [(value, suit) for value in values for suit in suits]
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

# Exibir a mão de forma formatada
def display_hand(hand, player, is_dealer=False, hide_card=False):
    if hide_card and is_dealer:
        print(f"{player} mão: {hand[0][0]}{hand[0][1]} [?]")
    else:
        hand_str = " ".join([f"{card}{suit}" for card, suit in hand])
        print(f"{player} mão: {hand_str} (valor: {calculate_hand_value(hand)})")

# Função principal da rodada
def play_blackjack_round(players, dealer_index, balances):
    deck = create_deck()
    hands = {player: [] for player in players}
    bets = {}

    dealer = players[dealer_index]
    print(f"\n--- Nova Rodada ---")
    print(f"{dealer} é o Dealer desta rodada!\n")

    # Realizar apostas
    for player in players:
        if player != dealer:
            while True:
                try:
                    bet = int(input(f"{player}, você tem {balances[player]} fichas. Quanto deseja apostar? "))
                    if 0 < bet <= balances[player]:
                        bets[player] = bet
                        balances[player] -= bet
                        break
                    print("Aposta inválida.")
                except ValueError:
                    print("Por favor, insira um valor válido.")

    # Distribuir cartas iniciais
    for _ in range(2):
        for player in players:
            hands[player].append(deck.pop())

    # Exibir cartas iniciais (Dealer esconde a segunda carta)
    for player in players:
        display_hand(hands[player], player, is_dealer=(player == dealer), hide_card=True)

    # Turno dos jogadores
    for player in players:
        if player == dealer:
            continue  # Dealer joga depois
        while True:
            display_hand(hands[player], player)
            if calculate_hand_value(hands[player]) == 21:
                print(f"{player} tem Blackjack!")
                break
            elif calculate_hand_value(hands[player]) > 21:
                print(f"{player} estourou!")
                break

            action = input(f"{player}, deseja 'hit' (pedir), 'stand' (parar), 'double' (dobrar aposta) ou 'split' (dividir)? ").lower()
            if action == 'hit':
                hands[player].append(deck.pop())
            elif action == 'stand':
                break
            elif action == 'double':
                if balances[player] >= bets[player]:
                    balances[player] -= bets[player]
                    bets[player] *= 2
                    hands[player].append(deck.pop())
                    break
                else:
                    print("Fichas insuficientes para dobrar a aposta.")
            elif action == 'split':
                # Implementação futura (se necessário)
                print("Funcionalidade de 'Split' ainda não implementada.")
            else:
                print("Ação inválida. Tente novamente.")

    # Turno do Dealer
    while calculate_hand_value(hands[dealer]) < 17 or \
            (calculate_hand_value(hands[dealer]) == 17 and any(card == 'A' for card, _ in hands[dealer])):
        hands[dealer].append(deck.pop())

    # Resultados finais
    print("\n--- Resultados Finais ---")
    for player in players:
        display_hand(hands[player], player)
    dealer_value = calculate_hand_value(hands[dealer])

    for player in players:
        if player == dealer:
            continue
        player_value = calculate_hand_value(hands[player])
        if player_value > 21:
            print(f"{player} perdeu a aposta de {bets[player]} (estourou).")
        elif dealer_value > 21 or player_value > dealer_value:
            winnings = bets[player] * (2 if player_value == 21 and len(hands[player]) == 2 else 1.5)
            balances[player] += winnings
            print(f"{player} ganhou {winnings:.0f} fichas!")
        elif player_value == dealer_value:
            balances[player] += bets[player]
            print(f"{player} empatou e recuperou sua aposta.")
        else:
            print(f"{player} perdeu a aposta de {bets[player]}.")

# Controlar rodadas
def play_blackjack():
    players = ["Jogador 1", "Jogador 2", "Jogador 3", "Jogador 4"]
    balances = {player: 100 for player in players}  # Cada jogador começa com 100 fichas
    dealer_index = 0

    while True:
        play_blackjack_round(players, dealer_index, balances)
        dealer_index = (dealer_index + 1) % 4

        if all(balances[player] == 0 for player in players if player != players[dealer_index]):
            print("Todos os jogadores estão sem fichas! Fim de jogo.")
            break

        next_round = input("\nDeseja jogar outra rodada? (s/n): ").lower()
        if next_round != 's':
            print("Encerrando o jogo.")
            break

# Iniciar o jogo
play_blackjack()

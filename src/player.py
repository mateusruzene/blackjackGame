class Player:
    def __init__(self, id):
        self.id = id
        self.hand = []
        self.bet = 0
        self.chips = 1000

    def receive_hand(self, hand):
        self.hand = hand

    def show_hand(self):
        return [str(card) for card in self.hand]
    
    def ask_bet(self):
        bet = int(input("Digite a aposta: "))
        if bet > self.chips or bet <= 0:
            print(f'Aposta inválida, aposte entre 1 e {self.chips}')
            return self.ask_bet()
        self.bet = bet
        return bet
    
    def find_card(self, suit, rank):
        for card in self.hand:
            if card.suit == suit and card.rank == rank:
                return card
        return None 
    
    def is_alive(self):
        return self.chips > 0
    
    def ask_play(self, deck):
        while True:
            # Calcula e exibe a soma da pontuação do jogador
            score = self.calculate_score()
            print(f"Sua mão: {self.show_hand()} | Pontuação: {score}")            
            # Verifica se o jogador ultrapassou 21 pontos
            if score > 21:
                print("Você ultrapassou 21!")
                return deck
            
            if score == 21:
                print("Você tem um blackjack!")
                return deck

            # Pergunta ao jogador se ele deseja continuar pedindo cartas ou parar
            choice = input("Deseja pedir mais uma carta? (s para sim, n para não): ").strip().lower()

            if choice == 's':
                if deck:
                    card = deck.pop()
                    self.hand.append(card)
                    print(f"Você puxou a carta: {card}.")
                else:
                    print("O deck está vazio!")
                continue
            elif choice == 'n':
                print(f"Você decidiu parar com {score} pontos.")
                return deck
            else:
                print("Escolha inválida. Digite 's' para sim ou 'n' para não.")
    
    def calculate_score(self) -> int:
        score = sum(card.value() for card in self.hand)
        # Ajustar o valor do Ás para 11, se não ultrapassar 21
        if any(card.rank == 'A' for card in self.hand) and score + 10 <= 21:
            score += 10
        return score
    
    def get_status(self, dealer_score: int) -> str:
        player_score = self.calculate_score()
        if player_score > 21:
            return "PERDEU"
        elif dealer_score > 21 or player_score > dealer_score:
            return "GANHOU"
        elif player_score == dealer_score:
            return "EMPATOU"
        return "PERDEU"
    
    def calculate_chips(self, score):
        if score == "GANHOU":
            self.chips = self.chips + (self.bet / 2)
            print(f"Você ganhou {self.bet / 2} fichas, sua aposta era: {self.bet} fichas, total: {self.chips} fichas")
        if score == "EMPATOU":
            self.chips = self.chips - (self.bet / 2)
            print(f"Você perdeu {self.bet / 2} fichas, sua aposta era: {self.bet} fichas, total: {self.chips} fichas")
        if score == "PERDEU":
            self.chips = self.chips - self.bet
            print(f"Você perdeu {self.bet} fichas, sua aposta era: {self.bet} fichas, total: {self.chips} fichas")            

    def __repr__(self):
        return f"player({self.name}, hand: {self.show_hand()})"

class Card:
    suits = ['♠', '♥', '♦', '♣']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f"{self.rank}{self.suit}"

    def __lt__(self, other):
        if self.ranks.index(self.rank) != self.ranks.index(other.rank):
            return self.ranks.index(self.rank) < self.ranks.index(other.rank)
        else:
            return self.suits.index(self.suit) < self.suits.index(other.suit)
        
    def value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 1  # Será ajustado para 11, se possível, no cálculo da pontuação.
        return int(self.rank)
        
    @classmethod
    def from_string(cls, card_str):
        suit = card_str[-1]
        rank = card_str[:-1]
        return cls(suit, rank)


import json
from .deck import Deck
from .card import Card
from .player import Player
from .network import setup_socket
from .utils import get_ports, read_config
import sys


NUM_OF_PLAYERS = 2
BASTAO = "BASTAO"

def upsert_bet(bets, player, bet):
    for i in range(len(bets)):
        if bets[i]["player"] == player:
            bets[i]["bet"] = bet
            return bets
    bets.append({"player": player, "bet": bet})
    return bets

def upsert_card(cards, player, card):
    for i in range(len(cards)):
        if cards[i]["player"] == player:
            cards[i]["card"] = card
            return cards
    cards.append({"player": player, "card": card, "wins": 0})
    return cards

def deal_cards(players):
    deck = Deck()
    deck.shuffle()
    hands = deck.draw_hands(NUM_OF_PLAYERS)
        
    for i in range(NUM_OF_PLAYERS):
        player = Player(i)
        player.hand = hands[i]
        players.append(player)
    
    return hands, deck
    
def main():    
    player_index = int(sys.argv[1])
    config = read_config()

    self_port, next_player_port, host, next_player_host = get_ports(config, player_index)
    if self_port is None or next_player_port is None:
        sys.exit(1)

    sock = setup_socket(self_port, host)
    
    my_player = Player(player_index)
    
    has_bastao = False
    if(int(my_player.id) == 0):
        has_bastao = True
        
    bets = []
    if has_bastao:
        print("Você é o dealer")
        print(f"Faça sua aposta, você tem: {my_player.chips} fichas")

        my_player.ask_bet()
        bets = upsert_bet(bets, my_player.id, my_player.bet)
        message = json.dumps({"state": "BETTING", "bets": bets})
        sock.sendto(message.encode(), (next_player_host, next_player_port))  
    
    while True:
        data, addr = sock.recvfrom(1024)
        pacote = json.loads(data.decode())

        if pacote["state"] == "BETTING":
            if "token" in pacote:
                if my_player.is_alive() == False:
                    sock.sendto(data, (next_player_host, next_player_port))
                    continue
                has_bastao = True
            
            if has_bastao == True:
                if "bets" in pacote:
                    local_players = []    
                    hands, deck = deal_cards(local_players)

                    my_player.receive_hand(hands[int(my_player.id)])
                    print(f"Minha mão: {my_player.show_hand()}")

                    message = json.dumps({"state": "PLAYING", "hands":[{"player": player.id, "hand": player.show_hand()} for player in local_players], "deck": deck.to_list()})
                    sock.sendto(message.encode(), (next_player_host, next_player_port))
                else:
                    local_bets = []
                    print(f"Faça sua aposta, você tem: {my_player.chips} fichas")
                    my_player.ask_bet()

                    local_bets = upsert_bet(local_bets, my_player.id, my_player.bet)

                    message = json.dumps({"state": "BETTING", "bets": local_bets})
                    sock.sendto(message.encode(), (next_player_host, next_player_port))
                continue
            if my_player.is_alive() == False:
                sock.sendto(data, (next_player_host, next_player_port))
                continue
            
            print(f"Faça sua aposta, você tem: {my_player.chips} fichas")

            my_player.ask_bet()
            bets = pacote["bets"]
            bets = upsert_bet(bets, my_player.id, my_player.bet)

            message = json.dumps({"state": "BETTING", "bets": bets})
            sock.sendto(message.encode(), (next_player_host, next_player_port))

        if pacote["state"] == "PLAYING":       
            if has_bastao == True:
                # TODO: Fazer a lógica das jogadas
                my_score = my_player.calculate_score(); #TODO: Melhorar o calculo do score de acordo com as cartas do jogador
                message = json.dumps({"state": "RESULTS", "dealer_score": my_score, "best_score": 0})
                sock.sendto(message.encode(), (next_player_host, next_player_port))                 
            
            if my_player.is_alive() == False:
                sock.sendto(data, (next_player_host, next_player_port))
                continue

            my_hand = next(player_info["hand"] for player_info in pacote["hands"] if player_info["player"] == int(my_player.id))
            my_hand = [Card.from_string(card_str) for card_str in my_hand]
            my_player.receive_hand(my_hand)
            my_player.ask_play(my_hand)

            deck = pacote["deck"]
            print(f"Minha mão: {my_player.show_hand()}")
            my_player.ask_play() #TODO: Fazer as perguntas de hit ou stand
            
            message = json.dumps({"state": "PLAYING", "hands": pacote["hands"], "deck": deck})
            sock.sendto(message, (next_player_host, next_player_port))

        # if pacote["state"] == "RESULTS":
        #     if has_bastao == True:
        #         best_score = int(pacote["best_score"]);
        #         my_status = my_player.get_status(best_score);
        #         #TODO: Calcular quantas fichas ele recebe/perde - se ganhar = aposta*x - se empatar = aposta - se perder = nada
        #         #TODO: Passar esses valores para o jodador e zerar a oposta dele (zerar apenas no fim do round)
        #         print(f"Você {my_status}! - Sua pontuação: {my_player.calculate_score()} - Maior pontuação da mesa: {best_score}")

        #         # TODO: Fazer a lógica dos end_round
        #         message = json.dumps({"state": "END_ROUND"})
        #         sock.sendto(message.encode(), (next_player_host, next_player_port))

        #     best_score = int(pacote["best_score"])
        #     dealer_score = int(pacote["dealer_score"])
        #     my_status = my_player.get_status(dealer_score);
        #     my_score = my_player.calculate_score() #TODO: Melhorar o calculo do score de acordo com as cartas do jogador
        #     biggest_score = my_score if my_score <= 21 and my_score > best_score else best_score
                
        #     #TODO: Calcular quantas fichas ele recebe/perde - se ganhar = aposta*x - se empatar = aposta - se perder = nada
        #     print(f"Você {my_status}! - Sua pontuação: {my_score} - Pontuação do Dealer: {dealer_score} - Maior pontuação da mesa: {best_score}")

        #     message = json.dumps({"state": "RESULTS", "dealer_score": dealer_score, "best_score": biggest_score})
        #     sock.sendto(message.encode(), (next_player_host, next_player_port))

        # if pacote["state"] == "END_ROUND":

            
        # if pacote["state"] == "PLAYING":
        #     if my_player.is_alive() == False:
        #         print("Você perdeu todas as vidas")
        #         sock.sendto(data, (next_player_host, next_player_port))
        #         continue

        #     cards_played = pacote["cards"]
            
        #     if len(cards_played) > 0:
        #         print(f"Cartas jogadas: {cards_played}")
                
        #     card_played = my_player.ask_play()
        #     print(f"Carta jogada: {card_played}")
            
        #     if has_bastao == True:                
        #         cards_played = upsert_card(cards_played, my_player.id, str(card_played))
                
        #         print("Agora é a hora de computar os resultados")
        #         all_cards = []
        #         for card_info in cards_played:
        #             player = card_info["player"]
        #             card = Card.from_string(card_info["card"])
        #             all_cards.append((player, card))
                                                    
        #         player_won, _ = max(all_cards, key=lambda x: x[1])
                
        #         #increment number of wins of the player that won the round
        #         for card_info in cards_played:
        #             if card_info["player"] == player_won:
        #                 card_info["wins"] += 1          
                
        #         if len(my_player.hand) == 0:
        #             message = json.dumps({"state": "END_OF_ROUND", "result": cards_played})
        #             sock.sendto(message.encode(), (next_player_host, next_player_port))
        #             continue
                
        #         message = json.dumps({"state": "RESULT", "result": cards_played, "last_win": player_won})
        #         sock.sendto(message.encode(), (next_player_host, next_player_port))
        #         continue
            
        #     cards_played = upsert_card(cards_played, my_player.id, str(card_played))
        #     message = json.dumps({"state": "PLAYING", "cards": cards_played})
        #     sock.sendto(message.encode(), (next_player_host, next_player_port))
            

        # if pacote["state"] == "RESULT":
        #     result = pacote["last_win"]
        #     print(f"Resultado da rodada: Jogador {result} ganhou")
        #     if has_bastao == True:
        #         print("Agora é a hora de começar a próxima rodada")
        #         cards_played = pacote["result"]
        #         message = json.dumps({"state": "PLAYING", "cards": cards_played})
        #         sock.sendto(message.encode(), (next_player_host, next_player_port))
        #         continue            
        #     sock.sendto(data, (next_player_host, next_player_port))
        
        # if pacote["state"] == "END_OF_ROUND":
        #     print("Resultado da rodada:")
        #     print(pacote["result"])
            
        #     if my_player.is_alive() == False:
        #         sock.sendto(data, (next_player_host, next_player_port))
        #         continue
            
        #     # subtract the number of lifes, it's the difference between the bets and the number of wins
        #     my_bet = my_player.bet
        #     my_wins = next(card_info["wins"] for card_info in pacote["result"] if card_info["player"] == my_player.id)
        #     my_player.lives -= abs(my_bet - my_wins)
        
        #     print(f"Minhas vidas: {my_player.lives}")
            
        #     #reset everything
        #     Card.reset_gato()
        #     my_player.bet = 0
        #     my_player.hand = []
                        
        #     if has_bastao == True:
        #         # começar novo jogo, passar o bastao pra frente
        #         print("Fim da rodada")
        #         has_bastao = False
                
        #         message = json.dumps({"state": "DEALING", "token": BASTAO})
        #         sock.sendto(message.encode(), (next_player_host, next_player_port))
        #         continue
        #     sock.sendto(data, (next_player_host, next_player_port))


if __name__ == "__main__":
    main()


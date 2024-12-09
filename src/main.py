import json
from .deck import Deck
from .card import Card
from .player import Player
from .utils import get_ports, read_config
import socket
import sys


NUM_OF_PLAYERS = 2
BASTAO = "BASTAO"

def setup_socket(self_port, host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    addr = (host, self_port)
    print(f"Binding to {addr}")
    sock.bind(addr)
    return sock

def set_bets(bets, player, bet):
    for i in range(len(bets)):
        if bets[i]["player"] == player:
            bets[i]["bet"] = bet
            return bets
    bets.append({"player": player, "bet": bet})
    return bets

def deal_cards(players):
    deck = Deck()
    deck.shuffle()
    hands, remaining = deck.draw_hands(NUM_OF_PLAYERS)
    for i in range(NUM_OF_PLAYERS):
        player = Player(i)
        player.hand = hands[i]
        players.append(player)
    
    return hands, remaining
    
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
        bets = set_bets(bets, my_player.id, my_player.bet)
        message = json.dumps({"state": "BETTING", "dealer_id": my_player.id, "bets": bets})
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
                    hands, remaining = deal_cards(local_players)

                    my_player.receive_hand(hands[int(my_player.id)])

                    message = json.dumps({"state": "PLAYING", "hands":[{"player": player.id, "hand": player.show_hand()} for player in local_players], "deck": remaining})
                    sock.sendto(message.encode(), (next_player_host, next_player_port))
                else:
                    local_bets = []
                    print("Você é o dealer")
                    print(f"Faça sua aposta, você tem: {my_player.chips} fichas")
                    my_player.ask_bet()

                    local_bets = set_bets(local_bets, my_player.id, my_player.bet)

                    message = json.dumps({"state": "BETTING", "dealer_id": my_player.id, "bets": local_bets})
                    sock.sendto(message.encode(), (next_player_host, next_player_port))
                continue
            else:
                if my_player.is_alive() == False:
                    sock.sendto(data, (next_player_host, next_player_port))
                    continue
                dealer_id = int(pacote["dealer_id"])
                print(f"O Dealer é o jogador {dealer_id + 1}")
                print(f"Faça sua aposta, você tem: {my_player.chips} fichas")
                my_player.ask_bet()
                bets = pacote["bets"]
                bets = set_bets(bets, my_player.id, my_player.bet)
                
                message = json.dumps({"state": "BETTING","dealer_id": dealer_id, "bets": bets})
                sock.sendto(message.encode(), (next_player_host, next_player_port))

        if pacote["state"] == "PLAYING":       
            if has_bastao == True:
                # TODO: Fazer a lógica das jogadas
                deck = pacote["deck"]
                deck = [Card.from_string(card_str) for card_str in deck]
                my_player.ask_play(deck)
                
                my_score = my_player.calculate_score(); #TODO: Melhorar o calculo do score de acordo com as cartas do jogador
                message = json.dumps({"state": "RESULTS", "dealer_score": my_score, "best_score": 0})
                sock.sendto(message.encode(), (next_player_host, next_player_port))                 
            else:
                if my_player.is_alive() == False:
                    sock.sendto(data, (next_player_host, next_player_port))
                    continue
                
                my_hand = next(player_info["hand"] for player_info in pacote["hands"] if player_info["player"] == int(my_player.id))
                my_hand = [Card.from_string(card_str) for card_str in my_hand]
                my_player.receive_hand(my_hand)

                deck = pacote["deck"]
                deck = [Card.from_string(card_str) for card_str in deck]
                remaining = my_player.ask_play(deck) #TODO: Fazer as perguntas de hit ou stand

                message = json.dumps({"state": "PLAYING", "hands": pacote["hands"], "deck": [str(card) for card in remaining]})
                sock.sendto(message.encode(), (next_player_host, next_player_port))

        if pacote["state"] == "RESULTS":
            if has_bastao == True:
                best_score = int(pacote["best_score"]);
                my_status = my_player.get_status(best_score);
                print(f"Você {my_status}! - Sua pontuação: {my_player.calculate_score()} - Maior pontuação da mesa: {best_score}")
                my_player.calculate_chips(my_status);
                
                players_alive = 1;
                if my_player.is_alive() == False:
                    players_alive = 0;
                    
                message = json.dumps({"state": "END_ROUND", "players_alive": players_alive})
                sock.sendto(message.encode(), (next_player_host, next_player_port))
            else:
                best_score = int(pacote["best_score"])
                dealer_score = int(pacote["dealer_score"])
                my_status = my_player.get_status(dealer_score);
                my_score = my_player.calculate_score() #TODO: Melhorar o calculo do score de acordo com as cartas do jogador
                biggest_score = my_score if my_score <= 21 and my_score > best_score else best_score

                print(f"Você {my_status}! - Sua pontuação: {my_score} - Pontuação do Dealer: {dealer_score}")
                my_player.calculate_chips(my_status);

                message = json.dumps({"state": "RESULTS", "dealer_score": dealer_score, "best_score": biggest_score})
                sock.sendto(message.encode(), (next_player_host, next_player_port))
        
        if pacote["state"] == "END_ROUND":
            print("Fim da rodada")
            if has_bastao == True:
                if int(pacote["players_alive"]) == 0:
                    print("Todos os jogadores morreram! Fim da partida.")
                    message = json.dumps({"state": "GAME_OVER"})
                    sock.sendto(message.encode(), (next_player_host, next_player_port))
                    return;
                has_bastao = False
                message = json.dumps({"state": "BETTING", "token": BASTAO})
                sock.sendto(message.encode(), (next_player_host, next_player_port))
            else:
                if my_player.is_alive() == False:
                    print("Você perdeu todas as fichas!")
                    sock.sendto(data, (next_player_host, next_player_port))
                    continue
                my_player.bet = 0
                my_player.hand = []
                sock.sendto(data, (next_player_host, next_player_port))

        if pacote["state"] == "GAME_OVER":
            print("Todos os jogadores morreram! Fim da partida.")
            sock.sendto(message.encode(), (next_player_host, next_player_port))
            return

if __name__ == "__main__":
    main()


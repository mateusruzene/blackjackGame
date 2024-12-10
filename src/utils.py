import sys
import os

# Recebe o arquivo de config para saber qual é a porta e o host atraves do index do usuário, retorna as portas e os hosts do usuário atual e o próximo
def get_ports(config, index):
    if index not in config:
        print(f"Index {index} not found in config")
        return None, None
    self_port, host = config[index] # Pega os parametros dentro do arquivo
    next_index = (index + 1) % len(config) # Verifica o próximo player, se for o último, pega o primeiro
    
    next_player_port, next_player_host = config[next_index]
    return self_port, next_player_port, host, next_player_host

# Lê o arquivo de configuração, separando por index, porta e host de cada usuário
def read_config():
    config = {}
    config_file_path = os.path.join(os.path.dirname(__file__), '..', 'players.txt')
    with open(config_file_path, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) != 3:
                continue
            index = int(parts[0])
            port = int(parts[1])
            host = parts[2]
            config[index] = (port, host)
    return config
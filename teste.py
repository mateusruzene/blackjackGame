import socket
import threading
import argparse

def iniciar_no(porta_local, porta_destino, tem_bastao=False):
    # Cria o socket UDP
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('localhost', porta_local))

    # Variáveis globais para controlar o bastão e mensagens
    bastao = tem_bastao
    id_no = porta_local  # Usaremos a porta local como identificador único para o nó

    # Função para receber mensagens
    def receber():
        nonlocal bastao
        while True:
            dados, addr = sock.recvfrom(1024)
            mensagem = dados.decode()

            # Se a mensagem é o bastão, habilita o envio
            if mensagem == "BASTAO":
                bastao = True
                print(f"[{porta_local}] Você recebeu o bastão. Agora pode enviar uma mensagem.")
            else:
                # Exibe a mensagem recebida e repassa adiante se não for do próprio nó
                print(f"[{porta_local}] Recebido de {addr}: {mensagem}")
                
                if not mensagem.endswith(f"_{id_no}"):  # Checa se o nó já é o remetente original
                    # Repassa a mensagem para o próximo nó
                    sock.sendto(mensagem.encode(), ('localhost', porta_destino))
                else:
                    # Mensagem retornou ao nó de origem; passa o bastão ao próximo nó
                    print(f"[{porta_local}] Mensagem retornou ao nó de origem. Passando o bastão.")
                    sock.sendto("BASTAO".encode(), ('localhost', porta_destino))

    # Função para enviar mensagens quando tiver o bastão
    def enviar():
        nonlocal bastao
        while True:
            if bastao:
                mensagem = input(f"[{porta_local}] Digite uma mensagem para enviar ao nó {porta_destino}: ")
                mensagem_com_id = f"{mensagem}_{id_no}"  # Adiciona ID do nó para rastrear o remetente original
                sock.sendto(mensagem_com_id.encode(), ('localhost', porta_destino))
                print(f"[{porta_local}] Enviado para localhost:{porta_destino}")
                bastao = False  # Passa o bastão após enviar a mensagem

    # Inicia as threads de envio e recebimento
    thread_receber = threading.Thread(target=receber)
    thread_receber.daemon = True
    thread_receber.start()

    thread_enviar = threading.Thread(target=enviar)
    thread_enviar.daemon = True
    thread_enviar.start()

    # Mantém o programa rodando
    thread_receber.join()
    thread_enviar.join()

if __name__ == "__main__":
    # Configuração dos argumentos de linha de comando
    parser = argparse.ArgumentParser(description="Configuração do nó na rede em anel com passagem de bastão.")
    parser.add_argument("porta_local", type=int, help="A porta que o nó usará para escutar.")
    parser.add_argument("porta_destino", type=int, help="A porta do próximo nó no anel para enviar mensagens.")
    parser.add_argument("--tem_bastao", action="store_true", help="Indica se o nó começa com o bastão.")
    
    args = parser.parse_args()

    # Inicia o nó com as portas passadas como argumento
    iniciar_no(args.porta_local, args.porta_destino, args.tem_bastao)

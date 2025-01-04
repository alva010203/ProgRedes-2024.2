import socket

DIRBASE = "files/"

# Configurações do servidor
host = "127.0.0.1"
port = 3456

# Criação do socket e conexão com o servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((host, port))
    print("Conectado ao servidor.")

    # Solicita o nome do arquivo
    arq = input('Digite o nome do arquivo: ')

    # Converte o nome do arquivo para bytes e envia o comprimento e o nome
    lenNameArq = len(arq.encode('utf-8')).to_bytes(2, 'big') #2 bytes do tamanho 
    msg = lenNameArq + arq.encode()  # Concatena o comprimento e o nome do arquivo
    sock.send(msg)  

    # Espera pela resposta do servidor
    fileIsOk = int.from_bytes(sock.recv(2), 'big')
    try:
        if fileIsOk == 0:
            tam = int.from_bytes(sock.recv(4), 'big') #recebe 4 bytes do tamanho do arq e converte para inteiro
            fd = open(DIRBASE+arq, 'wb')
            while tam > 0: 
                recBytes = sock.recv(4096)
                fd.write(recBytes)
                tam -= len(recBytes) #atualiza o tamanho S
            fd.close()
            print("Arquivo recebido com sucesso! ")
        else:
            print('Arquivo inacessível')

    except FileNotFoundError as e:
        print(f"Erro ao criar o arquivo: {e}")
    except PermissionError as e:
        print(f"Erro de permissão: {e}")

except socket.error as e:
    print(f'Erro de conexão: {e}')
finally:
    sock.close()
    print("Conexão encerrada.")
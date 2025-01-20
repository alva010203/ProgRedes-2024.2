import socket

DIRBASE = "files/"

# Configurações do servidor
host = "127.0.0.1"
port = 3456

# Criação do socket UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

try:
    # Solicita o nome do arquivo
    arq = input('Digite o nome do arquivo: ')

    # Converte o nome do arquivo para bytes e envia para o servidor
    msg = arq.encode('utf-8')
    sock.sendto(msg, (host, port))

    # Recebe a resposta do servidor
    data, addr = sock.recvfrom(1024)
    fileIsOk = int.from_bytes(data[:2], 'big')

    if fileIsOk == 0:
        # Recebe o tamanho do arquivo
        tam = int.from_bytes(data[2:6], 'big')
        fd = open(DIRBASE + arq, 'wb')

        while tam > 0:
            data, addr = sock.recvfrom(4096)
            fd.write(data)
            tam -= len(data)
        fd.close()
        print("Arquivo recebido com sucesso!")
    else:
        print('Arquivo inacessível')

except KeyboardInterrupt:
    print("O cliente interrompeu a ação")
except socket.error as e:
    print(f'Erro de conexão: {e}')
finally:
    sock.close()
    print("Conexão encerrada.")

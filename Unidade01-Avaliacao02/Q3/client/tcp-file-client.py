import socket, os

def menu():
    print("1- Solicitar lista de arquivos")
    print("2- Fazer download de um arquivo")
    print("3- Calcular hash SHA1 de um arquivo até uma posição")
    print("0- Sair\n")
    return int(input("Escolha uma opção: "))

def calcular_hash():
    try:
        sock.send((3).to_bytes(2, 'big'))  # Solicita o cálculo do hash

        # Solicita o nome do arquivo e a posição
        arq = input('Digite o nome do arquivo: ')
        posicao = int(input('Digite a posição até onde calcular o hash: '))

        # Converte o nome do arquivo e a posição para bytes e envia
        lenNameArq = len(arq.encode('utf-8')).to_bytes(2, 'big')
        msg = lenNameArq + arq.encode() + posicao.to_bytes(4, 'big')  # Concatena o nome do arquivo e a posição
        sock.send(msg)

        # Recebe a resposta do hash calculado
        hash_recebido = sock.recv(1024).decode('utf-8')
        print(f"Hash SHA1 até a posição especificada: {hash_recebido}")
    
    except Exception as e:
        print(f"Erro ao calcular o hash: {e}")

def Download():
    try:
        sock.send((2).to_bytes(2,'big'))
        # Solicita o nome do arquivo
        arq = input('Digite o nome do arquivo: ')
        
        # Converte o nome do arquivo para bytes e envia o comprimento e o nome
        lenNameArq = len(arq.encode('utf-8')).to_bytes(2, 'big') #2 bytes do tamanho 
        msg = lenNameArq + arq.encode()  # Concatena o com  primento e o nome do arquivo
        sock.send(msg)  
        
        pasta_valida = int.from_bytes(sock.recv(2), 'big')
        if pasta_valida == 3:
            print("Acesso negado, você não pode acessar arquivos fora da pasta files.")
            return
        # Espera pela resposta do servidor
        fileIsOk = int.from_bytes(sock.recv(2), 'big')

        if fileIsOk == 0:
            tam = int.from_bytes(sock.recv(4), 'big') #recebe 4 bytes do tamanho do arq e converte para inteiro
            print(f"O número de arquivos encotrado é: {tam}")
            #tratamento para caso o arquivo já exista no cliente
            for c in range(tam):
                tamanho_nome = sock.recv(2)
                tamanho_nome=  int.from_bytes(tamanho_nome, 'big')
                fileName = sock.recv(tamanho_nome).decode('utf-8')

                bytes_arq = int.from_bytes(sock.recv(4),'big') #tamanho em bytes do arquivo
                print(f"arquivo: {fileName}")

                if os.path.exists(DIRBASE + fileName): 
                    resposta = input(f"Arquivo {fileName} já existe Deseja subistituir? [S/N] ").lower()

                    while resposta != 's' and resposta != 'n':
                        print("Resposta inválida tente novamente usando 's' ou 'n'. ")
                        resposta = input("Deseja subistituir? [S/N] ").lower()
                    if resposta == 's':
                        None
                    elif resposta == 'n':
                        print("Download cancelado ")
                        return
                        
                with open(DIRBASE + fileName, 'wb') as fd:
                    recebido = 0
                    while recebido < bytes_arq: 
                        recBytes = sock.recv(min(4096, bytes_arq - recebido)) #pega o tamanho exato caso o resto seja menor de 4k
                        fd.write(recBytes)
                        recebido += len(recBytes)
                print("Arquivo recebido com sucesso! ")

        else:
            print('Arquivo inacessível')

    except FileNotFoundError as e:
        print(f"Erro ao criar o arquivo: {e}")
    except PermissionError as e:
        print(f"Erro de permissão: {e}")
    except BrokenPipeError as e:
        print(f"Erro: {e}")

def listagem():
    sock.send((1).to_bytes(2,'big')) #envia um codigo para solicitar a listagem
    print('Solicitando a listagem de arquivos...\n')
    tamanho = int.from_bytes(sock.recv(4), 'big')
    dados = b''

    while len(dados) < tamanho:
        dados += sock.recv(4096)
    
    print("Arquivos disponíveis:")
    print(dados.decode('utf-8'))

DIRBASE = "files/"

# Configurações do servidor
host = "127.0.0.1"
port = 3456

# Criação do socket e conexão com o servidor
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.connect((host, port))
    print("Conectado ao servidor.\n")
    opcao = menu()

    if opcao == 1:
        listagem()
    elif opcao == 2:
        Download()
    elif opcao == 3:
        calcular_hash()  
    elif opcao == 0:
        None
    else:
        print("Opção inválida")
except ValueError:
    print("valor informado não corresponde a numeros de escolha")
except KeyboardInterrupt:
    print('O usuario finalizou a ação')
except socket.error as e:
    print(f'Erro de conexão: {e}')

finally:
    sock.close()  # Fecha o socket se ele estiver aberto
    print("Conexão encerrada.")

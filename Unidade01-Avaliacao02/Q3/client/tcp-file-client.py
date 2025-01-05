import socket,os

def menu():
    print("1- Socilitar lista de arquivos")
    print("2- Fazer download de um arquivo")
    print("0- Sair\n")
    return int(input("Escolha  uma opção: "))

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

                bytes_arq = int.from_bytes(sock.recv(4),'big')
                print(f"tamanho bytes e: {bytes_arq}")
                print(f"arquivo bilu: {fileName}")

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
    elif opcao == 0:
        None
    else:
        print("Opção inválida")

except socket.error as e:
    print(f'Erro de conexão: {e}')

finally:
    sock.close()  # Fecha o socket se ele estiver aberto
    print("Conexão encerrada.")

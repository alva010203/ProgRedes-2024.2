import socket, os, glob

DIRBASE = "files/"
INTERFACE = ""  # escutará em todas as interfaces disponíveis
PORT = 3456

myTCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

caminho_dir = os.path.realpath(DIRBASE) #caminho iteiro ate files
def pasta_valida(pasta_solicitada):
    solicitacao = os.path.join(caminho_dir, pasta_solicitada) 
    caminho_usuario = os.path.realpath(solicitacao) #caminho inteiro solicitado pelo usuario

    comparação = os.path.commonpath([caminho_dir, caminho_usuario]) #retorna o maior caminho comum entre os diretorios
    return comparação

try:
    myTCPsock.bind((INTERFACE, PORT))
    myTCPsock.listen(1)  # permite apenas uma conexão
    print("Escutando em ...", (INTERFACE, PORT))

    while True:
        # Recebe a conexão
        con, cliente = myTCPsock.accept()
        print('Conectado por: ', cliente)

        comando = con.recv(2)
        comando = int.from_bytes(comando, 'big')

        if comando == 1:  # Pedido para listar arquivos
            print('Listando arquivos')

            lista_arquivos = os.listdir(DIRBASE)
            lista_arquivos = [f"{arq} ({os.path.getsize(DIRBASE + arq)} bytes)" for arq in lista_arquivos]

            lista_junta = '\n'.join(lista_arquivos).encode('utf-8')
            con.send(len(lista_junta).to_bytes(4, 'big'))
            con.send(lista_junta)

        elif comando == 2:  # Pedido de download de arquivos
            mensagem = con.recv(2)  # recebe 2 bytes do tamanho
            mensagem = int.from_bytes(mensagem, 'big')  # converte para inteiro
            
            fileName = con.recv(mensagem).decode('utf-8') #proximos bytes que contem o nome do arquivo
            print ("Recebi pedido para o arquivo ", fileName)

            pasta_valida(fileName)
            if pasta_valida(fileName) == caminho_dir:
                con.send(b'\x00\x02')
            else:
                con.send(b'\x00\x03')

            # Glob
            files = glob.glob(DIRBASE + fileName)
            print(f"Arquivos encontrados: {files}")

            if files:
                # Envia lista de arquivos encontrados
                con.send(b'\x00\x00')  # Sucesso
                con.send(len(files).to_bytes(4, 'big'))  # Envia o número de arquivos encontrados

                # Envia os nomes dos arquivos para o cliente
                for file in files:
                    file_name = os.path.basename(file) #filtra apenas o nome do arquivo
                    len_a = len(file_name.encode('utf-8')).to_bytes(2, 'big')
                    msg = len_a + file_name.encode() #concatena o tamanho e o nome
                    con.send(msg)
                    
                    print(f"nome sdoasdlka: {DIRBASE + file_name}")
                    
                    file_size = os.path.getsize(DIRBASE + file_name) #tamanho em bytes
                    con.send(file_size.to_bytes(4, 'big'))  # Envia o tamanho do arquivo
                    print(f"tamanho no server é : {file_size}")

                    with open(file, 'rb') as f:
                        print(f"Enviando arquivo {file}")
                        file_data = f.read(4096)
                        while file_data != b'':
                            con.send(file_data)
                            file_data = f.read(4096)
                            
            else:
                print("Nenhum arquivo encontrado com a máscara fornecida.")
                con.send(b'\x00\x01')  # Nenhum arquivo encontrado

            con.close()

except OSError:
    print("Erro: Endereço em uso.")
except Exception as e:
    print(f"Ocorreu um Erro: {e}")

finally:
    myTCPsock.close()  # Fecha o socket

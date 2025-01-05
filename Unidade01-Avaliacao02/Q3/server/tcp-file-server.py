import socket, os, glob, hashlib

DIRBASE = "files/"
INTERFACE = ""  # escutará em todas as interfaces disponíveis
PORT = 3456

myTCPsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

caminho_dir = os.path.realpath(DIRBASE)  # Caminho inteiro até "files"

def pasta_valida(pasta_solicitada):
    solicitacao = os.path.join(caminho_dir, pasta_solicitada)
    caminho_usuario = os.path.realpath(solicitacao)  # Caminho inteiro solicitado pelo usuário

    comparação = os.path.commonpath([caminho_dir, caminho_usuario])  # Retorna o maior caminho comum entre os diretórios
    return comparação

def calcular_sha1_ate_posicao(caminho_arquivo, posicao):
    # Função que calcula o hash SHA1 até a posição especificada
    sha1 = hashlib.sha1()
    try:
        with open(caminho_arquivo, 'rb') as f:
            dados = f.read(posicao)  # Lê o arquivo até a posição especificada
            sha1.update(dados)  # Atualiza o hash com os dados lidos
        return sha1.hexdigest()
    except FileNotFoundError:
        return None  # Arquivo não encontrado

try:
    myTCPsock.bind((INTERFACE, PORT))
    myTCPsock.listen(1)  # Permite apenas uma conexão
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
            mensagem = con.recv(2)  # Recebe 2 bytes do tamanho
            mensagem = int.from_bytes(mensagem, 'big')  # Converte para inteiro
            
            fileName = con.recv(mensagem).decode('utf-8')  # Próximos bytes que contêm o nome do arquivo
            print("Recebi pedido para o arquivo ", fileName)

            pasta_valida(fileName)
            if pasta_valida(fileName) == caminho_dir: # se for verdadeiro está na pasta files
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
                    file_name = os.path.basename(file)  # Filtra apenas o nome do arquivo
                    len_a = len(file_name.encode('utf-8')).to_bytes(2, 'big')
                    msg = len_a + file_name.encode()  # Concatena o tamanho e o nome
                    con.send(msg)
                    
                    print(f"nome do arquivo: {DIRBASE + file_name}")
                    
                    file_size = os.path.getsize(DIRBASE + file_name)  # Tamanho em bytes
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

        elif comando == 3:  # Pedido de calcular o hash SHA1 (posição específica)
            
            # Recebe o nome do arquivo e a posição
            mensagem = con.recv(2)
            mensagem = int.from_bytes(mensagem, 'big')

            fileName = con.recv(mensagem).decode('utf-8')  # Recebe o nome do arquivo
            posicao = int.from_bytes(con.recv(4), 'big')  # Recebe a posição até onde calcular o hash

            print(f"Calculando hash SHA1 do arquivo {fileName} até a posição {posicao}...")

            caminho_arquivo = os.path.join(DIRBASE, fileName)
            hash_resultado = calcular_sha1_ate_posicao(caminho_arquivo, posicao)

            if hash_resultado:
                con.send(hash_resultado.encode('utf-8'))  # Envia o hash para o cliente
                print(f"Hash SHA1 até a posição {posicao}: {hash_resultado}")
            else:
                con.send("Arquivo não encontrado.")  # Envia erro se o arquivo não for encontrado

            con.close()        

except OSError:
    print("Erro: Endereço em uso.")
except Exception as e:
    print(f"Ocorreu um Erro: {e}")

finally:
    myTCPsock.close()  # Fecha o socket

import socket, os

DIRBASE = "files/" 
INTERFACE = "" #escutará em todas as interfaces disponiveis 
PORT = 3456

myTCPsock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

try:
    myTCPsock.bind((INTERFACE, PORT))
    myTCPsock.listen(1) #permite apenas uma conexão
    print ("Escutando em ...", (INTERFACE, PORT))

    while True:
        # Recebe o nome do arquivo a servir
        con, cliente = myTCPsock.accept()
        print('Conectado por: ', cliente)

        comando = con.recv(2)
        comando = int.from_bytes(comando, 'big')

        if comando == 2:        
            mensagem = con.recv(2) #recebe 2 bytes do tamanho 
            mensagem =  int.from_bytes(mensagem, 'big') #converte para inteiro
            

            # Abre o arquivo a servir ao cliente
            fileName = con.recv(mensagem).decode('utf-8') #proximos bytes que contem o nome do arquivo
            print ("Recebi pedido para o arquivo ", fileName)

            fileName = DIRBASE+fileName
            print(f"Caminho completo do arquivo: {fileName}")

            if os.path.exists(fileName): #se encontrar o arquivo
                con.send(b'\x00\x00')
                fileSize = os.path.getsize(fileName) #pega o tamanho do arquivo em bytes
               
                con.send(fileSize.to_bytes(4, 'big')) #envia em 4 bytes em big endian

                fd = open (fileName, 'rb')
                print ("Enviando arquivo ", fileName)

                # Lê o conteúdo do arquivo a enviar ao cliente
                fileData = fd.read(4096) #4kb
                while fileData != b'':
                    con.send(fileData)
                    fileData = fd.read(4096)
                # Fecha o arquivo
                fd.close()
            else:
                print('1 ENVIADO')
                con.send(b'\x00\x01') #caso o arquivo não exista
            con.close()

        elif comando == 1:
            print('Listando arquivos')

            lista_arquivos = os.listdir(DIRBASE) 
            #nome e tamanho de cada arquivo separado por elementos em uma lista
            lista_arquivos =[f"{arq} ({os.path.getsize((DIRBASE + arq))} bytes)" for arq in lista_arquivos] 

            #lista serealizada(convertido em uma sequencia de bytes) 
            lista_junta = '\n'.join(lista_arquivos).encode('utf-8') 
            con.send(len(lista_junta).to_bytes(4, 'big')) 
            con.send(lista_junta) 

except OSError:
    print("Erro: Endereço em uso.")
except Exception as e:
    print(f"Ocorreu um Erro: {e}")

finally:
    myTCPsock.close() #fecha o socket
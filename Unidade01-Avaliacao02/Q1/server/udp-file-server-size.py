import socket, os

DIRBASE = "files/" 
INTERFACE = "" #escutará em todas as interfaces disponiveis 
PORT = 3456

myTCPsock = socket.socket (socket.AF_INET, socket.SOCK_STREAM)

myTCPsock.bind((INTERFACE, PORT))
myTCPsock.listen(1) #permite apenas uma conexão
print ("Escutando em ...", (INTERFACE, PORT))

while True:
    # Recebe o nome do arquivo a servir
    con, cliente = myTCPsock.accept()
    print('Conectado por: ', cliente)

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
        con.send(b'\x00\x01') #caso o arquivo não exista
    con.close()
myTCPsock.close() #fecha o socket
import socket, os

DIRBASE = "files/"
INTERFACE = ""  # Escutará em todas as interfaces disponíveis
PORT = 3456

myUDPsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
myUDPsock.bind((INTERFACE, PORT))
print("Escutando em ...", (INTERFACE, PORT))

while True:
    # Recebe o nome do arquivo a servir
    data, addr = myUDPsock.recvfrom(1024)
    fileName = data.decode('utf-8')
    print(f"Recebi pedido para o arquivo {fileName} de {addr}")

    fileName = DIRBASE + fileName
    print(f"Caminho completo do arquivo: {fileName}")

    if os.path.exists(fileName): #se encontrar o arquivo
        myUDPsock.sendto(b'\x00\x00', addr)
        fileSize = os.path.getsize(fileName) #pega o tamanho do arquivo em bytes
        myUDPsock.sendto(fileSize.to_bytes(4, 'big'), addr) #envia em 4 bytes em big endian

        fd = open (fileName, 'rb')
        print ("Enviando arquivo ", fileName)

        # Lê o conteúdo do arquivo a enviar ao cliente
        
        fileData = fd.read(4096) #4kb
        while fileData != b'':
            myUDPsock.sendto(fileData, addr)
            fileData = fd.read(4096)
        # Fecha o arquivo
        fd.close()
    else:
        myUDPsock.sendto(b'\x00\x01', addr) #caso o arquivo não exista

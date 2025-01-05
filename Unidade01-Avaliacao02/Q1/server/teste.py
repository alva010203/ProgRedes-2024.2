import os,socket
import os

caminho_do_arquivo = "Q1/server/files/palavra.txt"

if os.path.exists(caminho_do_arquivo):
    print("O arquivo existe!")
else:
    print("O arquivo NAO existe.")

import socket

HOST = 'localhost'
CLIENT_PORT = 8082
RM_PORT = 8083


def frontend(host='localhost', port=8082):
    sock_client = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
    sock_rm = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)

    sock_client.bind((HOST, CLIENT_PORT))
    sock_client.listen()
    print ("Escutando cliente")

    while True:
        print ("Esperando cliente...")
        sock_client.accept()

        sock_rm.connect((HOST, RM_PORT))
        print ("Conectando ao Gerenciador de Réplica Primário")


frontend()

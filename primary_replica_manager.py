import socket

HOST = 'localhost'
FRONTEND_PORT = 8083
SECUNDARY_RM_PORT = 8084


def primaryReplicaManager():
    sock_frontend = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
    sock_rms = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)

    sock_frontend.bind((HOST, FRONTEND_PORT))
    sock_frontend.listen()
    print ("Escutando frontend")

    while True:
        print ("Esperando frontend...")
        sock_frontend.accept()
        print("Conexão recebida")

        sock_rms.connect((HOST, SECUNDARY_RM_PORT))
        print ("Conectando aos Gerenciadores de Réplica Secundários")


primaryReplicaManager()

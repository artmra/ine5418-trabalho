import socket


def secundaryReplicaManager(host='localhost', port=8084):
    sock = socket.socket(socket.AF_INET,  socket.SOCK_STREAM)
    server_address = (host, port)
    sock.bind(server_address)
    sock.listen()
    print("Escutando RM Primário")

    while True:
        print ("Esperando RM Primário...")
        sock.accept()
        print("Conexão recebida")


secundaryReplicaManager()

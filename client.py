import socket


def client(host='localhost', port=8082):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (host, port)
    sock.connect(server_address)


client()

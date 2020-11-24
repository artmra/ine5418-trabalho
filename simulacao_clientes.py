from flask import Flask, request, views
import requests
import threading
import time
import os
import random
from datetime import datetime


# Realiza 10 requests com mensagens aleatórias para algum dos dois frontends
def dispatch_request():
    # É possivel mudar o numero de requisições aqui
    for i in range(0,2):
        file = open('lista.txt', 'r')
        product = random_line(file).rstrip()
        file.close()
        value = str(random.randint(1, 100)) + ' unidades de ' + product # Mensagem aleatória que será enviada para o frontend
        data = {'value': value,
                'pid': str(threading.get_ident())}
        print('Enviando a mensagem \'' + value + '\' para ser salva')
        result = requests.post('http://127.0.0.1:808'+str(random.randint(1, 2))+'/save', params= data)

        if result.content.decode() == 'ok':
            print('Mensagem salva no arquivo. Dê uma olhada!')
            time.sleep(5)

# Apenas obtem uma linha aleatoria do arquivo usado como base para gerar valores para serem mandados nos requests
def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile, 2):
      if random.randrange(num): continue
      line = aline
    return line

if __name__ == '__main__':
    app = Flask('client')

    # Instancia 3 threads, que executam o numero de requests definidos no método dispatch_request. Quantidade de threads
    # criadas pode ser alterado aqui
    for i in range(0,3):
        t = threading.Thread(target=dispatch_request)
        t.start()



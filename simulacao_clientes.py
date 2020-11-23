from flask import Flask, request, views
import requests
import threading
import time
import os
import random
from datetime import datetime

def dispatch_request():
    for i in range(0,25):
        file = open('lista.txt', 'r')
        product = random_line(file).rstrip()
        file.close()
        value = str(random.randint(1, 100)) + ' unidades de ' + product
        data = {'value': value,
                'tid': str(threading.get_ident())}
        print('Enviando requisição...')
        result = requests.post('http://127.0.0.1:8081/save', params= data)

        if result.content.decode() == 'ok':
            print('Finalizado!')

def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile, 2):
      if random.randrange(num): continue
      line = aline
    return line

if __name__ == '__main__':
    app = Flask('client')

    for i in range(0,3):
        t = threading.Thread(target=dispatch_request)
        t.start()



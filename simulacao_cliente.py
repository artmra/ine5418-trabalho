from flask import Flask, request, views
import requests
import threading
import time
import os
from datetime import datetime

def dispatch_request():
    for i in range(0,9):
        data = {'value': datetime.now().strftime("%H:%M:%S") + ' - ' + str(threading.get_ident())}
        print('Enviando requisição...')
        result = requests.post('http://127.0.0.1:5000/save', params= data)

        if result.content.decode() == 'ok':
            print('Finalizado!')

if __name__ == '__main__':
    app = Flask('client')

    for i in range(0,3):
        t = threading.Thread(target=dispatch_request)
        t.start()



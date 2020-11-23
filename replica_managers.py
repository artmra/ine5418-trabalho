from flask import Flask, request, views
import requests
import threading
import time
import os
import datetime

class Manager(views.View):
    methods = ['POST']

    def __init__(self, name, nextManagers=[]):
        self.name = name
        self.nextManagers = nextManagers

    def dispatch_request(self):
        if request.method == 'POST':
            value = request.args.get('value')
            self.saveValue(value)
            for i in self.nextManagers:
                data = {'value': value}
                result = requests.post(i, params= data)
                if result.content.decode() != 'ok':
                    return 'error'
            return 'ok'

    def saveValue(self, value):
        with open('files/{file}.txt'.format(file=self.name), 'a') as file:
            file.write(value + '\n')

if __name__ == '__main__':
    #CRIA PASTA FILES
    if not os.path.exists('./files'):
        os.makedirs('./files')
    #LIGA 3 SECONDARY MANAGERS E O PRIMARY NAS PORTAS 5000 PARA O PRIMARIO, 5001, 5002, 5003 PARA OS SECUNDARIOS
    qnt_secondarys = 3
    base = 5000
    secondarys = []
    for i in range(qnt_secondarys):
        app = Flask('secondary' + str(i + 1))
        app.add_url_rule('/save', view_func=Manager.as_view('myview', 'secondary' + str(i + 1)))
        secondarys.append(base + i + 1)
        threading.Thread(target=app.run, kwargs={'port': (base + i + 1)}).start()
    
    app = Flask('primary')
    app.add_url_rule('/save', view_func=Manager.as_view('myview', 'primary', list(map(lambda x: 'http://127.0.0.1:{port}/save'.format(port= x), secondarys))))
    app.run(port=base)
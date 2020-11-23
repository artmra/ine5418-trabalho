from flask import Flask, request, views
import requests
import threading
import time
import os
import datetime
import hashlib
import json

PM_ADDRESS = 'http://localhost:5000/save'

# Endpoint do front end
class FrontEnd(views.View):
    methods = ['POST']

    def __init__(self, name):
        self.name = name

    # Recebe uma requisição de atualização do arquivo e redireciona para o RM primário
    def dispatch_request(self):
        date = datetime.datetime.now().strftime("%d/%m/%Y - %H:%M:%S.%f")
        if request.method == 'POST':
            value = request.args.get('value')
            tid = request.args.get('pid')
            uid = hashlib.sha256((str(tid)+date+value).encode()).hexdigest()
            params = {"inputs": [
                                    {"value": value, # valor a ser adicionado no arquivo
                                     "date": date, # momento em que a requisição chegou no front end
                                     "pid": tid, # id da thread que realizou essa requisição
                                     "uid": uid}, # id unico gerado com base nos três outros atributos
                                ]
                    }
            result = requests.post(PM_ADDRESS, json=json.dumps(params))
            if result.content.decode() != 'ok':
                return 'error'
        return 'ok'

# Endpoint do Replica Manager
class Manager(views.View):
    methods = ['POST']
    backupListLock = threading.Lock()
    count = {} # Dicionario com os contadores de cada processo
    inputsToBackup = [] # Lista de inputs que devem ser adicionados nos arquivos de backup

    def __init__(self, name, nextManagers=[]):
        self.lock = threading.Lock()
        self.name = name
        self.nextManagers = nextManagers # Lista de RM secundários; Para RM's secundários essa lista é vazia.

    # Executa a atualização do arquivo
    def dispatch_request(self):
        if request.method == 'POST':
            inputs = json.loads(request.json)['inputs']
            self.saveValue(inputs)

            # Checar se o processo pode adicionar algo a lista de atualizações que devem ser feitas
            if len(self.nextManagers) > 0 :
                Manager.backupListLock.acquire()
                try:
                    Manager.inputsToBackup.append(inputs[0]) # input é adicionado a lista interna para futura atualização
                finally:
                    Manager.backupListLock.release()
            
            # Checar tamanho da lista, para decidir se os backups devem ou não ser atualizados
            Manager.backupListLock.acquire()
            try:
                if len(Manager.inputsToBackup) > 5:
                    data = {'inputs': Manager.inputsToBackup}
                    for i in self.nextManagers:
                        result = requests.post(i, json=json.dumps(data))
                        # Conforme dito pela professora, não é necessário tratar com os cenários em que a atualização dos backups dá errado
                        if result.content.decode() != 'ok':
                            print("Falha ao atualizar arquivo de backup do PM hospedado em " + i)
                    Manager.inputsToBackup.clear()
            finally:
                Manager.backupListLock.release()
            return 'ok'

    # Salva o valor no arquivo
    def saveValue(self, inputs):
        self.lock.acquire()
        try:
            with open('files/{file}.txt'.format(file=self.name), 'a') as file:
                for i in inputs:
                    file.write('uid: ' + str(i['uid']) + '; ' + 'pid: ' + str(i['pid']) + '; ' + i['date'] + ' :- ' + i['value'] + '\n')
        finally:
            self.lock.release()

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
    
    base = 8080
    for i in range(2):
        app = Flask('frontend' + str(i + 1))
        app.add_url_rule('/save', view_func=FrontEnd.as_view('myview', 'frontend' + str(i + 1)))
        threading.Thread(target=app.run, kwargs={'port': (base + i + 1)}).start()

    app = Flask('primary')
    app.add_url_rule('/save', view_func=Manager.as_view('myview', 'primary', list(map(lambda x: 'http://127.0.0.1:{port}/save'.format(port= x), secondarys))))
    app.run(port=5000)
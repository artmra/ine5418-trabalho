from flask import Flask, request, views
import requests
import threading
import time
import os
import datetime
import hashlib
import json

PM_ADDRESS = 'http://localhost:5000/save' # Apenas o endereço base do PM
FILE_LOCKS = {} # Dicionário que relaciona os arquivos aos seus locks

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
        self.name = name
        self.nextManagers = nextManagers # Lista de RM secundários; Para RM's secundários essa lista é vazia.

    # Executa a atualização do arquivo
    def dispatch_request(self):
        if request.method == 'POST':
            inputs = json.loads(request.json)['inputs']

            self.saveValue(inputs)
            # Checar se o processo pode adicionar algo a lista de atualizações que devem ser feitas
            if len(self.nextManagers) > 0:
                Manager.backupListLock.acquire()
                try:
                    Manager.inputsToBackup.append(inputs[0]) # input é adicionado a lista interna para futura atualização
                    # Checar tamanho da lista, para decidir se os backups devem ou não ser atualizados
                    if len(Manager.inputsToBackup) > 5: 
                        # Atualiza cada backup de maneira sequencial
                        for i in self.nextManagers:
                            data = {'inputs': Manager.inputsToBackup}
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
        FILE_LOCKS.get(self.name).acquire()
        try:
            with open('files/{file}.txt'.format(file=self.name), 'a') as file:
                for i in inputs:
                    file.write('uid: ' + str(i['uid']) + '; ' + 'pid: ' + str(i['pid']) + '; ' + i['date'] + ' :- ' + i['value'] + '\n')
                print("Mensagem salva no arquivo "+self.name+".txt")
        finally:
            FILE_LOCKS.get(self.name).release()

if __name__ == '__main__':
    # Cria pasta files
    if not os.path.exists('./files'):
        os.makedirs('./files')
    # Liga 3 Secondary Managers nas [5001-5003]
    qnt_secondarys = 3
    base = 5000
    secondarys = []
    for i in range(qnt_secondarys):
        app = Flask('secondary' + str(i + 1))
        app.add_url_rule('/save', view_func=Manager.as_view('myview', 'secondary' + str(i + 1)))
        secondarys.append(base + i + 1)
        FILE_LOCKS.update({'secondary' + str(i + 1) : threading.Lock()})
        threading.Thread(target=app.run, kwargs={'port': (base + i + 1)}).start()
    
    # Instancia 2 FrontEnds e os liga nas portas [8081-8082]
    base = 8080
    for i in range(2):
        app = Flask('frontend' + str(i + 1))
        app.add_url_rule('/save', view_func=FrontEnd.as_view('myview', 'frontend' + str(i + 1)))
        threading.Thread(target=app.run, kwargs={'port': (base + i + 1)}).start()

    # Instancia o Primary Manager e o associa a porta 5000
    app = Flask('primary')
    app.add_url_rule('/save', view_func=Manager.as_view('myview', 'primary', list(map(lambda x: 'http://127.0.0.1:{port}/save'.format(port= x), secondarys))))
    FILE_LOCKS.update({'primary' : threading.Lock()})
    app.run(port=5000)
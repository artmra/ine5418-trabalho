# ine5418-trabalho
Implementação do modelo de replicação passiva

# Passos para execução

1º Instale o Python3, pip3 e virtualenv(Comando para Ubuntu/Debian):

```
sudo apt get install python3
curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
python get-pip.py
pip3 install virtualenv
```

2º Crie um ambiente virtual:

```
python3 -m venv venv
```

3º Ative o ambiente virtual criado:

```
source venv/bin/activate
```

4º Instale so requerimentos para executar o projeto:

```
pip3 install -r requirements.txt
```

5º Abra um terminal, navegue até a pasta do projeto e execute:

```
python3 primary_backup.py
```

6º Abra outro terminal e execute o script a baixo para poder fazer requisições ao frontend; execute quantas vezes achar necessário:

```
python3 simulacao_cliente.py
```
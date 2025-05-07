import json

def arqExiste(nome):
    # VERIFICAÇÃO SE O ARQUIVO JA EXISTE
    try:
        with open(nome, 'r') as arq:
            json.load(arq)
            print(f'O arquivo {nome} já existia')

    except (FileExistsError, FileNotFoundError):
        with open(nome, 'w+') as arq:
            json.dump([], arq)
            print(f'O arquivo {nome} foi criado')
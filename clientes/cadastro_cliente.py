import json
import tkinter as tk

def salva_cliente(j, t):
    cliente = {
        "nome": nome.get(),
        "telefone": telefone.get(),
        "cpf_cnpj": cpf_cnpj.get(),
        "cep": cep.get(),
        "num_casa": num_casa.get(),
        "email": email.get()
    }

    with open('clientes.json', 'r+', encoding='utf-8') as arq:
            clientes = json.load(arq)
            clientes.append(cliente)

            arq.seek(0)
            json.dump(clientes, arq, indent=4, ensure_ascii=False)
            arq.truncate()

            print(f'Registro adicionado de {cliente["nome"]}')

    j.destroy()
    '''if t:
        i = len(clientes)-1
        mostrarCliente()'''

def cadastrocliente(t=False):
    global nome, telefone, cpf_cnpj, cep, num_casa, email

    # NOVA JANELA DO CADASTRO
    janela = tk.Toplevel()

    janela.grab_set() # PROÍBE DE MEXER NO ROOT ENQUANTO A JANELA ESTIVER ABERTA
    janela.geometry('400x300')
    janela.resizable(False, False)
    janela.title('Novo Cliente')

    # DADOS DO CLIENTE

    nome = tk.Entry(janela)
    telefone = tk.Entry(janela)
    cpf_cnpj = tk.Entry(janela)
    cep = tk.Entry(janela)
    num_casa = tk.Entry(janela)
    email = tk.Entry(janela)

    tk.Label(janela, text='Nome:').pack()
    nome.pack()
    tk.Label(janela, text='Telefone:').pack()
    telefone.pack()
    tk.Label(janela, text='CPF/CNPJ:').pack()
    cpf_cnpj.pack()
    tk.Label(janela, text='CEP:').pack()
    cep.pack()
    tk.Label(janela, text='N°:').pack()
    num_casa.pack()
    tk.Label(janela, text='E-mail:').pack()
    email.pack()

    botaoSalvar = tk.Button(janela, text='Salvar',
                            command=lambda: salva_cliente(janela, t))
    botaoSalvar.pack()

    janela.mainloop()

def ver_cadastros():
    janela = tk.Toplevel()
    janela.grab_set()
    janela.geometry('400x300')
    janela.resizable(False, False)
    janela.title('Visualizar Clientes')

    with open('clientes.json', 'r', encoding='utf-8') as arq:
            clientes = json.load(arq)


    if len(clientes) == 0:
        tk.Label(janela, text='Nenhum cliente cadastrado ainda!\n'
                              'Cadastre seu primeiro cliente clicando abaixo:').pack()
        tk.Button(janela, text='Novo Cliente', command=lambda: cadastrocliente(True)).pack()


    else:
        entrys = {}
        k = ['nome', 'telefone', 'cpf_cnpj', 'cep', 'num_casa', 'email']

        def mostrarCliente():
            global i

            cliente = clientes[i]

            for c in entrys.keys():
                entrys[c].config(state='normal') # HABILITANDO EDIÇÃO
                entrys[c].delete(0, tk.END) # APAGANDO TODOS OS CAMPOS
                entrys[c].insert(0, cliente[c]) # INSERINDO OS DADOS
                entrys[c].config(state='disabled') # DESATIVANDO EDIÇÃO

        def proximo():
            global i

            if i < len(clientes) - 1:
                i += 1
                mostrarCliente()

        def anterior():
            global i

            if i > 0:
                i -= 1
                mostrarCliente()

        def excluircliente():
            global i

            print(f'Cadastro excluido de {clientes[i]["nome"]}')
            clientes.pop(i)
            i -= 1
            mostrarCliente()

            try:
                with open('clientes.json', 'w', encoding='utf-8') as arq:
                    json.dump(clientes, arq, indent=4, ensure_ascii=False)
            except:
                print('Erro ao excluir o cadastro')

        # INFORMAÇÕES DO CADASTRO
        fonte = ('Arial', 12)

        for c in k:
            entry = tk.Entry(janela, font=fonte)
            entry.pack()
            entrys[c] = entry

        # BOTÕES
        tk.Button(janela, text='Próximo', command=proximo).pack()
        tk.Button(janela, text='Anterior', command=anterior).pack()
        tk.Button(janela, text='Novo Cliente', command=cadastrocliente).pack()
        tk.Button(janela, text='Excluir', command=excluircliente).pack()

        mostrarCliente()

i = 0
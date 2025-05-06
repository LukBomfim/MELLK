import json
import tkinter as tk

def salva_cliente(j):
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

    j.destroy()

def cadastrocliente():
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
                            command=lambda: salva_cliente(janela))
    botaoSalvar.pack()

    janela.mainloop()

def ver_cadastros():
    janela = tk.Toplevel()
    janela.grab_set()
    janela.geometry('400x300')
    janela.resizable(False, False)
    janela.title('Clientes Cadastrados')

    with open('clientes.json', 'r', encoding='utf-8') as arq:
            clientes = json.load(arq)

    frame = tk.Frame(janela, bg='red')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame.tkraise()
    cod = 0

    if len(clientes) == 0:
        tk.Label(janela, text='Nenhum cliente cadastrado ainda!\n'
                              'Cadastre seu primeiro cliente clicando abaixo:').pack()
        tk.Button(janela, text='Novo Cliente', command=cadastrocliente).pack()

    else:
        tk.Label(janela, text=f'Nome: {clientes[cod]["nome"]}\n'
                          f'Telefone: {clientes[cod]["telefone"]}\n'
                          f'CPF/CNPJ: {clientes[cod]["cpf_cnpj"]}\n'
                          f'CEP: {clientes[cod]["cep"]}\n'
                          f'N°: {clientes[cod]["num_casa"]}\n'
                          f'E-mail: {clientes[cod]["email"]}\n').pack()

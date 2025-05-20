import json, re
import tkinter as tk
from tkinter import ttk

i = 0
flagCPF = False
flagCEP = False
flagEmail = False

def inicio():
    global root

    # CRIANDO JANELA PRINCIPAL
    root = tk.Toplevel()
    root.title('CLIENTES')
    root.geometry('500x500')
    root.resizable(False, False)

    ver_cadastros()

def ver_cadastros():
    global i

    fonte = ('Arial', 12)

    with open('clientes.json', 'r', encoding='utf-8') as arq:
            clientes = json.load(arq)
            arq.close()


    # FRAME CASO NÃO TENHA CLIENTES CADASTRADOS
    frame_semcliente = tk.Frame(root)
    frame_semcliente.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame_semcliente.configure(bg='grey')
    tk.Label(frame_semcliente,
             text='Nenhum cliente cadastrado até agora.\n'
            'Cadastre seu primeiro cliente clicando abaixo:', font=fonte).pack()
    botaoNovoCliente(frame_semcliente)


    # FRAME CASO TENHA CLIENTES
    frame_verclientes = tk.Frame(root)
    frame_verclientes.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame_verclientes.configure(bg='grey')
    tk.Label(frame_verclientes, text=f'{i+1} de {len(clientes)}').pack()

    tk.Button(frame_verclientes, text='Próximo', command=proximo).pack()
    tk.Button(frame_verclientes, text='Anterior', command=anterior).pack()
    tk.Button(frame_verclientes, text='Excluir', command=confirmExcluir).pack()
    tk.Button(frame_verclientes, text='Editar', command=editar).pack()
    tk.Button(frame_verclientes, text='Pesquisar', command=pesquisar).pack()

    botaoNovoCliente(frame_verclientes)

    if not clientes:
        frame_semcliente.tkraise()

    else:
        l = ['Nome', 'Telefone', 'CPF/CNPJ', 'CEP', 'Número', 'E-mail']
        lc = 0

        entrys = {}
        k = ['nome', 'telefone', 'cpf_cnpj', 'cep', 'num_casa', 'email']
        cliente = clientes[i]

        for c in k:
            tk.Label(frame_verclientes, text=l[lc], bg='grey').pack()
            entry = tk.Entry(frame_verclientes, font=fonte)
            entry.pack()
            entrys[c] = entry
            lc += 1

        for c in entrys.keys():
            entrys[c].config(state='normal')  # ATIVANDO EDIÇÃO
            entrys[c].delete(0, tk.END)  # APAGANDO O CAMPO
            entrys[c].insert(0, cliente[c])  # INSERINDO O DADO
            entrys[c].config(state='disabled')  # DESATIVANDO EDIÇÃO

        frame_verclientes.tkraise()

def novoCliente():
    global nomeEntry, telefoneEntry, cpf_cnpjEntry, cepEntry, num_casaEntry, emailEntry, cod

    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)
        if not clientes:
            cod = 1
        else:
            cod = (clientes[-1]['cod']) + 1
        arq.close()

    # TELA DO CADASTRO
    frame_ncliente = tk.Frame(root)
    frame_ncliente.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame_ncliente.tkraise()

    fonte = ('Arial', 12)

    num = (frame_ncliente.register(entryNum), '%P')

    # ENTRYS DOS DADOS DO CADASTRO
    nomeEntry = tk.Entry(frame_ncliente, font=fonte)
    nomeEntry.bind('<FocusOut>', formNome)
    nomeEntry.bind('<KeyRelease>', formNomeCor)
    nomeEntry.bind('<FocusOut>', formNomeCor, add='+')

    telefoneEntry = tk.Entry(frame_ncliente, font=fonte, validate='key', validatecommand=num)
    telefoneEntry.bind('<KeyRelease>', formTel)

    cpf_cnpjEntry = tk.Entry(frame_ncliente, font=fonte, validate='key', validatecommand=num)
    cpf_cnpjEntry.bind('<KeyRelease>', formCPF_CNPJ)

    cepEntry = tk.Entry(frame_ncliente, font=fonte, validate='key', validatecommand=num)
    cepEntry.bind('<KeyRelease>', formCEP)

    num_casaEntry = tk.Entry(frame_ncliente, font=fonte, validate='key', validatecommand=num)

    emailEntry = tk.Entry(frame_ncliente, font=fonte)
    emailEntry.bind('<KeyRelease>', formEmail)


    tk.Label(frame_ncliente, text='Nome:').pack()
    nomeEntry.pack()
    tk.Label(frame_ncliente, text='Telefone:').pack()
    telefoneEntry.pack()
    tk.Label(frame_ncliente, text='CPF/CNPJ:').pack()
    cpf_cnpjEntry.pack()
    tk.Label(frame_ncliente, text='CEP:').pack()
    cepEntry.pack()
    tk.Label(frame_ncliente, text='N°:').pack()
    num_casaEntry.pack()
    tk.Label(frame_ncliente, text='E-mail:').pack()
    emailEntry.pack()

    tk.Button(frame_ncliente, text='Salvar', command=salva_NovoCliente).pack()
    botaoVoltar(frame_ncliente)

def entryNum(n):
    if n == '':
        return True

    for c in n:
        if c.isalpha():
            return False

    return True

def formNome(e):

    n = nomeEntry.get().upper()

    nomeEntry.delete(0, tk.END)
    nomeEntry.insert(0, n)

def formNomeCor(e):
    n = nomeEntry.get()

    if n == '':
        nomeEntry.configure(bg='pink')
    else:
        nomeEntry.configure(bg='white')

def formTel(e):

    tel = telefoneEntry.get()
    ftel = ''

    for c in tel: # FILTRANDO APENAS OS NÚMEROS
        if c.isnumeric():
            ftel += c

    if len(ftel) == 10: # TELEFONE FIXO
        ftel = f'({ftel[:2]}){ftel[2:6]}-{ftel[6:]}'
    elif len(ftel) > 10: # CELULAR
        ftel = f'({ftel[:2]}){ftel[2:7]}-{ftel[7:]}'

    telefoneEntry.configure(validate='none')
    telefoneEntry.delete(0, tk.END)
    telefoneEntry.insert(0, ftel)
    telefoneEntry.configure(validate='key')

def formCPF_CNPJ(e):
    global flagCPF

    c = cpf_cnpjEntry.get()
    fc = ''

    for n in c:
        if n.isnumeric():
            fc += n

    if len(fc) == 11: # CPF
        fc = f'{fc[:3]}.{fc[3:6]}.{fc[6:9]}-{fc[9:]}'
        cpf_cnpjEntry.configure(bg='white')
        flagCPF = False

    elif len(fc) == 14: # CNPJ
        fc = f'{fc[:2]}.{fc[2:5]}.{fc[5:8]}/{fc[8:12]}-{fc[12:]}'
        cpf_cnpjEntry.configure(bg='white')
        flagCPF = False

    elif fc == '':
        cpf_cnpjEntry.configure(bg='white')
        flagCPF = False

    else:
        cpf_cnpjEntry.configure(bg='pink')
        flagCPF = True

    cpf_cnpjEntry.delete(0, tk.END)
    cpf_cnpjEntry.insert(0, fc)

def formCEP(e):
    global flagCEP

    cep = cepEntry.get()
    fcep = ''

    for c in cep:
        if c.isnumeric():
            fcep += c

    if len(fcep) == 8:
        fcep = f'{fcep[:5]}-{fcep[5:]}'
        cepEntry.configure(bg='white')
        flagCEP = False

    elif fcep == '':
        cepEntry.configure(bg='white')
        flagCEP = False

    else:
        cepEntry.configure(bg='pink')
        flagCEP = True

    cepEntry.delete(0, tk.END)
    cepEntry.insert(0, fcep)

def formEmail(e):
    global flagEmail

    email = emailEntry.get().lower()
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$' # PADRÃO DO EMAIL EM REGEX

    if re.match(padrao, email) or email == '':
        emailEntry.configure(bg='white')
        flagEmail = False
    else:
        emailEntry.configure(bg='pink')
        flagEmail = True
    emailEntry.delete(0, tk.END)
    emailEntry.insert(0, email)

def salva_NovoCliente():
    global i, flagCPF, flagCEP, flagEmail

    if nomeEntry.get() == '' or flagCPF or flagCEP or flagEmail:
        msg = tk.Toplevel(root)
        msg.title('Corriga os dados')
        tk.Label(msg, text='Confira os dados e tente novamente.').pack()
        tk.Button(msg, text='OK', command=msg.destroy).pack()

    else:
        cliente = {
            "cod": cod,
            "nome": nomeEntry.get().upper(),
            "telefone": telefoneEntry.get(),
            "cpf_cnpj": cpf_cnpjEntry.get(),
            "cep": cepEntry.get(),
            "num_casa": num_casaEntry.get(),
            "email": emailEntry.get()
        }

        with open('clientes.json', 'r+', encoding='utf-8') as arq:
            clientes = json.load(arq)
            clientes.append(cliente)

            arq.seek(0)
            json.dump(clientes, arq, indent=4, ensure_ascii=False)
            arq.truncate()

            print(f'Registro adicionado de {cliente["nome"]}')
            arq.close()

        i = len(clientes)-1
        ver_cadastros()

def botaoNovoCliente(f):
    tk.Button(f, text='Novo', command=novoCliente).pack()

def botaoVoltar(f):
    tk.Button(f, text='Voltar', command=ver_cadastros).pack()

def proximo():
    global i

    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)
        arq.close()

    if i < len(clientes)-1:
        i += 1
        ver_cadastros()

def anterior():
    global i

    if i > 0:
        i -= 1
        ver_cadastros()

def confirmExcluir():
    janela = tk.Toplevel(root) # MENSAGEM DE CONFIRMAÇÃO
    janela.title('Excluir cliente')
    janela.geometry('200x100')
    janela.grab_set()
    janela.resizable(False, False)

    tk.Label(janela, text=f'Tem certeza que deseja excluir?').pack()
    tk.Button(janela, text='Excluir', command=lambda: excluir(janela)).pack()
    tk.Button(janela, text='Cancelar', command=janela.destroy).pack()

def excluir(j):
    global i

    with open('clientes.json', 'r+', encoding='utf-8') as arq:
        clientes = json.load(arq)
        try:
            print(f'Cadastro excluido de: {clientes[i]["nome"]}')
            clientes.pop(i)
            if i != 0:
                i -= 1

            arq.seek(0)
            json.dump(clientes, arq, indent=4, ensure_ascii=False)
            arq.truncate()
            ver_cadastros()

        except:
            print(f'Erro ao excluir o cadastro de {clientes[i]["nome"]}')

        arq.close()
    j.destroy()

def editar():
    global i, nomeEntry, telefoneEntry, cepEntry, cpf_cnpjEntry, num_casaEntry, emailEntry

    fonte = ('Arial', 12)

    frame_editar = tk.Frame(root)
    frame_editar.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Button(frame_editar, text='Salvar', command=salvaedicao).pack()
    tk.Button(frame_editar, text='Cancelar', command=ver_cadastros).pack()

    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)
        arq.close()

    num = (frame_editar.register(entryNum), '%P')

    tk.Label(frame_editar, text='Nome:').pack()
    nomeEntry = tk.Entry(frame_editar, font=fonte)
    nomeEntry.insert(0, clientes[i]['nome'])
    nomeEntry.bind('<FocusOut>', formNome)
    nomeEntry.pack()

    tk.Label(frame_editar, text='Telefone:').pack()
    telefoneEntry = tk.Entry(frame_editar, font=fonte, validate='key', validatecommand=num)
    telefoneEntry.insert(0, clientes[i]['telefone'])
    telefoneEntry.bind('<KeyRelease>', formTel)
    telefoneEntry.pack()

    tk.Label(frame_editar, text='CPF/CNPJ:').pack()
    cpf_cnpjEntry = tk.Entry(frame_editar, font=fonte, validate='key', validatecommand=num)
    cpf_cnpjEntry.insert(0, clientes[i]['cpf_cnpj'])
    cpf_cnpjEntry.bind('<KeyRelease>', formCPF_CNPJ)
    cpf_cnpjEntry.pack()

    tk.Label(frame_editar, text='CEP:').pack()
    cepEntry = tk.Entry(frame_editar, font=fonte, validate='key', validatecommand=num)
    cepEntry.insert(0, clientes[i]['cep'])
    cepEntry.bind('<KeyRelease>', formCEP)
    cepEntry.pack()

    tk.Label(frame_editar, text='N°:').pack()
    num_casaEntry = tk.Entry(frame_editar, font=fonte)
    num_casaEntry.insert(0, clientes[i]['num_casa'])
    num_casaEntry.pack()

    tk.Label(frame_editar, text='E-mail:').pack()
    emailEntry = tk.Entry(frame_editar, font=fonte)
    emailEntry.insert(0, clientes[i]['email'])
    emailEntry.bind('<KeyRelease>', formEmail)
    emailEntry.pack()

    frame_editar.tkraise()

def salvaedicao():
    global i
    if nomeEntry.get() == '' or flagCPF or flagCEP or flagEmail:
        msg = tk.Toplevel(root)
        msg.title('Corriga os dados')
        tk.Label(msg, text='Confira os dados e tente novamente.').pack()
        tk.Button(msg, text='OK', command=msg.destroy).pack()

    else:
        try:
            with open('clientes.json', 'r+', encoding='utf-8') as arq:
                clientes = json.load(arq)

                clientes[i]['nome'] = nomeEntry.get()
                clientes[i]['telefone'] = telefoneEntry.get()
                clientes[i]['cpf_cnpj'] = cpf_cnpjEntry.get()
                clientes[i]['cep'] = cepEntry.get()
                clientes[i]['num_casa'] = num_casaEntry.get()
                clientes[i]['email'] = emailEntry.get()

                arq.seek(0)
                json.dump(clientes, arq, indent=4, ensure_ascii=False)
                arq.truncate()

                arq.close()

            ver_cadastros()

        except:
            print('Erro ao editar o cadastro')

def pesquisar():
    global lista

    janela = tk.Toplevel()
    janela.geometry('900x400')
    janela.grab_set()
    janela.title('Busca de cliente')

    tk.Label(janela, text='Pesquisa por:').pack()
    opc = ttk.Combobox(janela, values=['Nome', 'Telefone', 'CPF/CNPJ'], state='readonly')
    opc.set('Nome')
    opc.pack()

    pesquisa = tk.Entry(janela)
    pesquisa.pack()

    dados = ['cod', 'nome', 'telefone', 'cpf_cnpj']
    lista = ttk.Treeview(janela, columns=dados, show='headings')
    lista.heading('cod', text='Cód.')
    lista.heading('nome', text='Nome')
    lista.heading('telefone', text='Telefone')
    lista.heading('cpf_cnpj', text='CPF/CNPJ')

    tk.Button(janela, text='Procurar', command=lambda: botaoProcurar(janela, opc, pesquisa)).pack()
    pesquisa.bind('<Return>', lambda event: botaoProcurar(janela, opc, pesquisa))

    lista.pack()

def botaoProcurar(j, cb, pe):
    global i

    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)
        arq.close()

    opc = cb.get()
    pesq = pe.get()

    resultados = []

    if opc == 'Nome':
        if not pesq == '':
            for cliente in clientes:
                if pesq.upper() in cliente['nome']:
                    c = {
                        'cod': clientes.index(cliente),
                        'nome': cliente['nome'],
                        'telefone': cliente['telefone'],
                        'cpf_cnpj': cliente['cpf_cnpj']
                    }
                    resultados.append(c)

    elif opc == 'Telefone':

        p = ''
        for n in pesq:
            if n.isnumeric():
                p += n

        if not p == '':
            for cliente in clientes:

                tel = ''
                for n in cliente['telefone']: # FILTRANDO APENAS OS NÚMEROS
                    if n.isnumeric():
                        tel += n

                if p in tel:
                    c = {
                        'cod': clientes.index(cliente),
                        'nome': cliente['nome'],
                        'telefone': cliente['telefone'],
                        'cpf_cnpj': cliente['cpf_cnpj']
                    }
                    resultados.append(c)

    elif opc == 'CPF/CNPJ':

        p = ''
        for n in pesq:
            if n.isnumeric():
                p += n

        if not p == '':
            for cliente in clientes:

                cpf = ''
                for n in cliente['cpf_cnpj']: # FILTRANDO APENAS OS NÚMEROS
                    if n.isnumeric():
                        cpf += n

                if p in cpf:
                    c = {
                        'cod': clientes.index(cliente),
                        'nome': cliente['nome'],
                        'telefone': cliente['telefone'],
                        'cpf_cnpj': cliente['cpf_cnpj']
                    }
                    resultados.append(c)

    for r in lista.get_children():
        lista.delete(r)

    for r in resultados:
        lista.insert('', 'end', iid=r['cod'], values=(
            r['cod'],
            r['nome'],
            r['telefone'],
            r['cpf_cnpj']
        ))

    lista.bind('<Double-1>', lambda event: selecionar(event, j))

def selecionar(e, j):
    global i

    try:
        i = int(lista.focus())
        j.destroy()
        ver_cadastros()
    except:
        print('Nenhum resultado')

import json
import re
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font as tkfont

i = 0
flagCPF = False
flagCEP = False
flagEmail = False

def inicio():
    global root

    # CRIANDO JANELA PRINCIPAL
    root = tk.Toplevel()
    root.title('MELLK - Clientes')
    root.geometry('600x600')
    root.configure(bg='#1A3C34')
    root.resizable(True, True)

    # Estilo dos botões
    global button_style
    button_style = {
        'font': ('Arial', 12),
        'bg': 'white',
        'fg': 'black',
        'activebackground': '#E5E5E5',
        'activeforeground': 'black',
        'width': 12,
        'height': 1,
        'borderwidth': 1,
        'cursor': 'hand2',
        'relief': 'flat'
    }

    ver_cadastros()

def ver_cadastros():
    global i

    fonte = ('Arial', 12)
    fonte_bold = ('Arial', 14, 'bold')

    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)

    # FRAME PRINCIPAL
    frame_verclientes = tk.Frame(root, bg='#1A3C34')
    frame_verclientes.place(relx=0, rely=0, relwidth=1, relheight=1)

    # FRAME CASO NÃO TENHA CLIENTES
    frame_semcliente = tk.Frame(root, bg='#1A3C34')
    frame_semcliente.place(relx=0, rely=0, relwidth=1, relheight=1)
    tk.Label(frame_semcliente,
             text='Nenhum cliente cadastrado.\nCadastre seu primeiro cliente abaixo:',
             font=fonte_bold, fg='white', bg='#1A3C34').place(relx=0.5, rely=0.4, anchor='center')
    botaoNovoCliente(frame_semcliente)

    # CABEÇALHO
    tk.Label(frame_verclientes, text=f'Cliente {i+1} de {len(clientes)}', font=fonte_bold, fg='white', bg='#1A3C34').pack(pady=20)

    # BOTÕES DE NAVEGAÇÃO
    nav_frame = tk.Frame(frame_verclientes, bg='#1A3C34')
    nav_frame.pack(pady=10)
    tk.Button(nav_frame, text='Anterior', command=anterior, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(nav_frame, text='Próximo', command=proximo, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(nav_frame, text='Excluir', command=confirmExcluir, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(nav_frame, text='Editar', command=editar, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(nav_frame, text='Pesquisar', command=pesquisar, **button_style).pack(side=tk.LEFT, padx=5)
    botaoNovoCliente(frame_verclientes)

    if not clientes:
        frame_semcliente.tkraise()
    else:
        l = ['Nome', 'Telefone', 'CPF/CNPJ', 'CEP', 'Número', 'E-mail']
        k = ['nome', 'telefone', 'cpf_cnpj', 'cep', 'num_casa', 'email']
        cliente = clientes[i]

        entrys = {}
        for idx, field in enumerate(k):
            tk.Label(frame_verclientes, text=l[idx], font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
            entry = tk.Entry(frame_verclientes, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')
            entry.pack(pady=2)
            entrys[field] = entry

        for c in entrys.keys():
            entrys[c].config(state='normal')
            entrys[c].delete(0, tk.END)
            entrys[c].insert(0, cliente[c])
            entrys[c].config(state='disabled')

        frame_verclientes.tkraise()

def novoCliente():
    global nomeEntry, telefoneEntry, cpf_cnpjEntry, cepEntry, num_casaEntry, emailEntry, cod

    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)
        cod = 1 if not clientes else clientes[-1]['cod'] + 1

    # FRAME DO CADASTRO
    frame_ncliente = tk.Frame(root, bg='#1A3C34')
    frame_ncliente.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    num = (frame_ncliente.register(entryNum), '%P')

    # ENTRYS DOS DADOS
    nomeEntry = tk.Entry(frame_ncliente, font=fonte, width=30)
    telefoneEntry = tk.Entry(frame_ncliente, font=fonte, width=30, validate='key', validatecommand=num)
    cpf_cnpjEntry = tk.Entry(frame_ncliente, font=fonte, width=30, validate='key', validatecommand=num)
    cepEntry = tk.Entry(frame_ncliente, font=fonte, width=30, validate='key', validatecommand=num)
    num_casaEntry = tk.Entry(frame_ncliente, font=fonte, width=30, validate='key', validatecommand=num)
    emailEntry = tk.Entry(frame_ncliente, font=fonte, width=30)

    fields = [
        ('Nome:', nomeEntry, [formNome, formNomeCor]),
        ('Telefone:', telefoneEntry, formTel),
        ('CPF/CNPJ:', cpf_cnpjEntry, formCPF_CNPJ),
        ('CEP:', cepEntry, formCEP),
        ('N°:', num_casaEntry, None),
        ('E-mail:', emailEntry, formEmail)
    ]

    for label_text, entry, bind_func in fields:
        tk.Label(frame_ncliente, text=label_text, font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        entry.pack(pady=2)
        if bind_func:
            if isinstance(bind_func, list):
                entry.bind('<FocusOut>', bind_func[0])
                entry.bind('<KeyRelease>', bind_func[1])
            else:
                entry.bind('<KeyRelease>', bind_func)

    # BOTÕES
    tk.Button(frame_ncliente, text='Salvar', command=salva_NovoCliente, **button_style).pack(pady=10)
    botaoVoltar(frame_ncliente)
    frame_ncliente.tkraise()

def entryNum(n):
    if n == '':
        return True
    return all(not c.isalpha() for c in n)

def formNome(e):
    n = nomeEntry.get().upper()
    nomeEntry.delete(0, tk.END)
    nomeEntry.insert(0, n)

def formNomeCor(e):
    n = nomeEntry.get()
    nomeEntry.configure(bg='pink' if n == '' else 'white')

def formTel(e):
    tel = ''.join(c for c in telefoneEntry.get() if c.isnumeric())
    if len(tel) == 10:
        ftel = f'({tel[:2]}){tel[2:6]}-{tel[6:]}'
    elif len(tel) == 11:
        ftel = f'({tel[:2]}){tel[2:7]}-{tel[7:]}'
    else:
        ftel = tel
    telefoneEntry.configure(validate='none')
    telefoneEntry.delete(0, tk.END)
    telefoneEntry.insert(0, ftel)
    telefoneEntry.configure(validate='key')

def formCPF_CNPJ(e):
    global flagCPF
    c = ''.join(n for n in cpf_cnpjEntry.get() if n.isnumeric())
    if len(c) == 11:
        fc = f'{c[:3]}.{c[3:6]}.{c[6:9]}-{c[9:]}'
        cpf_cnpjEntry.configure(bg='white')
        flagCPF = False
    elif len(c) == 14:
        fc = f'{c[:2]}.{c[2:5]}.{c[5:8]}/{c[8:12]}-{c[12:]}'
        cpf_cnpjEntry.configure(bg='white')
        flagCPF = False
    else:
        fc = c
        cpf_cnpjEntry.configure(bg='pink' if c else 'white')
        flagCPF = bool(c)
    cpf_cnpjEntry.delete(0, tk.END)
    cpf_cnpjEntry.insert(0, fc)

def formCEP(e):
    global flagCEP
    cep = ''.join(c for c in cepEntry.get() if c.isnumeric())
    if len(cep) == 8:
        fcep = f'{cep[:5]}-{cep[5:]}'
        cepEntry.configure(bg='white')
        flagCEP = False
    else:
        fcep = cep
        cepEntry.configure(bg='pink' if cep else 'white')
        flagCEP = bool(cep)
    cepEntry.delete(0, tk.END)
    cepEntry.insert(0, fcep)

def formEmail(e):
    global flagEmail
    email = emailEntry.get().lower()
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    flagEmail = not (re.match(padrao, email) or email == '')
    emailEntry.configure(bg='pink' if flagEmail else 'white')
    emailEntry.delete(0, tk.END)
    emailEntry.insert(0, email)

def salva_NovoCliente():
    global i, flagCPF, flagCEP, flagEmail
    if nomeEntry.get() == '' or flagCPF or flagCEP or flagEmail:
        messagebox.showerror('Erro', 'Confira os dados e tente novamente.')
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
        i = len(clientes)
        ver_cadastros()

def botaoNovoCliente(f):
    tk.Button(f, text='Novo Cliente', command=novoCliente, **button_style).place(relx=0.5, y=(root.winfo_screenheight())//2+100, anchor='center')

def botaoVoltar(f):
    tk.Button(f, text='Voltar', command=ver_cadastros, **button_style).place(relx=0.5, rely=0.9, anchor='center')

def proximo():
    global i
    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)
    if i < len(clientes) - 1:
        i += 1
        ver_cadastros()

def anterior():
    global i
    if i > 0:
        i -= 1
        ver_cadastros()

def confirmExcluir():
    janela = tk.Toplevel(root)
    janela.title('Excluir Cliente')
    janela.geometry('300x150')
    janela.configure(bg='#1A3C34')
    janela.grab_set()
    janela.resizable(False, False)
    tk.Label(janela, text='Tem certeza que deseja excluir este cliente?', font=('Arial', 11), fg='white', bg='#1A3C34').pack(pady=20)
    tk.Button(janela, text='Excluir', command=lambda: excluir(janela), **button_style).pack(pady=5)
    tk.Button(janela, text='Cancelar', command=janela.destroy, **button_style).pack(pady=5)

def excluir(j):
    global i
    with open('clientes.json', 'r+', encoding='utf-8') as arq:
        clientes = json.load(arq)
        try:
            clientes.pop(i)
            if i != 0 and i >= len(clientes):
                i -= 1
            arq.seek(0)
            json.dump(clientes, arq, indent=4, ensure_ascii=False)
            arq.truncate()
            ver_cadastros()
        except:
            messagebox.showerror('Erro', 'Erro ao excluir o cadastro.')
    j.destroy()

def editar():
    global i, nomeEntry, telefoneEntry, cepEntry, cpf_cnpjEntry, num_casaEntry, emailEntry
    frame_editar = tk.Frame(root, bg='#1A3C34')
    frame_editar.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)

    nomeEntry = tk.Entry(frame_editar, font=fonte, width=30)
    telefoneEntry = tk.Entry(frame_editar, font=fonte, width=30, validate='key', validatecommand=(frame_editar.register(entryNum), '%P'))
    cpf_cnpjEntry = tk.Entry(frame_editar, font=fonte, width=30, validate='key', validatecommand=(frame_editar.register(entryNum), '%P'))
    cepEntry = tk.Entry(frame_editar, font=fonte, width=30, validate='key', validatecommand=(frame_editar.register(entryNum), '%P'))
    num_casaEntry = tk.Entry(frame_editar, font=fonte, width=30, validate='key', validatecommand=(frame_editar.register(entryNum), '%P'))
    emailEntry = tk.Entry(frame_editar, font=fonte, width=30)

    fields = [
        ('Nome:', nomeEntry, [formNome, formNomeCor], clientes[i]['nome']),
        ('Telefone:', telefoneEntry, formTel, clientes[i]['telefone']),
        ('CPF/CNPJ:', cpf_cnpjEntry, formCPF_CNPJ, clientes[i]['cpf_cnpj']),
        ('CEP:', cepEntry, formCEP, clientes[i]['cep']),
        ('N°:', num_casaEntry, None, clientes[i]['num_casa']),
        ('E-mail:', emailEntry, formEmail, clientes[i]['email'])
    ]

    for label_text, entry, bind_func, value in fields:
        tk.Label(frame_editar, text=label_text, font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        entry.insert(0, value)
        entry.pack(pady=2)
        if bind_func:
            if isinstance(bind_func, list):
                entry.bind('<FocusOut>', bind_func[0])
                entry.bind('<KeyRelease>', bind_func[1])
            else:
                entry.bind('<KeyRelease>', bind_func)

    tk.Button(frame_editar, text='Salvar', command=salvaedicao, **button_style).pack(pady=10)
    tk.Button(frame_editar, text='Cancelar', command=ver_cadastros, **button_style).pack(pady=5)
    frame_editar.tkraise()

def salvaedicao():
    global i
    if nomeEntry.get() == '' or flagCPF or flagCEP or flagEmail:
        messagebox.showerror('Erro', 'Confira os dados e tente novamente.')
    else:
        try:
            with open('clientes.json', 'r+', encoding='utf-8') as arq:
                clientes = json.load(arq)
                clientes[i].update({
                    'nome': nomeEntry.get(),
                    'telefone': telefoneEntry.get(),
                    'cpf_cnpj': cpf_cnpjEntry.get(),
                    'cep': cepEntry.get(),
                    'num_casa': num_casaEntry.get(),
                    'email': emailEntry.get()
                })
                arq.seek(0)
                json.dump(clientes, arq, indent=4, ensure_ascii=False)
                arq.truncate()
            ver_cadastros()
        except:
            messagebox.showerror('Erro', 'Erro ao editar o cadastro.')

def pesquisar():
    global lista
    janela = tk.Toplevel()
    janela.title('MELLK - Busca de Cliente')
    janela.geometry('900x500')
    janela.configure(bg='#1A3C34')
    janela.grab_set()

    tk.Label(janela, text='Pesquisar por:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=10)
    opc = ttk.Combobox(janela, values=['Nome', 'Telefone', 'CPF/CNPJ'], state='readonly', font=('Arial', 12))
    opc.set('Nome')
    opc.pack(pady=5)

    pesquisa = tk.Entry(janela, font=('Arial', 12), width=30)
    pesquisa.pack(pady=5)

    dados = ['cod', 'nome', 'telefone', 'cpf_cnpj']
    lista = ttk.Treeview(janela, columns=dados, show='headings', height=15)
    lista.heading('cod', text='Cód.')
    lista.heading('nome', text='Nome')
    lista.heading('telefone', text='Telefone')
    lista.heading('cpf_cnpj', text='CPF/CNPJ')
    lista.column('cod', width=50)
    lista.column('nome', width=300)
    lista.column('telefone', width=150)
    lista.column('cpf_cnpj', width=150)

    # Scrollbar
    scrollbar = ttk.Scrollbar(janela, orient='vertical', command=lista.yview)
    lista.configure(yscrollcommand=scrollbar.set)
    lista.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    tk.Button(janela, text='Procurar', command=lambda: botaoProcurar(janela, opc, pesquisa), **button_style).pack(pady=10)
    pesquisa.bind('<Return>', lambda event: botaoProcurar(janela, opc, pesquisa))

def botaoProcurar(j, cb, pe):
    global i
    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)

    opc = cb.get()
    pesq = pe.get()
    resultados = []

    if opc == 'Nome' and pesq:
        resultados = [
            {'cod': idx, 'nome': c['nome'], 'telefone': c['telefone'], 'cpf_cnpj': c['cpf_cnpj']}
            for idx, c in enumerate(clientes) if pesq.upper() in c['nome']
        ]
    elif opc == 'Telefone' and pesq:
        p = ''.join(n for n in pesq if n.isnumeric())
        resultados = [
            {'cod': idx, 'nome': c['nome'], 'telefone': c['telefone'], 'cpf_cnpj': c['cpf_cnpj']}
            for idx, c in enumerate(clientes) if p in ''.join(n for n in c['telefone'] if n.isnumeric())
        ]
    elif opc == 'CPF/CNPJ' and pesq:
        p = ''.join(n for n in pesq if n.isnumeric())
        resultados = [
            {'cod': idx, 'nome': c['nome'], 'telefone': c['telefone'], 'cpf_cnpj': c['cpf_cnpj']}
            for idx, c in enumerate(clientes) if p in ''.join(n for n in c['cpf_cnpj'] if n.isnumeric())
        ]

    for r in lista.get_children():
        lista.delete(r)
    for r in resultados:
        lista.insert('', 'end', iid=r['cod'], values=(r['cod'], r['nome'], r['telefone'], r['cpf_cnpj']))

    lista.bind('<Double-1>', lambda event: selecionar(event, j))

def selecionar(e, j):
    global i
    try:
        i = int(lista.focus())
        j.destroy()
        ver_cadastros()
    except:
        messagebox.showinfo('Aviso', 'Nenhum resultado selecionado.')
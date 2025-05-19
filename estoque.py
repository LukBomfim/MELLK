import json
import tkinter as tk
from tkinter import ttk


def inicio():
    global tabela, root

    root = tk.Toplevel()
    root.geometry('1500x500')
    root.title('ESTOQUE')
    # root.state('zoomed')

    frame_estoque = tk.Frame(root)
    frame_estoque.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame_estoque.tkraise()
    frame_estoque.configure(bg='grey')

    tk.Button(frame_estoque, text='Novo Item', command=novoItem).pack()
    tk.Button(frame_estoque, text='Excluir', command=botaoExcluir).pack()
    tk.Button(frame_estoque, text='Editar', command=editar).pack()

            # ENTRYS PARA PESQUISAR
    tk.Label(frame_estoque, text='Código:').pack()
    codPesq = tk.Entry(frame_estoque)
    codPesq.pack()
    tk.Label(frame_estoque, text='Nome:').pack()
    nomePesq = tk.Entry(frame_estoque)
    nomePesq.pack()
    tk.Label(frame_estoque, text='Obs.:').pack()
    obsPesq = tk.Entry(frame_estoque)
    obsPesq.pack()

    pesq = [codPesq, nomePesq, obsPesq]
    tk.Button(frame_estoque, text='Procurar', command=lambda: botaoProcurar(p=pesq)).pack()
    tk.Button(frame_estoque, text='Limpar', command=lambda: limpar(pesq)).pack()
    root.bind('<Return>', lambda event: botaoProcurar(pesq, event))

    colunas = ['cod', 'nome', 'preco_venda', 'preco_custo', 'lucro', 'qtd', 'obs']

    tabela = ttk.Treeview(frame_estoque, columns=colunas, show='headings')
    tabela.heading('cod', text='Cód.')
    tabela.heading('nome', text='Descrição')
    tabela.heading('preco_venda', text='Venda')
    tabela.heading('preco_custo', text='Custo')
    tabela.heading('lucro', text='Lucro')
    tabela.heading('qtd', text='Disponível')
    tabela.heading('obs', text='Observação')

    atualizarTabela()

    tabela.bind('<Double-1>', editar)

    tabela.pack()

def botaoProcurar(p, e=None):
    estoque = receberEstoque()

    cod = p[0].get()
    nome = p[1].get().upper()
    obs = p[2].get()

    resultados = []

    for item in estoque:
        if cod in str(item['cod']) and nome in item['nome'] and obs in item['obs']:
            resultados.append(item.copy())

    for produto in tabela.get_children():
        tabela.delete(produto)

    for item in resultados:
        tabela.insert('', 'end', values=(
            item['cod'],
            item['nome'],
            f"{item['preco_venda']:.2f}",
            f"{item['preco_custo']:.2f}",
            item['lucro'],
            f"{item['qtd']:.2f}",
            item['obs']
        ))


def limpar(pesq):
    for p in pesq:
        p.delete(0, tk.END)

    botaoProcurar(pesq)

def editar(e=None):
    ind = tabela.focus()
    estoque = receberEstoque()

    if ind.isnumeric():
        item = estoque[int(ind)]

        janela = tk.Toplevel()
        janela.geometry('500x500')
        janela.title('Produto')
        janela.resizable(False, False)
        janela.grab_set()

        # FUNÇÕES PARA ENTRAR APENAS NÚMEROS
        numInt = (janela.register(entryNumInt), '%P')
        numFloat = (janela.register(entryNumFloat), '%P')

        codEntry = tk.Entry(janela, validate='key', validatecommand=numInt)
        codEntry.insert(0, item['cod'])

        nomeEntry = tk.Entry(janela)
        nomeEntry.bind('<FocusOut>', lambda event: formNome(event, nomeEntry))
        nomeEntry.insert(0, item['nome'])

        custoEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
        custoEntry.bind('<FocusOut>', lambda event: formFloat(event, custoEntry))
        custoEntry.bind('<FocusOut>', lambda event: vendaAlt(event, custoEntry, vendaEntry, lucroEntry), add='+')
        custoEntry.insert(0, item['preco_custo'])

        vendaEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
        vendaEntry.bind('<FocusOut>', lambda event: formFloat(event, vendaEntry))
        vendaEntry.bind('<FocusOut>', lambda event: vendaAlt(event, custoEntry, vendaEntry, lucroEntry), add='+')
        vendaEntry.insert(0, item['preco_venda'])

        lucroEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
        lucroEntry.bind('<FocusOut>', lambda event: formFloat(event, lucroEntry))
        lucroEntry.bind('<FocusOut>', lambda event: lucroAlt(event, custoEntry, vendaEntry, lucroEntry), add='+')
        lucroEntry.insert(0, item['lucro'])

        qtdEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
        qtdEntry.bind('<FocusOut>', lambda event: formFloat(event, qtdEntry))
        qtdEntry.insert(0, item['qtd'])

        obsText = tk.Text(janela, height=10, width=50)
        obsText.insert(1.0, item['obs'])

        tk.Label(janela, text='*Cód.:').pack()
        codEntry.pack()

        tk.Label(janela, text='*Nome:').pack()
        nomeEntry.pack()

        tk.Label(janela, text='*Custo:').pack()
        custoEntry.pack()

        tk.Label(janela, text='*Venda:').pack()
        vendaEntry.pack()

        tk.Label(janela, text='*Lucro: %').pack()
        lucroEntry.pack()

        tk.Label(janela, text='*Disponível:').pack()
        qtdEntry.pack()

        tk.Label(janela, text='Observações:').pack()
        obsText.pack()

        item_edt = {
        'univ_cod': item['univ_cod'],
        'cod': codEntry,
        'nome': nomeEntry,
        'preco_venda': vendaEntry,
        'preco_custo': custoEntry,
        'lucro': lucroEntry,
        'qtd': qtdEntry,
        'obs': obsText
    }

        tk.Button(janela, text='Salvar', command=lambda: salvar(janela, item_edt, False)).pack()
        tk.Button(janela, text='Cancelar', command=janela.destroy).pack()

def botaoExcluir():
    estoque = receberEstoque()

    ind = tabela.focus()

    if ind.isnumeric():
        msg = tk.Toplevel(root)
        msg.geometry('400x100')
        msg.grab_set()
        msg.resizable(False, False)
        msg.title('Excluir')
        tk.Label(msg, text=f'Tem certeza que deseja excluir o item {estoque[int(ind)]["nome"]}?', font=('Arial', 10)).pack()
        tk.Button(msg, text='Excluir', font=('Arial', 12), command=lambda: excluir(msg)).pack()
        tk.Button(msg, text='Cancelar', font=('Arial', 12), command=msg.destroy).pack()

def excluir(m):
    estoque = receberEstoque()
    ind = int(tabela.focus())

    nome = estoque[ind]['nome']
    estoque.pop(ind)

    try:
        with open('estoque.json', 'w', encoding='utf-8') as arq:
            json.dump(estoque, arq, indent=4, ensure_ascii=False)
            print(f'Item excluido: {nome}')
            arq.close()
    except:
        print('Erro ao excluir item')

    m.destroy()
    atualizarTabela()

def novoItem():
    global univ_cod

    janela = tk.Toplevel()
    janela.geometry('500x500')
    janela.title('Novo Item')
    janela.resizable(False, False)
    janela.grab_set()

    with open('estoque.json', 'r', encoding='utf-8') as arq:
        estoque = json.load(arq)
        if not estoque:
            univ_cod = 1
        else:
            univ_cod = (estoque[-1]['univ_cod']) + 1
        arq.close()

    # FUNÇÕES PARA ENTRAR APENAS NÚMEROS
    numInt = (janela.register(entryNumInt), '%P')
    numFloat = (janela.register(entryNumFloat), '%P')

                        # DADOS DO ITEM

    codEntry = tk.Entry(janela, validate='key', validatecommand=numInt)

    nomeEntry = tk.Entry(janela)
    nomeEntry.bind('<FocusOut>', lambda event: formNome(event, nomeEntry))

    custoEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
    custoEntry.bind('<FocusOut>', lambda event: formFloat(event, custoEntry))
    custoEntry.bind('<FocusOut>', lambda event: vendaAlt(event, custoEntry, vendaEntry, lucroEntry), add='+')

    vendaEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
    vendaEntry.bind('<FocusOut>', lambda event: formFloat(event, vendaEntry))
    vendaEntry.bind('<FocusOut>', lambda event: vendaAlt(event, custoEntry, vendaEntry, lucroEntry), add='+')

    lucroEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
    lucroEntry.bind('<FocusOut>', lambda event: formFloat(event, lucroEntry))
    lucroEntry.bind('<FocusOut>', lambda event: lucroAlt(event, custoEntry, vendaEntry, lucroEntry), add='+')

    qtdEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
    qtdEntry.bind('<FocusOut>', lambda event: formFloat(event, qtdEntry))

    obsText = tk.Text(janela, height=10, width=50)

    tk.Label(janela, text='*Cód.:').pack()
    codEntry.pack()

    tk.Label(janela, text='*Nome:').pack()
    nomeEntry.pack()

    tk.Label(janela, text='*Custo:').pack()
    custoEntry.pack()

    tk.Label(janela, text='*Venda:').pack()
    vendaEntry.pack()

    tk.Label(janela, text='*Lucro: %').pack()
    lucroEntry.pack()

    tk.Label(janela, text='*Disponível:').pack()
    qtdEntry.pack()

    tk.Label(janela, text='Observações:').pack()
    obsText.pack()

    codEntry.insert(0, univ_cod)

    itemEntry = {
        'univ_cod': univ_cod,
        'cod': codEntry,
        'nome': nomeEntry,
        'preco_venda': vendaEntry,
        'preco_custo': custoEntry,
        'lucro': lucroEntry,
        'qtd': qtdEntry,
        'obs': obsText
    }

    tk.Button(janela, text='Salvar', command=lambda: salvar(janela, itemEntry)).pack()
    tk.Button(janela, text='Cancelar', command=janela.destroy).pack()

def entryNumInt(n):
    if n == '':
        return True
    try:
        int(n)
        return True
    except:
        return False

def entryNumFloat(n):
    if n == '':
        return True
    try:
        float(n)
        return True
    except:
        return False

def convertNum(n):
    if not n == '':
        try:
            num = int(n)
            return num
        except:
            num = float(n)
            return num
    return None

def lucroAlt(e, c, v, l):
    if c.get() == '':
        custo = 0
    else:
        custo = float(c.get())

    if l.get() == '':
        lucro = 0
    else:
        lucro = float(l.get())

    venda = custo + ((custo/100) * lucro)

    v.delete(0, tk.END)
    v.insert(0, f'{venda:.2f}')

def vendaAlt(e, c, v, l):
    if c.get() == '':
        custo = 0
    else:
        custo = float(c.get())

    if v.get() == '':
        venda = 0
    else:
        venda = float(v.get())

    l.delete(0, tk.END)

    if custo == 0:
        if venda == 0:
            l.insert(0, '0.00')
        else:
            l.insert(0, '100.00')

    else:
        lucro = ((venda - custo) / custo) * 100
        l.insert(0, f'{lucro:.2f}')

def formNome(e, nome):
    fnome = nome.get().upper()

    nome.delete(0, tk.END)
    nome.insert(0, fnome)

def formFloat(e, n):
    fn = n.get()
    n.delete(0, tk.END)
    if fn == '':
        n.insert(0, '0.00')
    else:
        n.insert(0, f'{float(fn):.2f}')

def receberEstoque():
    with open('estoque.json', 'r', encoding='utf-8') as arq:
        estoque = json.load(arq)
        arq.close()
    return estoque

def atualizarTabela():
    estoque = receberEstoque()

    for i in tabela.get_children():
        tabela.delete(i)

    for produto in estoque:
        tabela.insert('', 'end', iid=estoque.index(produto), values=(
            produto['cod'],
            produto['nome'],
            f"{produto['preco_venda']:.2f}",
            f"{produto['preco_custo']:.2f}",
            produto['lucro'],
            f"{produto['qtd']:.2f}",
            produto['obs']
        ))

def salvar(janela, entry, novo=True):
    if not novo:
        ind = int(tabela.focus())
    else:
        ind = ''

    estoque = receberEstoque()
    flagCod = False
    flagNull = False

    k = ['cod', 'nome', 'preco_venda', 'preco_custo', 'lucro', 'qtd']
    obrig = ['cod', 'nome', 'preco_venda', 'preco_custo', 'lucro', 'qtd']

    item = {'univ_cod': entry['univ_cod']}

    # RECEBENDO OS DADOS
    for key in k:
        if key == 'cod' or key == 'preco_venda' or key == 'preco_custo' or key == 'lucro' or key == 'qtd':
            n = convertNum(entry[key].get())
        else:
            n = entry[key].get()

        item[key] = n

    item['obs'] = entry['obs'].get('1.0', 'end-1c')

            # VERIFICAÇÃO DAS FLAGS

    # CASO TENHA CÓDIGO REPETIDO
    for produto in estoque:
        if produto['cod'] == item['cod'] and estoque.index(produto) != ind:
            flagCod = True
            break

    # CASO ALGUM DADO OBRIGATÓRIO ESTEJA VAZIO
    for o in obrig:
        if not item[o]:
            flagNull = True
            break

    if flagCod:
        msg = tk.Toplevel(janela)
        msg.geometry('300x100')
        msg.grab_set()
        msg.resizable(False, False)
        msg.title('Erro')
        tk.Label(msg, text='Código já cadastrado!', font=('Arial', 10)).pack()
        tk.Button(msg, text='Ok', font=('Arial', 12), command=msg.destroy).pack()

    elif flagNull:
        msg = tk.Toplevel(janela)
        msg.geometry('300x100')
        msg.grab_set()
        msg.resizable(False, False)
        msg.title('Erro')
        tk.Label(msg, text='Preencha os dados obrigatórios! *', font=('Arial', 10)).pack()
        tk.Button(msg, text='Ok', command=msg.destroy).pack()

    else:
        if novo:
            # ADICIONANDO O NOVO ITEM AO ARQUIVO JSON
            with open('estoque.json', 'r+', encoding='utf-8') as arq:
                estoque = json.load(arq)
                estoque.append(item)

                arq.seek(0)
                json.dump(estoque, arq, indent=4, ensure_ascii=False)
                arq.truncate()

                print(f'Novo item cadastrado: {item["nome"]}')
                arq.close()

        else:
            # SALVANDO A ALTERAÇÃO DO ITEM
            with open('estoque.json', 'r+', encoding='utf-8') as arq:
                estoque = json.load(arq)
                estoque[ind] = item
                arq.seek(0)
                json.dump(estoque, arq, indent=4, ensure_ascii=False)
                arq.truncate()

                print(f'Cadastro alterado com sucesso!')
                arq.close()

        atualizarTabela()
        janela.destroy()

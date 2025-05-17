import json
import tkinter as tk
from tkinter import ttk


def inicio():
    global tabela

    root = tk.Toplevel()
    root.geometry('1500x500')
    root.title('ESTOQUE')
    # root.state('zoomed')

    frame_estoque = tk.Frame(root)
    frame_estoque.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame_estoque.tkraise()
    frame_estoque.configure(bg='grey')

    with open('estoque.json', 'r', encoding='utf-8') as arq:
        estoque = json.load(arq)
        arq.close()

    tk.Button(frame_estoque, text='Novo Item', command=novoItem).pack()

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

    tabela.pack()

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
    vendaEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
    custoEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
    lucroEntry = tk.Entry(janela, validate='key', validatecommand=numFloat)
    qtdEntry = tk.Entry(janela, validate='key', validatecommand=numInt)
    obsText = tk.Text(janela, height=10, width=50)

    tk.Label(janela, text='*Cód.:').pack()
    codEntry.pack()

    tk.Label(janela, text='*Nome:').pack()
    nomeEntry.pack()

    tk.Label(janela, text='*Venda:').pack()
    vendaEntry.pack()

    tk.Label(janela, text='*Custo:').pack()
    custoEntry.pack()

    tk.Label(janela, text='*Lucro:').pack()
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

def formNome(e, nome):
    fnome = nome.get().upper()

    nome.delete(0, tk.END)
    nome.insert(0, fnome)

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
        tabela.insert('', 'end', values=(
            produto['cod'],
            produto['nome'],
            produto['preco_venda'],
            produto['preco_custo'],
            produto['lucro'],
            produto['qtd'],
            produto['obs']
        ))

def salvar(janela, entry):
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
    for produto in estoque:

        # CASO TENHA CÓDIGO REPETIDO
        if produto['cod'] == item['cod']:
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

        # ADICIONANDO O NOVO ITEM AO ARQUIVO JSON
        with open('estoque.json', 'r+', encoding='utf-8') as arq:
            estoque = json.load(arq)
            estoque.append(item)

            arq.seek(0)
            json.dump(estoque, arq, indent=4, ensure_ascii=False)
            arq.truncate()

            print(f'Novo item cadastrado: {item["nome"]}')
            arq.close()

        atualizarTabela()

        janela.destroy()



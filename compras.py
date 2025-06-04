import tkinter as tk
from tkinter import ttk, messagebox
import json

def inicio():
    global root, listaCompras
    root = tk.Toplevel()
    root.geometry('1000x1000')
    root.state('zoomed')

    tk.Label(root, text='MÓDULO DE COMPRAS').pack()

    colunas = ['num_compra', 'fornecedor', 'total', 'data']
    listaCompras = ttk.Treeview(root, columns=colunas, show='headings')
    listaCompras.heading('num_compra', text='N°')
    listaCompras.heading('fornecedor', text='Fornecedor')
    listaCompras.heading('total', text='Valor Total')
    listaCompras.heading('data', text='Data')
    listaCompras.pack()

    atualizarCompras(listaCompras)
    listaCompras.bind('<Delete>', lambda event: excluirCompra(event, listaCompras))
    listaCompras.bind('<Double-1>', lambda event: abrirCompra(event, listaCompras))

    tk.Button(root, text='Nova Compra', command=novaCompra).pack()

def atualizarCompras(l):
    compras = receberCompras()

    for c in l.get_children():
        l.delete(c)

    for compra in compras:
        l.insert('', 'end', iid=compras.index(compra), values=(
            compra['num_compra'],
            compra['fornecedor'],
            compra['total'],
            compra['data']
        ))

def excluirCompra(e, l):
    compras = receberCompras()
    try:
        i = int(l.focus())
    except:
        return

    confirm = messagebox.askyesno('Excluir Compra',
                                  f'Tem certeza que deseja excluir a Compra N°{compras[i]["num_compra"]}?',
                                  parent=root)
    if confirm:
        try:
            compras.pop(i)

            with open('compras.json', 'w+', encoding='utf-8') as arq:
                json.dump(compras, arq)
                arq.close()
        except:
            messagebox.showerror('Erro', 'Erro ao excluir a compra', parent=root)
        atualizarCompras(l)

def abrirCompra(e, l):
    compras = receberCompras()
    try:
        i = int(l.focus())
    except:
        return

    compra = compras[i]

    janela = tk.Toplevel(root)
    janela.grab_set()
    janela.transient(root)
    janela.geometry('1050x700')

    tk.Label(janela, text=f'COMPRA N°{compra["num_compra"]}').pack()
    tk.Label(janela, text=f'Fornecedor: {compra["fornecedor"]}').pack()


def novaCompra():
    compras = receberCompras()
    itens = []
    if not compras:
        num_compra = 1
    else:
        num_compra = compras[-1]['num_compra'] + 1

    janela = tk.Toplevel(root)
    janela.grab_set()
    janela.transient(root)
    janela.geometry('1050x700')

    tk.Label(janela, text=f'COMPRA N°{num_compra}').pack()

    def atualizarLista():
        t = 0.0

        for i in lista.get_children():
            lista.delete(i)
        for item in itens:
            t += item['total']

            lista.insert('', 'end', iid=itens.index(item), values=(
                item['cod'],
                item['nome'],
                f'R$ {item["preco_custo"]:.2f}',
                item['qtd'],
                f'R$ {item["total"]:.2f}'
            ))

        total.configure(state='normal')
        total.delete(0, 'end')
        total.insert(0, f'{t:.2f}')
        total.configure(state='disabled')

    def verificarDados(entries):
        for entry in entries:
            if not entry.get():
                return True
        return False

    def verificarCod(entries):
        for item in itens:
            if int(entries[4].get()) == item['cod']:
                return True
        return False

    def confirmarItem(entries, janela, avulso):
        estoque = receberEstoque()

        flagDados = verificarDados(entries)

        if flagDados:
            messagebox.showerror('Dados inválidos', 'Preencha os dados corretamente!', parent=janela)

        else:
            if avulso:
                univ_cod = None
                cod = 'Avulso'
            else:
                flagCod = verificarCod(entries)
                if flagCod:
                    messagebox.showerror('Erro', 'Item já inserido na compra.', parent=janela)
                    return

                cod = int(entries[4].get())
                for produto in estoque:
                    if cod == produto['cod']:
                        univ_cod = produto['univ_cod']
                        break
                else:
                    univ_cod = None

            item = {
                'univ_cod': univ_cod,
                'cod': cod,
                'nome': entries[0].get(),
                'preco_custo': float(entries[1].get()),
                'qtd': float(entries[2].get()),
                'total': float(entries[3].get()),
            }

            itens.append(item)
            janela.destroy()
            atualizarLista()

    def atualizarTotalItem(e, valorEntry, qtdEntry, totalEntry):
        if valorEntry.get() and qtdEntry.get():
            vlr = float(valorEntry.get())
            qtd = float(qtdEntry.get())
            total = vlr * qtd
        else:
            total = 0.0

        totalEntry.configure(state='normal')
        totalEntry.delete(0, 'end')
        totalEntry.insert(0, f'{total:.2f}')
        totalEntry.configure(state='disabled')

    def addItemEstoque():
        janelaItem = tk.Toplevel(janela)
        janelaItem.title('Item Estoque')
        janelaItem.grab_set()
        janelaItem.transient(janela)
        janelaItem.geometry('400x300')

        tk.Label(janelaItem, text='Cód.').pack()
        codEntry = tk.Entry(janelaItem, validate='key', validatecommand=(janelaItem.register(entryNumInt), '%P'))
        codEntry.pack()

        tk.Label(janelaItem, text='Nome').pack()
        nomeEntry = tk.Entry(janelaItem)
        nomeEntry.configure(state='disabled')
        nomeEntry.pack()

        tk.Label(janelaItem, text='Valor Unit.').pack()
        valorEntry = tk.Entry(janelaItem, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'))
        valorEntry.pack()

        tk.Label(janelaItem, text='Qtd.').pack()
        qtdEntry = tk.Entry(janelaItem, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'))
        qtdEntry.insert(0, '1')
        qtdEntry.pack()

        tk.Label(janelaItem, text='Valor Total').pack()
        totalEntry = tk.Entry(janelaItem)
        totalEntry.insert(0, '0.00')
        totalEntry.configure(state='disabled')
        totalEntry.pack()

        tk.Label(janelaItem, text='Disponível').pack()
        disponivelEntry = tk.Entry(janelaItem)
        disponivelEntry.configure(state='disabled')
        disponivelEntry.pack()

        entries = [nomeEntry, valorEntry, qtdEntry, totalEntry, codEntry]

        tk.Button(janelaItem, text='Confirmar', command=lambda: confirmarItem(entries, janelaItem, False)).pack()

        def itemPorCod(e):
            estoque = receberEstoque()
            cod = codEntry.get()

            for item in estoque:
                if cod == str(item['cod']):
                    nomeEntry.configure(state='normal')
                    nomeEntry.delete(0, 'end')
                    nomeEntry.insert(0, item['nome'])
                    nomeEntry.configure(state='disabled')

                    valorEntry.delete(0, 'end')
                    valorEntry.insert(0, f"{item['preco_custo']:.2f}")

                    disponivelEntry.configure(state='normal')
                    disponivelEntry.delete(0, 'end')
                    disponivelEntry.insert(0, item['qtd'])
                    disponivelEntry.configure(state='disabled')
                    break
            else:
                nomeEntry.configure(state='normal')
                nomeEntry.delete(0, 'end')
                nomeEntry.insert(0, '')
                nomeEntry.configure(state='disabled')

                valorEntry.delete(0, 'end')
                valorEntry.insert(0, '')

                disponivelEntry.configure(state='normal')
                disponivelEntry.delete(0, 'end')
                disponivelEntry.insert(0, '')
                disponivelEntry.configure(state='disabled')

        codEntry.bind('<KeyRelease>', itemPorCod)
        codEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry), add='+')
        valorEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))
        qtdEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))

    def addItemAvulso():
        janelaItem = tk.Toplevel(janela)
        janelaItem.title('Item Avulso')
        janelaItem.grab_set()
        janelaItem.transient(janela)
        janelaItem.geometry('400x300')

        tk.Label(janelaItem, text='Nome').pack()
        nomeEntry = tk.Entry(janelaItem)
        nomeEntry.pack()

        tk.Label(janelaItem, text='Valor Unit.').pack()
        valorEntry = tk.Entry(janelaItem, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'))
        valorEntry.pack()

        tk.Label(janelaItem, text='Qtd.').pack()
        qtdEntry = tk.Entry(janelaItem, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'))
        qtdEntry.insert(0, '1')
        qtdEntry.pack()

        tk.Label(janelaItem, text='Valor Total').pack()
        totalEntry = tk.Entry(janelaItem)
        totalEntry.insert(0, '0.00')
        totalEntry.configure(state='disabled')
        totalEntry.pack()

        entries = [nomeEntry, valorEntry, qtdEntry, totalEntry]
        valorEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))
        qtdEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))

        tk.Button(janelaItem, text='Confirmar', command=lambda: confirmarItem(entries, janelaItem, True)).pack()

    def excluirItem(e):
        try:
            i = int(lista.focus())
        except:
            return
        confirm = messagebox.askyesno('Excluir Item',
                                      f'Tem certeza que deseja excluir o item {itens[i]["nome"]}?', parent=janela)
        if confirm:
            itens.pop(i)
            atualizarLista()

    tk.Label(janela, text='Fornecedor:').pack()
    fornecedor = tk.Entry(janela)
    fornecedor.pack()

    colunas = ['cod', 'nome', 'valor', 'qtd', 'total']
    lista = ttk.Treeview(janela, columns=colunas, show='headings')
    lista.heading('cod', text='Cód.')
    lista.heading('nome', text='Produto')
    lista.heading('valor', text='Valor Unit.')
    lista.heading('qtd', text='Qtd.')
    lista.heading('total', text='Total')
    lista.pack()

    tk.Label(janela, text='Valor da Compra: R$').pack()
    total = tk.Entry(janela)
    total.insert(0, '0.00')
    total.pack()
    total.configure(state='disabled')

    tk.Button(janela, text='Adicionar Item\ndo Estoque', command=addItemEstoque).pack()
    tk.Button(janela, text='Adicionar Item\nAvulso', command=addItemAvulso).pack()

    def cancelar():
        confirm = messagebox.askyesno('Confirmar',
                                      'Tem certeza que deseja cancelar essa compra?',
                                      parent=janela)
        if confirm:
            janela.destroy()

    def finalizar():
        try:
            valorTotal = float(total.get())
        except:
            valorTotal = 0.0

        if not itens:
            messagebox.showerror('Error', 'Nenhum produto inserido!', parent=janela)

        elif fornecedor.get() == '':
            messagebox.showerror('Error', 'Insira o nome do fornecedor', parent=janela)

        else:
            if valorTotal == 0:
                messagebox.showinfo('Finalizar compra',
                                    'Valor total zerado, '
                                    'finalizando compra sem forma de pagamento!', parent=janela)
            else:
                janelapag = tk.Toplevel(janela)
                janelapag.title('Forma de pagamento')
                janelapag.grab_set()
                janelapag.transient(janela)
                janelapag.geometry('400x300')

                tk.Label(janelapag, text="Selecione a forma de pagamento:", font=('Arial', 12)).pack(pady=10)

                forma_pagamento = tk.StringVar(value="1")  # valor padrão

                # Radiobuttons de pagamento
                tk.Radiobutton(janelapag, text="Á vista", variable=forma_pagamento, value="1").pack()
                tk.Radiobutton(janelapag, text="Fiado", variable=forma_pagamento, value="2").pack()
                tk.Radiobutton(janelapag, text="Parcelado", variable=forma_pagamento, value="3").pack()

                def confirmar_pagamento():
                    global listaCompras

                    compras = receberCompras()
                    estoque = receberEstoque()

                    forma = forma_pagamento.get()
                    if forma == '1':
                        pagamento = 'À vista'
                    elif forma == '2':
                        pagamento = 'Fiado'
                    else:
                        pagamento = 'Parcelado'

                    compra = {
                        'num_compra': num_compra,
                        'itens': itens,
                        'fornecedor': fornecedor.get(),
                        'total': valorTotal,
                        'data': None,
                        'pagamento': pagamento
                    }

                    for item in itens:
                        for produto in estoque:
                            if item['univ_cod'] == produto['univ_cod']:
                                produto['qtd'] += item['qtd']
                                produto['preco_custo'] = item['preco_custo']

                                if produto['preco_venda'] == 0:
                                    produto['lucro'] = 0.0
                                elif produto['preco_custo'] == 0:
                                    produto['lucro'] = 100.0
                                else:
                                    produto['lucro'] = ((produto['preco_venda'] - produto['preco_custo']) / produto['preco_custo'])*100

                                break

                    with open('estoque.json', 'w+', encoding='utf-8') as arq:
                        json.dump(estoque, arq, indent=4, ensure_ascii=False)
                        arq.close()

                    with open('compras.json', 'w+', encoding='utf-8') as arq:
                        compras.append(compra)
                        json.dump(compras, arq, indent=4, ensure_ascii=False)
                        arq.close()

                    atualizarCompras(listaCompras)
                    janela.destroy()


                tk.Button(janelapag, text="Confirmar", command=confirmar_pagamento).pack()

    lista.bind('<Delete>', excluirItem)

    tk.Button(janela, text='Finalizar Compra', command=finalizar).pack()
    tk.Button(janela, text='Cancelar', command=cancelar).pack()

    atualizarLista()

def receberCompras():
    with open('compras.json', 'r', encoding='utf-8') as arq:
        return json.load(arq)

def receberEstoque():
    with open('estoque.json', 'r', encoding='utf-8') as arq:
        return json.load(arq)

def entryNumFloat(n):
    # Valida se a entrada é um número decimal
    if n == '':
        return True
    try:
        float(n)
        return True
    except:
        return False

def entryNumInt(n):
    # Valida se a entrada é um número inteiro
    if n == '':
        return True
    try:
        int(n)
        return True
    except:
        return False

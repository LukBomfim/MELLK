import tkinter as tk
from tkinter import ttk, messagebox
import json
import datetime

# Estilo global para botões
button_style = {
    'font': ('Arial', 11),
    'bg': '#FFFFFF',
    'fg': '#000000',
    'activebackground': '#E5E5E5',
    'activeforeground': '#000000',
    'width': 15,
    'height': 2,
    'borderwidth': 1,
    'cursor': 'hand2',
    'relief': 'flat'
}

def inicio():
    root = tk.Toplevel()
    root.geometry('1000x1000')
    root.state('zoomed')
    root.configure(bg='#1A3C34')

    # Frame principal
    frame_principal = tk.Frame(root, bg='#1A3C34')
    frame_principal.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Cabeçalho
    header_frame = tk.Frame(frame_principal, bg='#1A3C34')
    header_frame.pack(pady=20)
    tk.Label(header_frame, text="MÓDULO DE COMPRAS", font=('Arial', 16, 'bold'), fg='white', bg='#1A3C34').pack()

    # Frame da tabela
    table_frame = tk.Frame(frame_principal, bg='#1A3C34')
    table_frame.pack(fill='both', expand=True, padx=20, pady=10)

    colunas = ['num_compra', 'fornecedor', 'total', 'data']
    listaCompras = ttk.Treeview(table_frame, columns=colunas, show='headings', height=20)
    listaCompras.heading('num_compra', text='N°')
    listaCompras.heading('fornecedor', text='Fornecedor')
    listaCompras.heading('total', text='Valor Total')
    listaCompras.heading('data', text='Data')
    listaCompras.column('num_compra', width=100)
    listaCompras.column('fornecedor', width=400)
    listaCompras.column('total', width=150)
    listaCompras.column('data', width=150)
    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=listaCompras.yview)
    listaCompras.configure(yscrollcommand=scrollbar.set)
    listaCompras.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    atualizarCompras(listaCompras)
    listaCompras.bind('<Delete>', lambda event: excluirCompra(event, listaCompras))
    listaCompras.bind('<Double-1>', lambda event: abrirCompra(event, listaCompras))

    # Botões
    button_frame = tk.Frame(frame_principal, bg='#1A3C34')
    button_frame.pack(pady=20)
    tk.Button(button_frame, text='Nova Compra', command=lambda: novaCompra(listaCompras), **button_style).pack()

    return root

def atualizarCompras(l):
    compras = receberCompras()

    for c in l.get_children():
        l.delete(c)

    for compra in compras:
        l.insert('', 'end', iid=compras.index(compra), values=(
            compra['num_compra'],
            compra['fornecedor'],
            f"R$ {compra['total']:.2f}" if compra['total'] else "R$ 0.00",
            compra['data'] if compra['data'] else 'N/A'
        ))

def excluirCompra(e, l):
    compras = receberCompras()
    try:
        i = int(l.focus())
    except:
        return

    confirm = messagebox.askyesno('Excluir Compra',
                                  f'Tem certeza que deseja excluir a Compra N°{compras[i]["num_compra"]}?',
                                  parent=l.winfo_toplevel())
    if confirm:
        try:
            compras.pop(i)
            with open('compras.json', 'w', encoding='utf-8') as arq:
                json.dump(compras, arq, indent=4, ensure_ascii=False)
            atualizarCompras(l)
        except Exception as ex:
            messagebox.showerror('Erro', f'Erro ao excluir a compra: {str(ex)}', parent=l.winfo_toplevel())

def abrirCompra(e, l):
    compras = receberCompras()
    try:
        i = int(l.focus())
    except:
        return

    compra = compras[i]

    janela = tk.Toplevel(l.winfo_toplevel())
    janela.grab_set()
    janela.transient(l.winfo_toplevel())
    janela.configure(bg='#1A3C34')
    janela.title(f'Compra N°{compra["num_compra"]}')

    largura_tela = l.winfo_screenwidth()
    altura_tela = l.winfo_screenheight()
    pos_x = (largura_tela - 1050) // 2
    pos_y = (altura_tela - 700) // 2
    janela.geometry(f'1050x700+{pos_x}+{pos_y}')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    fonte_bold = ('Arial', 14, 'bold')

    header_frame = tk.Frame(frame, bg='#1A3C34')
    header_frame.pack(pady=10, fill='x')
    tk.Label(header_frame, text=f'COMPRA N°{compra["num_compra"]}', font=fonte_bold, fg='white', bg='#1A3C34').pack()
    tk.Label(header_frame, text=f'Fornecedor: {compra["fornecedor"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w', padx=20)

    # Tabela de itens
    table_frame = tk.Frame(frame, bg='#1A3C34')
    table_frame.pack(fill='both', expand=True, padx=20, pady=10)

    colunas = ['cod', 'nome', 'preco_custo', 'qtd', 'total']
    tabela = ttk.Treeview(table_frame, columns=colunas, show='headings', height=15)
    tabela.heading('cod', text='Cód.')
    tabela.heading('nome', text='Produto')
    tabela.heading('preco_custo', text='Valor Unit.')
    tabela.heading('qtd', text='Qtd.')
    tabela.heading('total', text='Total')
    tabela.column('cod', width=100)
    tabela.column('nome', width=300)
    tabela.column('preco_custo', width=150)
    tabela.column('qtd', width=100)
    tabela.column('total', width=150)
    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    tabela.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    for item in compra['itens']:
        tabela.insert('', 'end', values=(
            item['cod'],
            item['nome'],
            f'R${item["preco_custo"]:.2f}',
            f'{item["qtd"]:.2f}',
            f'R${item["total"]:.2f}'
        ))

    # Informações adicionais
    info_frame = tk.Frame(frame, bg='#1A3C34')
    info_frame.pack(fill='x', padx=20, pady=10)
    tk.Label(info_frame, text=f'Total: R${compra["total"]:.2f}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')
    tk.Label(info_frame, text=f'Data: {compra["data"] if compra["data"] else "N/A"}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')
    tk.Label(info_frame, text=f'Pagamento: {compra["pagamento"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Fechar', command=janela.destroy, **button_style).pack()

def novaCompra(listaCompras):
    compras = receberCompras()
    itens = []
    num_compra = 1 if not compras else compras[-1]['num_compra'] + 1

    janela = tk.Toplevel(listaCompras.winfo_toplevel())
    janela.grab_set()
    janela.transient(listaCompras.winfo_toplevel())
    janela.configure(bg='#1A3C34')
    janela.title(f'Nova Compra N°{num_compra}')

    largura_tela = listaCompras.winfo_screenwidth()
    altura_tela = listaCompras.winfo_screenheight()
    pos_x = (largura_tela - 1050) // 2
    pos_y = (altura_tela - 700) // 2
    janela.geometry(f'1050x700+{pos_x}+{pos_y}')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    fonte_bold = ('Arial', 14, 'bold')

    header_frame = tk.Frame(frame, bg='#1A3C34')
    header_frame.pack(pady=10, fill='x')
    tk.Label(header_frame, text=f'COMPRA N°{num_compra}', font=fonte_bold, fg='white', bg='#1A3C34').pack()

    fornecedor_frame = tk.Frame(frame, bg='#1A3C34')
    fornecedor_frame.pack(fill='x', padx=20, pady=10)
    tk.Label(fornecedor_frame, text='Fornecedor:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    fornecedor = tk.Entry(fornecedor_frame, font=fonte, width=50, bg='#E5E5E5', fg='#000000', insertbackground='#000000')
    fornecedor.pack(side=tk.LEFT, padx=5)

    table_frame = tk.Frame(frame, bg='#1A3C34')
    table_frame.pack(fill='both', expand=True, padx=20, pady=10)

    colunas = ['cod', 'nome', 'valor', 'qtd', 'total']
    lista = ttk.Treeview(table_frame, columns=colunas, show='headings', height=15)
    lista.heading('cod', text='Cód.')
    lista.heading('nome', text='Produto')
    lista.heading('valor', text='Valor Unit.')
    lista.heading('qtd', text='Qtd.')
    lista.heading('total', text='Total')
    lista.column('cod', width=100)
    lista.column('nome', width=300)
    lista.column('valor', width=150)
    lista.column('qtd', width=100)
    lista.column('total', width=150)
    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=lista.yview)
    lista.configure(yscrollcommand=scrollbar.set)
    lista.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    total_frame = tk.Frame(frame, bg='#1A3C34')
    total_frame.pack(fill='x', padx=20, pady=10)
    tk.Label(total_frame, text='Valor da Compra: R$', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    total = tk.Entry(total_frame, font=fonte, width=15, state='disabled', disabledbackground='#E5E5E5')
    total.insert(0, '0.00')
    total.pack(side=tk.LEFT, padx=5)

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Adicionar Item do Estoque', command=lambda: addItemEstoque(lista, total, itens, janela), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Adicionar Item Avulso', command=lambda: addItemAvulso(lista, total, itens, janela), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Finalizar Compra', command=lambda: finalizar(lista, total, fornecedor, itens, num_compra, listaCompras, janela), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar', command=lambda: cancelar(janela), **button_style).pack(side=tk.LEFT, padx=5)

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
                f'{item["qtd"]:.2f}',
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

    def verificarCod(entries, itens):
        for item in itens:
            if entries[-1].get() and int(entries[-1].get()) == item['cod']:
                return True
        return False

    def confirmarItem(entries, janelaItem, avulso, lista, total, itens):
        estoque = receberEstoque()
        flagDados = verificarDados(entries[:-1] if avulso else entries)
        if flagDados:
            messagebox.showerror('Dados inválidos', 'Preencha os dados corretamente!', parent=janelaItem)
            return

        if avulso:
            univ_cod = None
            cod = 'Avulso'
        else:
            flagCod = verificarCod(entries, itens)
            if flagCod:
                messagebox.showerror('Erro', 'Item já inserido na compra.', parent=janelaItem)
                return
            cod = int(entries[-1].get())
            for produto in estoque:
                if cod == produto['cod']:
                    univ_cod = produto.get('univ_cod')
                    break
            else:
                messagebox.showerror('Erro', 'Código não encontrado no estoque.', parent=janelaItem)
                return

        item = {
            'univ_cod': univ_cod,
            'cod': cod,
            'nome': entries[0].get(),
            'preco_custo': float(entries[1].get()),
            'qtd': float(entries[2].get()),
            'total': float(entries[3].get()),
        }
        itens.append(item)
        janelaItem.destroy()
        atualizarLista()

    def atualizarTotalItem(e, valorEntry, qtdEntry, totalEntry):
        if valorEntry.get() and qtdEntry.get():
            try:
                vlr = float(valorEntry.get())
                qtd = float(qtdEntry.get())
                total = vlr * qtd
            except ValueError:
                total = 0.0
        else:
            total = 0.0
        totalEntry.configure(state='normal')
        totalEntry.delete(0, 'end')
        totalEntry.insert(0, f'{total:.2f}')
        totalEntry.configure(state='disabled')

    def addItemEstoque(lista, total, itens, janela):
        janelaItem = tk.Toplevel(janela)
        janelaItem.title('Adicionar Item do Estoque')
        janelaItem.grab_set()
        janelaItem.transient(janela)
        janelaItem.configure(bg='#1A3C34')

        pos_x = (largura_tela - 400) // 2
        pos_y = (altura_tela - 400) // 2
        janelaItem.geometry(f'400x400+{pos_x}+{pos_y}')

        frame_item = tk.Frame(janelaItem, bg='#1A3C34')
        frame_item.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(frame_item, text='Cód.', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        codEntry = tk.Entry(frame_item, font=fonte, width=20, validate='key', validatecommand=(janelaItem.register(entryNumInt), '%P'), bg='#E5E5E5', fg='#000000', insertbackground='#000000')
        codEntry.pack(pady=2)

        tk.Label(frame_item, text='Nome', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        nomeEntry = tk.Entry(frame_item, font=fonte, width=20, state='disabled', disabledbackground='#E5E5E5')
        nomeEntry.pack(pady=2)

        tk.Label(frame_item, text='Valor Unit.', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        valorEntry = tk.Entry(frame_item, font=fonte, width=20, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'), bg='#E5E5E5', fg='#000000', insertbackground='#000000')
        valorEntry.pack(pady=2)

        tk.Label(frame_item, text='Qtd.', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        qtdEntry = tk.Entry(frame_item, font=fonte, width=20, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'), bg='#E5E5E5', fg='#000000', insertbackground='#000000')
        qtdEntry.insert(0, '1.00')
        qtdEntry.pack(pady=2)

        tk.Label(frame_item, text='Valor Total', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        totalEntry = tk.Entry(frame_item, font=fonte, width=20, state='disabled', disabledbackground='#E5E5E5')
        totalEntry.insert(0, '0.00')
        totalEntry.pack(pady=2)

        tk.Label(frame_item, text='Disponível', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        disponivelEntry = tk.Entry(frame_item, font=fonte, width=20, state='disabled', disabledbackground='#E5E5E5')
        disponivelEntry.pack(pady=2)

        entries = [nomeEntry, valorEntry, qtdEntry, totalEntry, codEntry]

        button_frame = tk.Frame(frame_item, bg='#1A3C34')
        button_frame.pack(pady=10)
        tk.Button(button_frame, text='Confirmar', command=lambda: confirmarItem(entries, janelaItem, False, lista, total, itens), **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text='Cancelar', command=janelaItem.destroy, **button_style).pack(side=tk.LEFT, padx=5)

        def itemPorCod():
            estoque = receberEstoque()
            cod = codEntry.get()
            for item in estoque:
                if cod == str(item['cod']):
                    nomeEntry.configure(state='normal')
                    nomeEntry.delete(0, tk.END)
                    nomeEntry.insert(0, item['nome'])
                    nomeEntry.configure(state='disabled')
                    valorEntry.delete(0, tk.END)
                    valorEntry.insert(0, f"{item['preco_custo']:.2f}")
                    disponivelEntry.configure(state='normal')
                    disponivelEntry.delete(0, tk.END)
                    disponivelEntry.insert(0, f"{item['qtd']:.2f}")
                    disponivelEntry.configure(state='disabled')
                    break
            else:
                nomeEntry.configure(state='normal')
                nomeEntry.delete(0, tk.END)
                nomeEntry.configure(state='disabled')
                valorEntry.delete(0, tk.END)
                disponivelEntry.configure(state='normal')
                disponivelEntry.delete(0, tk.END)
                disponivelEntry.configure(state='disabled')

        codEntry.bind('<KeyRelease>', lambda event: itemPorCod())
        codEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry), add='+')
        valorEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))
        qtdEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))

    def addItemAvulso(lista, total, itens, janela):
        janelaItem = tk.Toplevel(janela)
        janelaItem.title('Adicionar Item Avulso')
        janelaItem.grab_set()
        janelaItem.transient(janela)
        janelaItem.configure(bg='#1A3C34')

        pos_x = (largura_tela - 400) // 2
        pos_y = (altura_tela - 350) // 2
        janelaItem.geometry(f'400x350+{pos_x}+{pos_y}')

        frame_item = tk.Frame(janelaItem, bg='#1A3C34')
        frame_item.place(relx=0, rely=0, relwidth=1, relheight=1)

        tk.Label(frame_item, text='Nome', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        nomeEntry = tk.Entry(frame_item, font=fonte, width=25, bg='#E5E5E5', fg='#000000', insertbackground='#000000')
        nomeEntry.pack(pady=2)

        tk.Label(frame_item, text='Valor Unit.', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        valorEntry = tk.Entry(frame_item, font=fonte, width=15, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'), bg='#E5E5E5', fg='#000000', insertbackground='#000000')
        valorEntry.pack(pady=2)

        tk.Label(frame_item, text='Qtd.', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        qtdEntry = tk.Entry(frame_item, font=fonte, width=15, validate='key', validatecommand=(janelaItem.register(entryNumFloat), '%P'), bg='#E5E5E5', fg='#000000', insertbackground='#000000')
        qtdEntry.insert(0, '1.00')
        qtdEntry.pack(pady=2)

        tk.Label(frame_item, text='Valor Total', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        totalEntry = tk.Entry(frame_item, font=fonte, width=15, state='disabled', disabledbackground='#E5E5E5')
        totalEntry.insert(0, '0.00')
        totalEntry.pack(pady=2)

        entries = [nomeEntry, valorEntry, qtdEntry, totalEntry]

        button_frame = tk.Frame(frame_item, bg='#1A3C34')
        button_frame.pack(pady=10)
        tk.Button(button_frame, text='Confirmar', command=lambda: confirmarItem(entries, janelaItem, True, lista, total, itens), **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text='Cancelar', command=janelaItem.destroy, **button_style).pack(side=tk.LEFT, padx=5)

        valorEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))
        qtdEntry.bind('<KeyRelease>', lambda event: atualizarTotalItem(event, valorEntry, qtdEntry, totalEntry))

    def excluirItem(e, itens, lista, total):
        try:
            i = int(lista.focus())
        except:
            return
        confirm = messagebox.askyesno('Excluir Item',
                                      f'Tem certeza que deseja excluir o item {itens[i]["nome"]}?', parent=janela)
        if confirm:
            itens.pop(i)
            atualizarLista()

    def cancelar(janela):
        confirm = messagebox.askyesno('Confirmar',
                                      'Tem certeza que deseja cancelar essa compra?',
                                      parent=janela)
        if confirm:
            janela.destroy()

    def finalizar(lista, total, fornecedor, itens, num_compra, listaCompras, janela):
        try:
            valorTotal = float(total.get())
        except:
            valorTotal = 0.0

        if not itens:
            messagebox.showerror('Erro', 'Nenhum produto inserido.', parent=janela)
            return
        elif not fornecedor.get():
            messagebox.showerror('Erro', 'Insira o nome do fornecedor.', parent=janela)
            return

        if valorTotal == 0:
            messagebox.showinfo('Finalizar compra',
                                'Valor total zerado, finalizando compra sem forma de pagamento!', parent=janela)
            confirmar_pagamento('Nenhum', lista, total, fornecedor, itens, num_compra, listaCompras, janela)
        else:
            janelapag = tk.Toplevel(janela)
            janelapag.title('Forma de Pagamento')
            janelapag.grab_set()
            janelapag.transient(janela)
            janelapag.configure(bg='#1A3C34')

            pos_x = (largura_tela - 400) // 2
            pos_y = (altura_tela - 300) // 2
            janelapag.geometry(f'400x300+{pos_x}+{pos_y}')

            frame_pag = tk.Frame(janelapag, bg='#1A3C34')
            frame_pag.place(relx=0, rely=0, relwidth=1, relheight=1)

            tk.Label(frame_pag, text="Selecione a forma de pagamento:", font=fonte_bold, fg='white', bg='#1A3C34').pack(pady=20)

            forma_pagamento = tk.StringVar(value="1")
            tk.Radiobutton(frame_pag, text="À vista", variable=forma_pagamento, value="1", font=fonte, fg='white', bg='#1A3C34', selectcolor='#3b3b3b').pack(anchor='w', padx=20, pady=5)
            tk.Radiobutton(frame_pag, text="Fiado", variable=forma_pagamento, value="2", font=fonte, fg='white', bg='#1A3C34', selectcolor='#3b3b3b').pack(anchor='w', padx=20, pady=5)
            tk.Radiobutton(frame_pag, text="Parcelado", variable=forma_pagamento, value="3", font=fonte, fg='white', bg='#1A3C34', selectcolor='#3b3b3b').pack(anchor='w', padx=20, pady=5)

            button_frame = tk.Frame(frame_pag, bg='#1A3C34')
            button_frame.pack(pady=20)
            tk.Button(button_frame, text="Confirmar", command=lambda: confirmar_pagamento(forma_pagamento.get(), lista, total, fornecedor, itens, num_compra, listaCompras, janelapag), **button_style).pack()

    def confirmar_pagamento(forma_pagamento, lista, total, fornecedor, itens, num_compra, listaCompras, janelapag):
        compras = receberCompras()
        estoque = receberEstoque()

        if forma_pagamento == '1':
            pagamento = 'À vista'
        elif forma_pagamento == '2':
            pagamento = 'Fiado'
        elif forma_pagamento == '3':
            pagamento = 'Parcelado'
        else:
            pagamento = 'Nenhum'

        compra = {
            'num_compra': num_compra,
            'itens': itens,
            'fornecedor': fornecedor.get(),
            'total': float(total.get()),
            'data': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'pagamento': pagamento
        }

        for item in itens:
            for produto in estoque:
                if item.get('univ_cod') == produto.get('univ_cod'):
                    produto['qtd'] = float(produto.get('qtd', 0)) + item['qtd']
                    produto['preco_custo'] = item['preco_custo']
                    if produto['preco_custo'] == 0:
                        produto['lucro'] = 0.0
                    else:
                        produto['lucro'] = ((produto.get('preco_venda', 0) - produto['preco_custo']) / produto['preco_custo']) * 100
                    break

        try:
            with open('estoque.json', 'w', encoding='utf-8') as arq:
                json.dump(estoque, arq, indent=4, ensure_ascii=False)

            compras.append(compra)
            with open('compras.json', 'w', encoding='utf-8') as arq:
                json.dump(compras, arq, indent=4, ensure_ascii=False)

            atualizarCompras(listaCompras)
            janelapag.destroy()
            lista.winfo_toplevel().destroy()
        except Exception as ex:
            messagebox.showerror('Erro', f'Erro ao salvar a compra: {str(ex)}', parent=janelapag)

    lista.bind('<Delete>', lambda e: excluirItem(e, itens, lista, total))
    atualizarLista()

def receberCompras():
    try:
        with open('compras.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def receberEstoque():
    try:
        with open('estoque.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def entryNumFloat(n):
    if n == '':
        return True
    try:
        float(n)
        return True
    except:
        return False

def entryNumInt(n):
    if n == '':
        return True
    try:
        int(n)
        return True
    except:
        return False

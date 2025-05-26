import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
import json, os

def inicio():
    global root, frameInicial

    root = tk.Toplevel()
    root.geometry('1000x500')
    root.title('VENDAS')
    root.state('zoomed')

                # FRAME INICIAL DO MÓDULO VENDAS
    frameInicial = tk.Frame(root)
    frameInicial.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Button(frameInicial, text='Nova Venda Direta', command=vendaDireta).pack()
    tk.Button(frameInicial, text='Novo Pedido', command=vendaPedido).pack()
    tk.Button(frameInicial, text='Novo Orçamento', command=orcamento).pack()

    root.mainloop()

def receberEstoque():
    with open('estoque.json', 'r', encoding='utf-8') as arq:
        estoque = json.load(arq)
        arq.close()
    return estoque

def receberClientes():
    with open('clientes.json', 'r', encoding='utf-8') as arq:
        clientes = json.load(arq)
        arq.close()
    return clientes

def vendaDireta():
    global cliente

    cliente = {
        "cod": None,
        "nome": "CLIENTE NÃO IDENTIFICADO",
        "telefone": "",
        "cpf_cnpj": "",
        "cep": "",
        "num_casa": "",
        "email": ""
    }

    venda()

def vendaPedido():
    global cliente
    cliente = {}

    janela = tk.Toplevel(root)
    janela.transient(root)
    janela.grab_set()
    janela.title('Busca de Cliente')
    janela.geometry('900x400')

    tk.Label(janela, text='Pesquisa por:').pack()
    opc = ttk.Combobox(janela, values=['Nome', 'Telefone', 'CPF/CNPJ'], state='readonly')
    opc.set('Nome')
    opc.pack()

    pesquisa = tk.Entry(janela)
    pesquisa.pack()

    dados = ['cod', 'nome', 'telefone', 'cpf_cnpj']
    lista = ttk.Treeview(janela, columns=dados, show='headings')
    lista.heading(dados[0], text='Cód.')
    lista.heading(dados[1], text='Nome')
    lista.heading(dados[2], text='Telefone')
    lista.heading(dados[3], text='CPF/CNPJ')

    tk.Button(janela, text='Procurar', command=lambda: buscaCliente(janela, opc, pesquisa, lista)).pack()
    janela.bind('<Return>', lambda event: buscaCliente(janela, opc, pesquisa, lista, event))
    lista.pack()
    lista.bind('<Double-1>', lambda event: selecionarClienteVenda(event, janela, lista))

def buscaCliente(j, cb, pe, l, e=None):
    clientes = receberClientes()

    opc = cb.get()
    pesq = pe.get()

    resultado = []

    if opc == 'Nome':
        if not pesq == '':
            for result in clientes:
                if pesq.upper() in result['nome']:
                    c = {
                        'cod': result['cod'],
                        'nome': result['nome'],
                        'telefone': result['telefone'],
                        'cpf_cnpj': result['cpf_cnpj'],
                    }
                    resultado.append(c)

    elif opc == 'Telefone':

        p = ''
        for n in pesq:
            if n.isnumeric():
                p += n

        if not p == '':
            for result in clientes:

                tel = ''
                for n in result['telefone']: # FILTRANDO APENAS OS NÚMEROS
                    if n.isnumeric():
                        tel += n

                if p in tel:
                    c = {
                        'cod': result['cod'],
                        'nome': result['nome'],
                        'telefone': result['telefone'],
                        'cpf_cnpj': result['cpf_cnpj']
                    }
                    resultado.append(c)

    elif opc == 'CPF/CNPJ':

        p = ''
        for n in pesq:
            if n.isnumeric():
                p += n

        if not p == '':
            for result in clientes:

                cpf = ''
                for n in result['cpf_cnpj']: # FILTRANDO APENAS OS NÚMEROS
                    if n.isnumeric():
                        cpf += n

                if p in cpf:
                    c = {
                        'cod': result['cod'],
                        'nome': result['nome'],
                        'telefone': result['telefone'],
                        'cpf_cnpj': result['cpf_cnpj']
                    }
                    resultado.append(c)

    for r in l.get_children():
        l.delete(r)

    for r in resultado:
        l.insert('', 'end', iid=r['cod'], values=(
            r['cod'],
            r['nome'],
            r['telefone'],
            r['cpf_cnpj'],
        ))

def selecionarClienteVenda(e, j, l):
    global cliente

    clientes = receberClientes()

    try:
        codCliente = int(l.focus())
        for c in clientes:
            if c['cod'] == codCliente:
                cliente = c
                j.destroy()
                venda()
                break
    except:
        return

def venda():
    global num_venda, itens, itensLista, valorTotal, valorTotalLabel

    itens = []
    valorTotal = 0.0

    with open('vendas.json', 'r', encoding='utf-8') as arq:
        vendas = json.load(arq)
        arq.close()

    if not vendas:
        num_venda = 1
    else:
        num_venda = len(vendas)+1

    root.geometry('1000x700')
    frame = tk.Frame(root)
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)
    frame.config(bg='grey')

    fonte = ('Arial', 14)

                    # DADOS DO CLIENTE
    tk.Label(frame, text=f'VENDA N°{num_venda}', font=fonte).pack()
    tk.Label(frame, text=f'Cliente: {cliente["nome"]}', font=fonte).pack()
    tk.Label(frame, text=f'Telefone: {cliente["telefone"]}', font=fonte).pack()
    tk.Label(frame, text=f'CPF/CNPJ: {cliente["cpf_cnpj"]}', font=fonte).pack()
    tk.Label(frame, text=f'CEP: {cliente["cep"]}', font=fonte).pack()
    tk.Label(frame, text=f'N°: {cliente["num_casa"]}', font=fonte).pack()
    tk.Label(frame, text=f'E-mail: {cliente["email"]}', font=fonte).pack()

                    # VALOR DA VENDA
    tk.Label(frame, text=f'Valor Total: ', font=fonte).pack()
    valorTotalLabel = tk.Label(frame, text=f'R$ {valorTotal:.2f}', font=fonte)
    valorTotalLabel.pack()

                    # ITENS NO CARRINHO
    colunas = ['cod', 'nome', 'preco_venda', 'qtd', 'total']
    itensLista = ttk.Treeview(frame, columns=colunas, show='headings')
    itensLista.heading('cod', text='Código')
    itensLista.heading('nome', text='Nome')
    itensLista.heading('preco_venda', text='Valor Unit.')
    itensLista.heading('qtd', text='Qtd')
    itensLista.heading('total', text='Total')

                    # BOTÕES
    tk.Button(frame, text='Adicionar Item\ndo Estoque', command=itemEstoque).pack()
    tk.Button(frame, text='Adicionar Item\nAvulso', command=itemAvulso).pack()
    tk.Button(frame, text='Excluir Item', command= lambda: excluirItem(itensLista, frame)).pack()
    itensLista.bind('<Delete>', lambda event: excluirItem(itensLista, frame))

    itensLista.pack()

    venda = [num_venda, cliente, itens]

    tk.Button(frame, text='Cancelar Venda', command= lambda: cancelarVenda(frame)).pack()
    tk.Button(frame, text='Finalizar Venda', command= lambda: finalizarVenda(venda)).pack()

def finalizarVenda(inf_vendas):
    num_venda = int(inf_vendas[0])
    cliente = inf_vendas[1]
    itens = inf_vendas[2]
    total = 0

    if not itens:
        messagebox.showerror('Erro', 'Nenhum item adicionado', parent=root)

    else:
        for item in inf_vendas[2]:
            total += item['total']

        pagamentos={
            'Dinheiro': 0.0,
            'Pix': [],
            'Credito': [],
            'Debito': [],
        }

        venda = {
            'num_venda': num_venda,
            'cliente': cliente,
            'itens': itens,
            'total': total,
            'pagamento': pagamentos
        }

        janela = tk.Toplevel(root)
        janela.transient(root)
        janela.geometry('600x700')

        tk.Button(janela, text='Voltar', command=janela.destroy).pack()

        tk.Label(janela, text='FORMA DE PAGAMENTO').pack()

        def totalPago(pagamentos):
            totalPago = pagamentos['Dinheiro']

            if pagamentos['Pix']:
                totalPago += sum(pagamentos['Pix'])

            if pagamentos['Credito']:
                for p in pagamentos['Credito']:
                    totalPago += p['valor']

            if pagamentos['Debito']:
                totalPago += sum(pagamentos['Debito'])

            return totalPago

        def atualizarRestante(pago, rest, total):
            rest.configure(state='normal')
            rest.delete(0, tk.END)
            rest.insert(0, f'{total - pago:.2f}')
            rest.configure(state='disabled')

        def atualizarLista(lista, pagamentos):

            for p in lista.get_children():
                lista.delete(p)

            if pagamentos['Dinheiro'] != 0:
                lista.insert('', 'end', values=(
                    'Dinheiro',
                    f"R$ {pagamentos['Dinheiro']:.2f}",
                    ''))
            for pix in pagamentos['Pix']:
                lista.insert('', 'end', values=(
                    'Pix/Transferência',
                    f'R$ {pix:.2f}',
                    ''
                ))
            for cred in pagamentos['Credito']:
                lista.insert('', 'end', values=(
                    'Cartão de Crédito',
                    f"R$ {cred['valor']:.2f}",
                    f"Parcelas: {cred['parcelas']}"
                ))
            for deb in pagamentos['Debito']:
                lista.insert('', 'end', values=(
                    'Cartão de Débito',
                    f"R$ {deb:.2f}",
                    ''
                ))

        def zerar(lista, entries, rest, total):
            pagamentos['Dinheiro'] = 0.0
            pagamentos['Pix'].clear()
            pagamentos['Credito'].clear()
            pagamentos['Debito'].clear()

            for p in lista.get_children():
                lista.delete(p)

            for e in entries:
                e.configure(state='normal')
                e.delete(0, tk.END)
                e.insert(0, '0.00')
                e.configure(state='disabled')

            atualizarRestante(totalPago(pagamentos), rest, total)

        def pagDinheiro(entry, pag, rest, total, lista):
            janelapag = tk.Toplevel(janela)
            janelapag.transient(root)
            janelapag.geometry('150x150')
            janelapag.grab_set()

            tk.Label(janelapag, text='VALOR PAGO: R$').pack()
            valor = tk.Entry(janelapag, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))
            valor.insert(0, entry.get())
            valor.pack()

            def confirmar(v, pag, j, rest, total, entry, lista):

                if v.get() == '':
                    valor = 0
                else:
                    valor = float(v.get())

                pag['Dinheiro'] = valor
                atualizarRestante(totalPago(pag), rest, total)

                entry.configure(state='normal')
                entry.delete(0, tk.END)
                entry.insert(0, f'{valor:.2f}')
                entry.configure(state='disabled')

                atualizarLista(lista, pag)

                j.destroy()

            tk.Button(janelapag, text='Confirmar', command=lambda: confirmar(valor, pag, janelapag, rest, total, entry, lista)).pack()
            janelapag.bind('<Return>', lambda event: confirmar(valor, pag, janelapag, rest, total, entry, lista))

        def pagPix(entry, pag, rest, total, forma, lista):
            janelapag = tk.Toplevel(janela)
            janelapag.transient(root)
            janelapag.geometry('150x150')
            janelapag.grab_set()

            tk.Label(janelapag, text='VALOR PAGO: R$').pack()
            valor = tk.Entry(janelapag, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))
            valor.insert(0, f'{float(rest.get()):.2f}')
            valor.pack()

            def confirmar(v, pag, j, rest, total, entry, forma, lista):

                if v.get() == '':
                    messagebox.showerror('Erro', 'Valor inválido.', parent=j)
                else:
                    if float(v.get()) == 0:
                        messagebox.showerror('Erro', 'Valor inválido.', parent=j)

                    else:
                        valor = float(v.get())
                        pag[forma].append(valor)
                        atualizarRestante(totalPago(pag), rest, total)

                        entry.configure(state='normal')
                        entry.delete(0, tk.END)
                        entry.insert(0, sum(pag[forma]))
                        entry.configure(state='disabled')

                        atualizarLista(lista, pag)

                        j.destroy()

            tk.Button(janelapag, text='Confirmar', command=lambda: confirmar(valor, pag, janelapag, rest, total, entry, forma, lista)).pack()
            janelapag.bind('<Return>', lambda event: confirmar(valor, pag, janelapag, rest, total, entry, forma, lista))


        def pagCredito(entry, pag, rest, total, lista):
            janelapag = tk.Toplevel(janela)
            janelapag.transient(root)
            janelapag.geometry('150x150')
            janelapag.grab_set()

            tk.Label(janelapag, text='VALOR PAGO: R$').pack()
            valor = tk.Entry(janelapag, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))
            valor.insert(0, f'{float(rest.get()):.2f}')
            valor.pack()

            tk.Label(janelapag, text='Qtd. Parcelas:').pack()
            parcelas = tk.Entry(janelapag, validate='key', validatecommand=(janela.register(entryNumInt), '%P'))
            parcelas.insert(0, '1')
            parcelas.pack()

            def confirmar(v, p, pag, j, rest, total, entry, lista):
                if v.get() == '':
                    messagebox.showerror('Erro', 'Valor inválido.', parent=j)
                elif p.get() == '':
                    messagebox.showerror('Erro', 'Quantidade de parcelas inválida.', parent=j)
                else:
                    if float(v.get()) == 0:
                        messagebox.showerror('Erro', 'Valor inválido.', parent=j)
                    elif int(p.get()) == 0:
                        messagebox.showerror('Erro', 'Quantidade de parcelas inválida.', parent=j)
                    else:
                        valor = float(v.get())
                        parcelas = int(p.get())
                        pagamento = {'valor': valor, 'parcelas': parcelas}
                        pag['Credito'].append(pagamento)
                        soma = 0
                        for p in pag['Credito']:
                            soma += p['valor']

                        atualizarRestante(totalPago(pag), rest, total)

                        entry.configure(state='normal')
                        entry.delete(0, tk.END)
                        entry.insert(0, f'{soma:.2f}')
                        entry.configure(state='disabled')

                        atualizarLista(lista, pag)

                        j.destroy()

            tk.Button(janelapag, text='Confirmar', command=lambda: confirmar(valor, parcelas, pag, janelapag, rest, total, entry, lista)).pack()
            janelapag.bind('<Return>', lambda event: confirmar(valor, parcelas, pag, janelapag, rest, total, entry, lista))

        colunas = ['forma', 'valor', 'obs']
        pagtabela = ttk.Treeview(janela, columns=colunas, show='headings')
        pagtabela.heading('forma', text='Forma de pgto')
        pagtabela.heading('valor', text='Valor')
        pagtabela.heading('obs', text='Observação')

        valorRestante = tk.Entry(janela)
        atualizarRestante(totalPago(pagamentos), valorRestante, total)

        dinheiro = tk.Entry(janela)
        dinheiro.insert(0, '0.00')
        dinheiro.config(state='disabled')
        tk.Button(janela, text='Dinheiro:', command= lambda: pagDinheiro(dinheiro, pagamentos, valorRestante, total, pagtabela)).pack()

        dinheiro.pack()

        credito = tk.Entry(janela)
        tk.Button(janela, text='Cartão de crédito:', command=lambda: pagCredito(credito, pagamentos, valorRestante, total, pagtabela)).pack()
        credito.insert(0, '0.00')
        credito.config(state='disabled')
        credito.pack()

        debito = tk.Entry(janela)
        tk.Button(janela, text='Cartão de débito:', command=lambda: pagPix(debito, pagamentos, valorRestante, total, 'Debito', pagtabela)).pack()
        debito.insert(0, '0.00')
        debito.config(state='disabled')
        debito.pack()

        pix = tk.Entry(janela)
        tk.Button(janela, text='PIX / Transferência:', command=lambda: pagPix(pix, pagamentos, valorRestante, total, 'Pix', pagtabela)).pack()
        pix.insert(0, '0.00')
        pix.config(state='disabled')
        pix.pack()

        pagtabela.pack()

        desconto = tk.Entry(janela, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))
        tk.Label(janela, text='DESCONTO: ').pack()
        desconto.pack()

        tk.Label(janela, text='TOTAL DA VENDA: R$').pack()
        valorTotal = tk.Entry(janela)
        valorTotal.insert(0, f'{total:.2f}')
        valorTotal.configure(state='disabled')
        valorTotal.pack()

        tk.Label(janela, text='RESTANTE A PAGAR: R$').pack()
        valorRestante.pack()

        entries = [dinheiro, credito, debito, pix]
        entriesTotal = [valorTotal, valorRestante]

        tk.Button(janela, text='Zerar e recomeçar', command=lambda: zerar(pagtabela, entries, valorRestante, total)).pack()
        tk.Button(janela, text='Finalizar', command=lambda: fecharVenda(venda, float(valorRestante.get()), janela)).pack()

        desconto.bind('<KeyRelease>', lambda event: desc(event, janela, desconto, total, totalPago(pagamentos), entriesTotal))

def fecharVenda(venda, restante, j):

    if restante > 0:
        messagebox.showerror('Pagamento inválido', 'Pagamento menor que o valor total.', parent=j)
    else:
        if restante < 0:
            messagebox.showinfo('Troco', f'Troco devido: R$ {restante * (-1):.2f}', parent=j)

        with open('vendas.json', 'r+', encoding='utf-8') as arq:
            vendas = json.load(arq)
            vendas.append(venda)

            arq.seek(0)
            json.dump(vendas, arq, indent=4, ensure_ascii=False)
            arq.truncate()

            arq.close()
        recibo = messagebox.askyesno('Recibo:', 'Deseja imprimir um recibo da venda?', parent=j)
        if recibo:
            gerarRecibo(venda, restante*(-1))
        j.destroy()
        root.geometry('1000x500')
        frameInicial.tkraise()

def gerarRecibo(venda, troco=0):
    arq = f'recibo_venda{venda["num_venda"]}.pdf'
    recibo = canvas.Canvas(arq)
    recibo.setFont('Courier', 10)
    recibo.setTitle(f'Recibo de Venda N°{venda["num_venda"]}')
    y = 800

    def linha(t, s=15):
        nonlocal y
        recibo.drawString(40, y, t)
        y -= s

    linha(f'RECIBO DA VENDA N°{venda["num_venda"]}')
    linha('----------------------------------------------')
    linha(f'CLIENTE: {venda["cliente"]["nome"]:>36}')
    linha(f'TELEFONE: {venda["cliente"]["telefone"]:>36}')
    linha(f'CPF/CNPJ: {venda["cliente"]["cpf_cnpj"]:>36}')
    linha(f'E-MAIL: {venda["cliente"]["email"]:>36}')
    linha('----------------------------------------------')
    linha(f'{"PRODUTO":<15}{"VLR.UNIT.":>12}{"QTD":>6}{"TOTAL":>12}')
    linha('----------------------------------------------')

    for item in venda['itens']:
        nome = item['nome']
        valor = float(item['preco_venda'])
        qtd = float(item['qtd'])
        total = float(item['total'])

        linha(f'{nome:<15}{valor:12.2f}{qtd:>6.1f}{total:>12.2f}')

    total_geral = float(venda['total'])

    linha('----------------------------------------------')
    linha(f'{"TOTAL GERAL:":>33} R$ {total_geral:>7.2f}')
    linha('----------------------------------------------')
    linha(f'{"FORMAS DE PAGAMENTO":^45}')

    for k, v in venda['pagamento'].items():
        forma = k
        valor = 0
        if forma == 'Credito':
            for pag in v:
                valor = float(pag['valor'])
                parcela = f'Parcelas: {pag["parcelas"]}'

                linha(f'{forma:>15}{valor:^10.2f}{parcela:<20}')

        elif forma == 'Pix' or forma == 'Debito':
            valor = sum(v)
            if valor > 0:
                linha(f'{forma:>15}{valor:^10.2f}')

        else:
            valor = v
            if valor > 0:
                linha(f'{forma:>15}{valor:^10.2f}')

    linha(f'{f"TROCO: {troco:.2f}":^45}')

    recibo.save()
    os.startfile(arq)

def desc(e, j, d, t, pago, entries):
    try:
        desconto = float(d.get()) if d.get() else 0
    except ValueError:
        desconto = 0

    novoTotal = t - desconto
    novoRestante = novoTotal - pago

    if novoTotal < 0:
        messagebox.showerror('Erro', 'Desconto maior que o total.', parent=j)
        return

    entries[0].configure(state='normal')
    entries[0].delete(0, tk.END)
    entries[0].insert(0, f'{novoTotal:.2f}')
    entries[0].configure(state='disabled')

    entries[1].configure(state='normal')
    entries[1].delete(0, tk.END)
    entries[1].insert(0, f'{novoRestante:.2f}')
    entries[1].configure(state='disabled')

def itemEstoque():

    janela = tk.Toplevel()
    janela.title('Item Estoque')
    janela.geometry('300x300')
    janela.grab_set()

    cod = tk.Entry(janela)
    nome = tk.Entry(janela, state='disabled')
    venda = tk.Entry(janela, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))
    qtd = tk.Entry(janela, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))

    tk.Label(janela, text='Código do produto:').pack()
    cod.pack()

    tk.Label(janela, text='Item:').pack()
    nome.pack()

    tk.Label(janela, text='Valor:').pack()
    venda.pack()

    tk.Label(janela, text='Quantidade:').pack()
    qtd.insert(0, '1')
    qtd.pack()

    tk.Label(janela, text='Total:').pack()
    total = tk.Entry(janela, state='disabled')
    total.pack()

    tk.Label(janela, text='Disponível:').pack()
    disp = tk.Entry(janela, state='disabled')
    disp.pack()

    cod.bind('<KeyRelease>', lambda event: item_por_cod(event, cod, nome, venda, disp))
    cod.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total), add='+')
    venda.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))
    qtd.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))

    dados = [cod, nome, venda, qtd, total, disp]

    def procurarItem(d, j):
        estq = receberEstoque()

        janela = tk.Toplevel(j)
        janela.title('Procurar Item')
        janela.geometry('700x700')
        janela.state('zoomed')
        janela.grab_set()

        cod = tk.Entry(janela)
        nome = tk.Entry(janela)
        obs = tk.Entry(janela)

        tk.Label(janela, text='Código:').pack()
        cod.pack()
        tk.Label(janela, text='Nome do produto:').pack()
        nome.pack()
        tk.Label(janela, text='Obs.:').pack()
        obs.pack()

        pesq = [cod, nome, obs]

        dados = ['cod', 'nome', 'preco_venda', 'qtd', 'obs']
        tabela = ttk.Treeview(janela, columns=dados, show='headings')
        tabela.heading('cod', text='Código')
        tabela.heading('nome', text='Nome')
        tabela.heading('preco_venda', text='Valor Unit.')
        tabela.heading('qtd', text='Disponível')
        tabela.heading('obs', text='Observação')

        tabela.pack()

        def procurar(tabela, pesq, estq):
            cod = pesq[0].get()
            nome = pesq[1].get().upper()
            obs = pesq[2].get().upper()
            result = []

            for i in estq:
                if cod in str(i['cod']) and nome in i['nome'].upper() and obs in i['obs'].upper():
                    result.append(i)

            if cod == '' and nome == '' and obs == '':
                result = estq

            for item in tabela.get_children():
                tabela.delete(item)

            for r in result:
                tabela.insert('', 'end', iid=r['cod'], values=(
                    r['cod'],
                    r['nome'],
                    f"{r['preco_venda']:.2f}",
                    f"{r['qtd']:.2f}",
                    r['obs']
                ))

        procurar(tabela, pesq, estq)

        cod.bind('<KeyRelease>', lambda event: procurar(tabela, pesq, estq))
        nome.bind('<KeyRelease>', lambda event: procurar(tabela, pesq, estq))
        obs.bind('<KeyRelease>', lambda event: procurar(tabela, pesq, estq))

        def selecionar(tabela, estq, d, j):

            if tabela.focus() != '':
                cod = int(tabela.focus())

                for item in estq:
                    if cod == item['cod']:

                        d[0].delete(0, tk.END)
                        d[0].insert(0, item['cod'])

                        d[1].configure(state='normal')
                        d[1].delete(0, tk.END)
                        d[1].insert(0, item['nome'])
                        d[1].configure(state='disabled')

                        d[2].delete(0, tk.END)
                        d[2].insert(0, item['preco_venda'])

                        d[4].configure(state='normal')
                        d[4].delete(0, tk.END)
                        d[4].insert(0, f'{item["preco_venda"] * float(d[3].get()):.2f}')
                        d[4].configure(state='disabled')

                        d[5].configure(state='normal')
                        d[5].delete(0, tk.END)
                        d[5].insert(0, item['qtd'])
                        d[5].configure(state='disabled')

                        break

                j.destroy()

        tabela.bind('<Double-1>', lambda event: selecionar(tabela, estq, d, janela))

    tk.Button(janela, text='Procurar', command= lambda: procurarItem(dados, janela)).pack()
    tk.Button(janela, text='Adicionar', command= lambda: addItemEstoque(dados, janela)).pack()

def addItemEstoque(dados, j):
    global itens

    flagItem = True
    flagDados = True

    cod = dados[0].get()
    nome = dados[1].get()
    venda = dados[2].get()
    qtd = dados[3].get()

    if not cod or not nome or not venda or not qtd:
        flagDados = False
        messagebox.showerror('Erro', 'Preencha os dados do item.', parent=j)

    if flagDados:
        for i in itens:
            if i['cod'] == cod:
                flagItem = False
                messagebox.showerror('Erro', 'Item já adicionado ao pedido.', parent=j)
                break

    if flagDados and flagItem:
        total = float(venda) * float(qtd)

        item = {
            'cod': cod,
            'nome': nome,
            'preco_venda': venda,
            'qtd': qtd,
            'total': total
        }

        itens.append(item)
        atualizarItensLista()
        atualizarValorTotal()

        j.destroy()

def item_por_cod(e, c, no, v, d):
    estq = receberEstoque()

    try:
        int(c.get())

    except:
        no.configure(state='normal')
        no.delete(0, tk.END)
        no.configure(state='disabled')
        v.delete(0, tk.END)

        d.configure(state='normal')
        d.delete(0, tk.END)
        d.configure(state='disabled')

    else:
        cod = int(c.get())

        for i in estq:
            if cod == i['cod']:
                item = i
                no.configure(state='normal')
                no.delete(0, tk.END)
                no.insert(0, item['nome'])
                no.configure(state='disabled')

                v.delete(0, tk.END)
                v.insert(0, f'{item["preco_venda"]:.2f}')

                d.configure(state='normal')
                d.delete(0, tk.END)
                d.insert(0, f'{item["qtd"]:.2f}')
                d.configure(state='disabled')
                break
        else:
            no.configure(state='normal')
            no.delete(0, tk.END)
            no.configure(state='disabled')
            v.delete(0, tk.END)

def totalItem(e, v, q, t):
    try:
        float(v.get())
        float(q.get())
    except:
        t.configure(state='normal')
        t.delete(0, tk.END)
        t.configure(state='disabled')
    else:
        venda = float(v.get())
        qtd = float(q.get())
        t.configure(state='normal')
        t.delete(0, tk.END)
        t.insert(0, f'R$ {venda*qtd:.2f}')
        t.configure(state='disabled')

def itemAvulso():

    janela = tk.Toplevel()
    janela.title('Item Avulso')
    janela.geometry('300x200')
    janela.resizable(False, False)
    janela.grab_set()

    nome = tk.Entry(janela)
    venda = tk.Entry(janela, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))
    qtd = tk.Entry(janela, validate='key', validatecommand=(janela.register(entryNumFloat), '%P'))
    total = tk.Entry(janela, state='disabled')
    venda.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))
    qtd.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))

    tk.Label(janela, text='Nome:').pack()
    nome.pack()
    tk.Label(janela, text='Valor venda:').pack()
    venda.pack()
    tk.Label(janela, text='Quantidade:').pack()
    qtd.pack()
    tk.Label(janela, text='Total:').pack()
    total.pack()

    dados = [nome, venda, qtd]

    tk.Button(janela, text='Adicionar', command=lambda: addItemAvulso(dados, janela)).pack()

def addItemAvulso(dados, j):
    global itens

    flag = True

    nome = dados[0].get()
    venda = dados[1].get()
    qtd = dados[2].get()

    if not nome or not venda or not qtd:
        flag = False
        messagebox.showerror('Erro', 'Preencha os dados do item.', parent=j)

    if flag:
        item = {
            'cod': 'Avulso',
            'nome': nome,
            'preco_venda': float(venda),
            'qtd': float(qtd),
            'total': float(venda) * float(qtd)
        }
        itens.append(item)
        atualizarItensLista()
        atualizarValorTotal()

        j.destroy()

def excluirItem(l, f):
    global itens

    try:
        int(l.focus())
    except:
        messagebox.showerror('Erro', 'Selecione um item para remover.', parent=f)
    else:
        ind = int(l.focus())
        item = itens[ind]
        confirm = messagebox.askokcancel('Confirmar', f'Tem certeza que deseja remover o item {item["nome"]}?', parent=f)

        if confirm:
            itens.pop(ind)
            atualizarItensLista()
            atualizarValorTotal()

def cancelarVenda(f):
    global num_venda
    confirm = messagebox.askyesno('Cancelar', f'Tem certeza que deseja cancelar a venda N°{num_venda}?',
                                  parent=f)
    if confirm:
        root.geometry('1000x500')
        f.destroy()

def atualizarItensLista():
    global itensLista, itens

    for i in itensLista.get_children():
        itensLista.delete(i)

    for item in itens:
        itensLista.insert('', 'end', iid=itens.index(item), values=(
            item['cod'],
            item['nome'],
            item['preco_venda'],
            item['qtd'],
            item['total'],
        ))

def atualizarValorTotal():
    global itens, valorTotal, valorTotalLabel
    valorTotal = 0

    for item in itens:
        valorTotal += item['total']

    valorTotalLabel.configure(text=f'{valorTotal:.2f}')

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

def orcamento():
    print('Orçamento')

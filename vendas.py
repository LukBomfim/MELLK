import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
import json, os

from datetime import datetime

# Estilo pros botões, pra deixar tudo com a mesma cara
# Aqui a gente define como os botões vão ficar: fonte, cor, tamanho, tudo padronizado
button_style = {
    'font': ('Arial', 11),
    'bg': 'white',
    'fg': 'black',
    'activebackground': '#E5E5E5',
    'activeforeground': 'black',
    'width': 15,
    'height': 2,
    'borderwidth': 1,
    'cursor': 'hand2',
    'relief': 'flat'
}


def inicio():
    # Essa função monta a tela inicial do módulo de vendas
    global root, frameInicial

    # Usamos Toplevel porque esse módulo é tipo uma "extensão" de uma janela principal que já existe
    root = tk.Toplevel()
    root.geometry('1000x500')  # Define o tamanho inicial da janela
    root.title('VENDAS')  # Nome que aparece na barra de título
    root.state('zoomed')  # Abre a janela maximizada
    root.configure(bg='#1A3C34')  # Fundo verde escuro pra manter o estilo

    # Frame principal que cobre a janela toda, é como a base pra colocar outros elementos
    frameInicial = tk.Frame(root, bg='#1A3C34')
    frameInicial.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Frame pro cabeçalho, só pro título ficar bonitinho
    header_frame = tk.Frame(frameInicial, bg='#1A3C34')
    header_frame.pack(pady=20)
    tk.Label(header_frame, text="Sistema de Vendas - Módulo Vendas", font=('Arial', 16, 'bold'), fg='white',
             bg='#1A3C34').pack()

    # Frame pros botões principais, bem no meio da tela
    button_frame = tk.Frame(frameInicial, bg='#1A3C34')
    button_frame.pack(expand=True)
    tk.Button(button_frame, text='Nova Venda Direta', command=vendaDireta, **button_style).pack(
        pady=10)  # Venda rápida, sem cliente específico
    tk.Button(button_frame, text='Novo Pedido', command=vendaPedido, **button_style).pack(
        pady=10)  # Pedido com cliente cadastrado
    tk.Button(button_frame, text='Listar Vendas', command=listar_vendas, **button_style).pack(
        pady=10)  # Novo orçamento
    tk.Button(button_frame, text='Novo Orçamento', command=novoOrcamento, **button_style).pack(
        pady=10)  # Novo orçamento

    # Mantém a janela aberta, rodando o loop principal
    root.mainloop()


def receberEstoque():
    # Pega os itens do estoque de um arquivo JSON
    try:
        with open('estoque.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)  # Devolve a lista de itens
    except FileNotFoundError:
        return []  # Se não achar o arquivo, retorna uma lista vazia


def receberClientes():
    # Carrega os clientes de um arquivo JSON
    try:
        with open('clientes.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)  # Devolve a lista de clientes
    except FileNotFoundError:
        return []  # Se o arquivo não existir, retorna lista vazia


def receberVendas():
    # Carrega as vendas de um arquivo JSON
    try:
        with open('vendas.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)  # Devolve a lista de vendas
    except FileNotFoundError:
        return []  # Se o arquivo não existir, retorna lista vazia


def vendaDireta():
    # Começa uma venda direta, sem precisar escolher cliente
    global cliente
    cliente = {
        "cod": None,
        "nome": "CLIENTE NÃO IDENTIFICADO",
        "telefone": "",
        "cpf_cnpj": "",
        "cep": "",
        "num_casa": "",
        "email": ""
    }  # Cliente padrão pra vendas rápidas
    venda()  # Abre a tela de venda


def vendaPedido():
    # Inicia um pedido, mas precisa escolher um cliente primeiro
    global cliente
    cliente = {}  # Cliente começa vazio, vai ser preenchido depois da busca

    # Nova janela pra buscar o cliente
    janela = tk.Toplevel(root)
    janela.transient(root)  # Faz ela depender da janela principal
    janela.grab_set()  # Trava o foco nessa janela até fechar
    janela.title('MELLK - Busca de Cliente')
    janela.geometry('900x400')
    janela.configure(bg='#1A3C34')

    # Centraliza a janela na tela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - 900) // 2
    pos_y = (altura_tela - 400) // 2
    janela.geometry(f'900x400+{pos_x}+{pos_y}')

    # Frame que cobre a janela toda
    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Título da janela de busca
    tk.Label(frame, text='Pesquisar Cliente', font=('Arial', 14, 'bold'), fg='white', bg='#1A3C34').pack(pady=10)

    # Frame pra busca, com combobox e campo de texto
    search_frame = tk.Frame(frame, bg='#1A3C34')
    search_frame.pack(pady=10, fill='x', padx=20)
    tk.Label(search_frame, text='Pesquisar por:', font=('Arial', 12), fg='white', bg='#1A3C34').pack()
    opc = ttk.Combobox(search_frame, values=['Nome', 'Telefone', 'CPF/CNPJ'], state='readonly', font=('Arial', 12))
    opc.set('Nome')  # Começa com busca por nome
    opc.pack(pady=5)
    pesquisa = tk.Entry(search_frame, font=('Arial', 12), width=30)
    pesquisa.pack(pady=5)

    # Tabela pra mostrar os resultados da busca
    dados = ['cod', 'nome', 'telefone', 'cpf_cnpj']
    lista = ttk.Treeview(frame, columns=dados, show='headings', height=10)
    lista.heading('cod', text='Cód.')
    lista.heading('nome', text='Nome')
    lista.heading('telefone', text='Telefone')
    lista.heading('cpf_cnpj', text='CPF/CNPJ')
    lista.column('cod', width=100)
    lista.column('nome', width=300)
    lista.column('telefone', width=150)
    lista.column('cpf_cnpj', width=150)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=lista.yview)
    lista.configure(yscrollcommand=scrollbar.set)
    lista.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    # Botões pra procurar ou cancelar
    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Procurar', command=lambda: buscaCliente(janela, opc, pesquisa, lista),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)
    janela.bind('<Return>', lambda event: buscaCliente(janela, opc, pesquisa, lista, event))  # Busca com Enter
    lista.bind('<Double-1>',
               lambda event: selecionarClienteVenda(event, janela, lista))  # Seleciona cliente com duplo clique


def buscaCliente(j, cb, pe, l, e=None):
    # Faz a busca de clientes com base no critério escolhido
    clientes = receberClientes()
    opc = cb.get()  # Pega o tipo de busca (Nome, Telefone, CPF/CNPJ)
    pesq = pe.get()  # Pega o texto digitado
    resultado = []

    if opc == 'Nome':
        if pesq:
            for result in clientes:
                if pesq.upper() in result['nome'].upper():  # Busca case-insensitive
                    c = {
                        'cod': result['cod'],
                        'nome': result['nome'],
                        'telefone': result['telefone'],
                        'cpf_cnpj': result['cpf_cnpj'],
                    }
                    resultado.append(c)
    elif opc == 'Telefone':
        p = ''.join(n for n in pe.get() if n.isnumeric())  # Só números
        if p:
            for result in clientes:
                tel = ''.join(n for n in result['telefone'] if n.isnumeric())
                if p in tel:
                    c = {
                        'cod': result['cod'],
                        'nome': result['nome'],
                        'telefone': result['telefone'],
                        'cpf_cnpj': result['cpf_cnpj']
                    }
                    resultado.append(c)
    elif opc == 'CPF/CNPJ':
        p = ''.join(n for n in pe.get() if n.isnumeric())  # Só números
        if p:
            for result in clientes:
                cpf = ''.join(n for n in result['cpf_cnpj'] if n.isnumeric())
                if p in cpf:
                    c = {
                        'cod': result['cod'],
                        'nome': result['nome'],
                        'telefone': result['telefone'],
                        'cpf_cnpj': result['cpf_cnpj']
                    }
                    resultado.append(c)

    # Limpa a tabela antes de mostrar os resultados
    for r in l.get_children():
        l.delete(r)

    # Preenche a tabela com os clientes encontrados
    for r in resultado:
        l.insert('', 'end', iid=r['cod'], values=(
            r['cod'],
            r['nome'],
            r['telefone'],
            r['cpf_cnpj'],
        ))


def selecionarClienteVenda(e, j, l):
    # Seleciona um cliente da tabela e vai pra tela de venda
    global cliente
    clientes = receberClientes()

    try:
        codCliente = int(l.focus())  # Pega o código do cliente selecionado
        for c in clientes:
            if c['cod'] == codCliente:
                cliente = c  # Define o cliente escolhido
                j.destroy()  # Fecha a janela de busca
                venda()  # Abre a tela de venda
                break
    except:
        return  # Se não selecionar nada, só ignora


def venda():
    # Monta a tela principal de vendas
    global num_venda, itens, itensLista, valorTotal, valorTotalLabel

    itens = []  # Lista de itens da venda
    valorTotal = 0.0  # Total começa zerado

    # Pega o número da próxima venda
    try:
        with open('vendas.json', 'r', encoding='utf-8') as arq:
            vendas = json.load(arq)
        num_venda = 1 if not vendas else vendas[-1].get('num_venda', 0) + 1
    except FileNotFoundError:
        num_venda = 1

    # Ajusta o tamanho da janela pra tela de venda
    root.geometry('1000x700')
    frame = tk.Frame(root, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Define fontes pra manter o visual consistente
    fonte = ('Arial', 12)
    fonte_bold = ('Arial', 14, 'bold')

    # Cabeçalho com número da venda e nome do cliente
    header_frame = tk.Frame(frame, bg='#1A3C34')
    header_frame.pack(pady=10, fill='x')
    tk.Label(header_frame, text=f'Venda N°{num_venda} - Cliente: {cliente["nome"]}', font=fonte_bold, fg='white',
             bg='#1A3C34').pack()

    # Mostra os dados do cliente
    cliente_frame = tk.Frame(frame, bg='#1A3C34')
    cliente_frame.pack(pady=10, fill='x', padx=20)
    tk.Label(cliente_frame, text=f'Telefone: {cliente["telefone"]}', font=fonte, fg='white', bg='#1A3C34').pack(
        anchor='w')
    tk.Label(cliente_frame, text=f'CPF/CNPJ: {cliente["cpf_cnpj"]}', font=fonte, fg='white', bg='#1A3C34').pack(
        anchor='w')
    tk.Label(cliente_frame, text=f'CEP: {cliente["cep"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')
    tk.Label(cliente_frame, text=f'N°: {cliente["num_casa"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')
    tk.Label(cliente_frame, text=f'E-mail: {cliente["email"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')

    # Frame pra adicionar itens pelo código, com rótulos pra cada campo
    item_frame = tk.Frame(frame, bg='#1A3C34')
    item_frame.pack(pady=10, fill='x', padx=20)

    # Rótulo e entrada pro código do produto
    tk.Label(item_frame, text='Código:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    cod_entry = tk.Entry(item_frame, font=fonte, width=10, bg='#E5E5E5', fg='#000000', insertbackground='#000000')
    cod_entry.pack(side=tk.LEFT, padx=5)

    # Rótulo e entrada pra quantidade a vender
    tk.Label(item_frame, text='Quantidade:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT, padx=(10, 5))
    qtd_entry = tk.Entry(item_frame, font=fonte, width=10, bg='#E5E5E5', fg='#000000', insertbackground='#000000')
    qtd_entry.insert(0, '1.00')
    qtd_entry.pack(side=tk.LEFT, padx=5)

    # Rótulo e campo pro nome do produto
    tk.Label(item_frame, text='Nome do Produto:', font=fonte, fg='white', bg="#1A3C34").pack(side=tk.LEFT, padx=(10, 5))
    nome_label = tk.Label(item_frame, text='', font=fonte, fg='white', bg='#3b3b3b', width=30, relief="sunken", bd=3)
    nome_label.pack(side=tk.LEFT, padx=5)

    # Rótulo e campo pro valor unitário
    tk.Label(item_frame, text='Valor Unit.:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT, padx=(10, 5))
    preco_label = tk.Label(item_frame, text='', font=fonte, fg='white', bg='#3b3b3b', width=10, relief="sunken", bd=3)
    preco_label.pack(side=tk.LEFT, padx=5)

    # Rótulo e campo pra quantidade disponível
    tk.Label(item_frame, text='Disponível:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT, padx=(10, 5))
    disp_label = tk.Label(item_frame, text='', font=fonte, fg='white', bg='#3b3b3b', width=10, relief="sunken", bd=3)
    disp_label.pack(side=tk.LEFT, padx=5)

    # Botão pra adicionar o item
    tk.Button(item_frame, text='Adicionar',
              command=lambda: adicionarItemPorCodigo(cod_entry, nome_label, preco_label, qtd_entry, disp_label, frame),
              **button_style).pack(side=tk.LEFT, padx=5)

    # Faz a busca do item enquanto o usuário digita o código
    cod_entry.bind('<KeyRelease>', lambda event: item_por_cod(event, cod_entry, nome_label, preco_label, disp_label))

    # Ao clicar enter, adiciona ...
    cod_entry.bind('<Return>',
                   lambda event: adicionarItemPorCodigo(cod_entry, nome_label, preco_label, qtd_entry, disp_label,
                                                        frame))

    # Exibindo o valor total
    total_frame = tk.Frame(frame, bg='#1A3C34')
    total_frame.pack(pady=10)
    tk.Label(total_frame, text='Valor Total:', font=fonte_bold, fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    valorTotalLabel = tk.Label(total_frame, text=f'R$ {valorTotal:.2f}', font=fonte_bold, fg='white', bg='#1A3C34',
                               bd=1, relief="raised")
    valorTotalLabel.pack(side=tk.LEFT, padx=5)

    # Frame para a tabela e barra de rolagem
    table_frame = tk.Frame(frame, bg='#1A3C34')
    table_frame.pack(fill='both', expand=True, padx=20, pady=10)

    # Tabela pra listar os itens da venda
    colunas = ['cod', 'nome', 'preco_venda', 'qtd', 'total']

    itensLista = ttk.Treeview(table_frame, columns=colunas, show='headings', height=10)
    itensLista.heading('cod', text='Código')
    itensLista.heading('nome', text='Nome')
    itensLista.heading('preco_venda', text='Valor Unit.')
    itensLista.heading('qtd', text='Qtd')
    itensLista.heading('total', text='Total')
    itensLista.column('cod', width=100)
    itensLista.column('nome', width=300)
    itensLista.column('preco_venda', width=100)
    itensLista.column('qtd', width=100)
    itensLista.column('total', width=100)

    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=itensLista.yview)
    itensLista.configure(yscrollcommand=scrollbar.set)
    itensLista.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    # Botões pra gerenciar a venda, organizados em duas colunas abaixo da tabela
    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)

    tk.Button(button_frame, text='Add. Item do Estoque', command=itemEstoque, **button_style).pack(padx=5, side=tk.LEFT)
    tk.Button(button_frame, text='Add. Item Avulso', command=itemAvulso, **button_style).pack(padx=5, side=tk.LEFT)
    tk.Button(button_frame, text='Excluir Item', command=lambda: excluirItem(itensLista, frame), **button_style).pack(
        padx=5, side=tk.LEFT)
    tk.Button(button_frame, text='Cancelar Venda', command=lambda: cancelarVenda(frame), **button_style).pack(padx=5,
                                                                                                              side=tk.LEFT)
    tk.Button(button_frame, text='Finalizar Venda', command=lambda: finalizarVenda([num_venda, cliente, itens]),
              **button_style).pack(padx=5, side=tk.LEFT)

    itensLista.bind('<Delete>', lambda event: excluirItem(itensLista, frame))


def adicionarItemPorCodigo(cod_entry, nome_label, preco_label, qtd_entry, disp_label, parent):
    # Adiciona um item à venda usando o código digitado
    global itens

    estoque = receberEstoque()

    cod = cod_entry.get()
    nome = nome_label['text']
    preco = preco_label['text']
    qtd = qtd_entry.get()
    disp = disp_label['text']

    # Verifica se todos os campos estão preenchidos
    if not cod or not nome or not preco or not qtd or not disp:
        messagebox.showerror('Erro', 'Preencha ou selecione um item válido', parent=parent)
        return

    # Tenta converter os valores pra números
    try:
        cod_val = int(cod)
        preco_val = float(preco.replace('R$ ', ''))
        qtd_val = float(qtd)
        disp_val = float(disp)
    except ValueError:
        messagebox.showerror('Erro', 'Valores inválidos para preço ou quantidade', parent=parent)
        return

    # Quantidade não pode ser zero ou negativa
    if qtd_val <= 0:
        messagebox.showerror('Erro', 'A quantidade deve ser maior que zero', parent=parent)
        return

    # Verifica se tem estoque suficiente
    if qtd_val > disp_val:
        confirm = messagebox.askyesnocancel('Estoque Indisponível',
                                            f'Quantidade disponível em estoque ({disp_val}), é insuficiente.\n'
                                            f'Deseja adicionar mesmo assim?',
                                            parent=parent)
        if not confirm:
            return

    # Não deixa adicionar o mesmo item duas vezes
    for item in itens:
        if item['cod'] == cod:
            messagebox.showerror('Erro', 'Item já adicionado à venda', parent=parent)
            return

    # Calcula o total e cria o item
    total = preco_val * qtd_val

    for i in estoque:
        if cod_val == i['cod']:
            univ_cod = i['univ_cod']
            break
    else:
        univ_cod = ''

    item = {
        'univ_cod': univ_cod,
        'cod': cod,
        'nome': nome,
        'preco_venda': preco_val,
        'qtd': qtd_val,
        'total': total
    }
    itens.append(item)
    atualizarItensLista()  # Atualiza a tabela
    atualizarValorTotal()  # Atualiza o total

    # Limpa os campos pra próxima adição
    cod_entry.delete(0, tk.END)
    nome_label.configure(text='')
    preco_label.configure(text='')
    qtd_entry.delete(0, tk.END)
    qtd_entry.insert(0, '1.00')
    disp_label.configure(text='')


def item_por_cod(e, c, no, v, d):
    # Busca item no estoque enquanto o usuário digita o código
    estq = receberEstoque()

    try:
        cod = int(c.get())  # Tenta pegar o código digitado
    except:
        no.configure(text='')  # Se não for válido, limpa os campos
        v.configure(text='')
        d.configure(text='')
    else:
        for i in estq:
            if cod == i['cod']:  # Achou o item
                no.configure(text=i['nome'])
                v.configure(text=f'R$ {i["preco_venda"]:.2f}')
                d.configure(text=f'{i["qtd"]:.2f}')
                break
        else:
            no.configure(text='')  # Se não achar, limpa
            v.configure(text='')
            d.configure(text='')


def finalizarVenda(inf_vendas):
    # Tela pra finalizar a venda e processar o pagamento
    num_venda = inf_vendas[0]
    cliente = inf_vendas[1]
    itens = inf_vendas[2]
    total = sum(item['total'] for item in itens)  # Calcula o total

    # Não deixa finalizar sem itens
    if not itens:
        messagebox.showerror('Erro', 'Nenhum item adicionado à venda', parent=root)
        return

    # Nova janela pra finalizar
    janela = tk.Toplevel(root)
    janela.transient(root)
    janela.grab_set()
    janela.title('MELLK - Finalizar Venda')
    largura_janela = 900
    altura_janela = 600
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()

    pos_x = (largura_tela - largura_janela) // 2
    pos_y = (altura_tela - altura_janela) // 2

    janela.geometry(f'{largura_janela}x{altura_janela}+{pos_x}+{pos_y}')
    janela.configure(bg='#1A3C34')
    janela.resizable(False, False)

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    fonte_bold = ('Arial', 14, 'bold')
    num_float = (janela.register(entryNumFloat), '%P')  # Valida números decimais

    tk.Label(frame, text=f'Finalizar Venda N°{num_venda}', font=fonte_bold, fg='white', bg='#1A3C34').pack(pady=10)

    # Dicionário pra armazenar os pagamentos
    pagamentos = {'Dinheiro': 0.0, 'Pix': [], 'Credito': [], 'Debito': []}

    def totalPago(pagamentos):
        # Calcula o total pago somando todas as formas
        totalPago = pagamentos['Dinheiro']
        totalPago += sum(pagamentos['Pix'])
        totalPago += sum(pagamentos['Debito'])
        for p in pagamentos['Credito']:
            totalPago += p['valor']

        return totalPago

    def atualizarRestante(pago, rest, total):
        # Atualiza o campo "Restante a Pagar"
        rest.configure(state='normal')
        rest.delete(0, tk.END)
        rest.insert(0, f'{total - pago:.2f}')
        rest.configure(state='disabled')

    def atualizarLista(lista, pagamentos):
        # Atualiza a tabela de formas de pagamento
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
        # Reseta todos os pagamentos
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

    def pagDinheiro(entry, pag, rest, lista):
        # Janela pra adicionar pagamento em dinheiro
        janelapag = tk.Toplevel(janela)
        janelapag.transient(janela)
        janelapag.geometry(f'{largura_janela - 500}x{altura_janela - 450}+{pos_x * 2}+{pos_y * 2}')
        janelapag.configure(bg='#1A3C34')
        janelapag.grab_set()

        tk.Label(janelapag, text='Valor Pago (R$):', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        valor = tk.Entry(janelapag, font=fonte, validate='key', validatecommand=num_float)
        valor.insert(0, entry.get())
        valor.pack(pady=2)

        def confirmar(v, pag, j, rest, entry, lista):
            valor_val = float(v.get() or 0)
            pag['Dinheiro'] = valor_val
            atualizarRestante(totalPago(pag), rest, float(valorTotal.get()))
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, f'{valor_val:.2f}')
            entry.configure(state='disabled')
            atualizarLista(lista, pag)
            j.destroy()

        tk.Button(janelapag, text='Confirmar',
                  command=lambda: confirmar(valor, pag, janelapag, rest, entry, lista), **button_style).pack(
            pady=10)
        janelapag.bind('<Return>', lambda event: confirmar(valor, pag, janelapag, rest, entry, lista))

    def pagPix(entry, pag, rest, forma, lista):
        # Janela pra adicionar pagamento via Pix ou Débito
        janelapag = tk.Toplevel(janela)
        janelapag.transient(janela)

        janelapag.geometry(f'{largura_janela - 500}x{altura_janela - 450}+{pos_x * 2}+{pos_y * 2}')

        janelapag.configure(bg='#1A3C34')
        janelapag.grab_set()

        tk.Label(janelapag, text='Valor Pago (R$):', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        valor = tk.Entry(janelapag, font=fonte, validate='key', validatecommand=num_float)
        valor.insert(0, f'{float(rest.get()):.2f}')
        valor.pack(pady=2)

        def confirmar(v, pag, j, rest, entry, forma, lista):
            if not v.get() or float(v.get()) == 0:
                messagebox.showerror('Erro', 'Insira um valor válido', parent=j)
                return
            valor_val = float(v.get())
            pag[forma].append(valor_val)
            atualizarRestante(totalPago(pag), rest, float(valorTotal.get()))
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, f'{sum(pag[forma]):.2f}')
            entry.configure(state='disabled')
            atualizarLista(lista, pag)
            j.destroy()

        tk.Button(janelapag, text='Confirmar',
                  command=lambda: confirmar(valor, pag, janelapag, rest, entry, forma, lista),
                  **button_style).pack(pady=10)
        janelapag.bind('<Return>', lambda event: confirmar(valor, pag, janelapag, rest, entry, forma, lista))

    def pagCredito(entry, pag, rest, lista):
        # Janela pra adicionar pagamento com cartão de crédito
        janelapag = tk.Toplevel(janela)
        janelapag.transient(janela)
        janelapag.geometry(f'{largura_janela - 500}x{altura_janela - 250}+{pos_x * 2}+{pos_y * 2}')
        janelapag.configure(bg='#1A3C34')
        janelapag.grab_set()

        tk.Label(janelapag, text='Valor Pago (R$):', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        valor = tk.Entry(janelapag, font=fonte, validate='key', validatecommand=num_float)
        valor.insert(0, f'{float(rest.get()):.2f}')
        valor.pack(pady=2)
        tk.Label(janelapag, text='Qtd. Parcelas:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        parcelas = tk.Entry(janelapag, font=fonte, validate='key',
                            validatecommand=(janelapag.register(entryNumInt), '%P'))
        parcelas.insert(0, '1')
        parcelas.pack(pady=2)

        def confirmar(v, parc, pag, j, rest, entry, lista):
            if not v.get() or float(v.get()) == 0:
                messagebox.showerror('Erro', 'Insira um valor válido', parent=j)
                return
            if not parc.get() or int(parc.get()) == 0:
                messagebox.showerror('Erro', 'Quantidade de parcelas inválida', parent=j)
                return
            valor_val = float(v.get())
            parcelas_val = int(parc.get())
            pagamento = {'valor': valor_val, 'parcelas': parcelas_val}
            pag['Credito'].append(pagamento)
            atualizarRestante(totalPago(pag), rest, float(valorTotal.get()))
            entry.configure(state='normal')
            entry.delete(0, tk.END)
            entry.insert(0, f'{sum(p["valor"] for p in pag["Credito"]):.2f}')
            entry.configure(state='disabled')
            atualizarLista(lista, pag)
            j.destroy()

        tk.Button(janelapag, text='Confirmar',
                  command=lambda: confirmar(valor, parcelas, pag, janelapag, rest, entry, lista),
                  **button_style).pack(pady=10)
        janelapag.bind('<Return>', lambda event: confirmar(valor, parcelas, pag, janelapag, rest, entry, lista))

    # Frame pros valores totais e desconto
    total_frame = tk.Frame(frame, bg='#1A3C34')
    total_frame.pack(pady=10, fill='x', padx=20)

    tk.Label(total_frame, text='Desconto (R$):', font=fonte, fg='white', bg='#1A3C34').grid(row=0, column=0, padx=5,
                                                                                            pady=5, sticky='e')
    descontoEntry = tk.Entry(total_frame, font=fonte, width=15, validate='key', validatecommand=num_float)
    descontoEntry.insert(0, '0.00')
    descontoEntry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(total_frame, text='Total da Venda (R$):', font=fonte, fg='white', bg='#1A3C34').grid(row=0, column=2,
                                                                                                  padx=5, pady=5,
                                                                                                  sticky='e')
    valorTotal = tk.Entry(total_frame, font=fonte, width=15, disabledbackground='#E5E5E5')
    valorTotal.insert(0, f'{total:.2f}')
    valorTotal.configure(state='disabled')
    valorTotal.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(total_frame, text='Restante a Pagar (R$):', font=fonte, fg='white', bg='#1A3C34').grid(row=0, column=4,
                                                                                                    padx=5, pady=5,
                                                                                                    sticky='e')
    valorRestante = tk.Entry(total_frame, font=fonte, width=15, state='disabled', disabledbackground='#E5E5E5')
    valorRestante.insert(0, f'{total:.2f}')
    valorRestante.grid(row=0, column=5, padx=5, pady=5)
    atualizarRestante(totalPago(pagamentos), valorRestante, total)

    # Frame pras formas de pagamento
    pagamento_frame = tk.Frame(frame, bg='#1A3C34')
    pagamento_frame.pack(pady=10, fill='x', padx=20)
    tk.Label(pagamento_frame, text='Formas de Pagamento', font=fonte_bold, fg='white', bg='#1A3C34').pack(anchor='w')

    entries = []
    for forma in ['Dinheiro', 'Pix', 'Debito', 'Credito']:
        subframe = tk.Frame(pagamento_frame, bg='#1A3C34')
        subframe.pack(fill='x', pady=2)
        tk.Label(subframe, text=f'{forma}:', font=fonte, fg='white', bg='#1A3C34', width=15).pack(side=tk.LEFT)
        entry = tk.Entry(subframe, font=fonte, width=15, state='disabled', disabledbackground='#E5E5E5')
        entry.insert(0, '0.00')
        entry.pack(side=tk.LEFT, padx=5)
        entries.append(entry)
        if forma == 'Credito':
            tk.Button(subframe, text='Adicionar',
                      command=lambda e=entry: pagCredito(e, pagamentos, valorRestante, pagtabela),
                      **button_style).pack(side=tk.LEFT)
        elif forma == 'Dinheiro':
            tk.Button(subframe, text='Adicionar',
                      command=lambda e=entry: pagDinheiro(e, pagamentos, valorRestante, pagtabela),
                      **button_style).pack(side=tk.LEFT)
        else:
            tk.Button(subframe, text='Adicionar',
                      command=lambda e=entry, f=forma: pagPix(e, pagamentos, valorRestante, f, pagtabela),
                      **button_style).pack(side=tk.LEFT)

    # Tabela pra mostrar as formas de pagamento
    colunas = ['forma', 'valor', 'obs']
    pagtabela = ttk.Treeview(frame, columns=colunas, show='headings', height=5)
    pagtabela.heading('forma', text='Forma de Pagamento')
    pagtabela.heading('valor', text='Valor')
    pagtabela.heading('obs', text='Observação')
    pagtabela.column('forma', width=150)
    pagtabela.column('valor', width=100)
    pagtabela.column('obs', width=200)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=pagtabela.yview)
    pagtabela.configure(yscrollcommand=scrollbar.set)
    pagtabela.pack(fill='x', padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    def confirmarPagamento():
        # Confirma o pagamento e finaliza a venda
        desconto = float(descontoEntry.get())
        total_pago = totalPago(pagamentos)
        total_venda = float(valorTotal.get())
        bruto = total_venda + desconto
        if total_pago < total_venda:
            messagebox.showerror('Erro', 'O valor pago é insuficiente', parent=janela)
            return

        venda = {
            'num_venda': num_venda,
            'cliente': cliente,
            'itens': itens,
            'bruto': bruto,
            'desconto': desconto,
            'total': total_venda,
            'pagamento': pagamentos,
            'data': datetime.now().strftime("%d/%m/%Y")  # Adicionando a data no ato da vendas...
        }
        fecharVenda(venda, total_venda - total_pago, janela)

    # Atualiza os totais quando o desconto muda
    descontoEntry.bind('<KeyRelease>', lambda event: desc(event, janela, descontoEntry, total, totalPago(pagamentos),
                                                          valorTotal, valorRestante))

    # Botões pra gerenciar o pagamento
    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=20)
    tk.Button(button_frame, text='Zerar e Recomeçar', command=lambda: zerar(pagtabela, entries, valorRestante, total),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Confirmar Pagamento', command=confirmarPagamento, **button_style).pack(side=tk.LEFT,
                                                                                                         padx=5)
    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)


def fecharVenda(venda, restante, j):
    estoque = receberEstoque()

    # Valida o pagamento
    if restante > 0:
        messagebox.showerror('Pagamento inválido', 'Pagamento menor que o valor total', parent=j)
        return
    if restante < 0:
        messagebox.showinfo('Troco', f'Troco devido: R$ {restante * (-1):.2f}', parent=j)

    # Salva a venda no arquivo JSON
    try:
        with open('vendas.json', 'r+', encoding='utf-8') as arq:
            vendas = json.load(arq)
            vendas.append(venda)
            arq.seek(0)
            json.dump(vendas, arq, indent=4, ensure_ascii=False)
            arq.truncate()
    except FileNotFoundError:
        with open('vendas.json', 'w', encoding='utf-8') as arq:
            json.dump([venda], arq, indent=4, ensure_ascii=False)

    # Atualiza o estoque
    for item in venda['itens']:
        for produto in estoque:
            if item['univ_cod'] == produto['univ_cod']:
                produto['qtd'] -= item['qtd']
                break
    with open('estoque.json', 'w', encoding='utf-8') as arq:
        json.dump(estoque, arq, indent=4, ensure_ascii=False)

    # Sincroniza contas a receber para vendas a crédito
    if venda['pagamento'].get('Credito'):
        try:
            from financeiro import criarContasReceberVenda
            criarContasReceberVenda(venda)
        except ImportError:
            messagebox.showwarning('Aviso', 'Módulo financeiro não encontrado. Contas a receber não foram criadas.',
                                   parent=j)

    # Pergunta se quer gerar recibo
    recibo = messagebox.askyesno('Recibo:', 'Deseja imprimir um recibo da venda?', parent=j)
    if recibo:
        gerarRecibo(venda, restante * (-1))
    j.destroy()
    root.geometry('1000x500')
    frameInicial.tkraise()  # Volta pra tela inicial


def gerarRecibo(venda, troco=0):
    # ciando arquivo do recibo em Pdf
    arq = f'recibo_venda{venda["num_venda"]}.pdf'

    # Tamanho da página
    page_size = (227, 280)
    recibo = canvas.Canvas(arq, pagesize=page_size)
    largura, altura = page_size
    margem = 10  # margem

    recibo.setFont('Courier', 6)  # fonte
    recibo.setTitle(f'Recibo de Venda N°{venda["num_venda"]}')
    y = altura - margem - 20  # inicio

    def linha(t, s=10, centro=False):
        # escreve uma linha no PDF
        nonlocal y
        if y < margem + 20:  # nova página
            recibo.showPage()
            recibo.setFont('Courier', 8)
            y = altura - margem - 20
        if centro:
            recibo.drawCentredString(largura / 2, y, t)
        else:
            recibo.drawString(margem, y, t)
        y -= s

    # Título + data
    recibo.setFont('Courier-Bold', 10)
    linha(f'RECIBO VENDA {venda["num_venda"]}', centro=True, s=12)
    recibo.setFont('Courier', 8)
    linha(f'Data: {venda["data"]}', s=10)  # linh da data!
    linha('-' * 40, s=10)

    # Dados do cliente
    linha(f'CLIENTE: {venda["cliente"]["nome"][:20]:<20}')
    linha(f'CPF/CNPJ: {venda["cliente"]["cpf_cnpj"]:<20}')
    linha('-' * 40, s=10)

    # Tabela de itens
    linha(f'{"ITEM":<20}{"VAL":>8}{"QTD":>6}{"TOTAL":>8}')
    linha('-' * 40, s=8)
    for item in venda['itens']:
        nome = item['nome'][:20]
        valor = float(item['preco_venda'])
        qtd = float(item['qtd'])
        total = float(item['total'])
        linha(f'{nome:<20}{valor:>8.2f}{qtd:>6.1f}{total:>8.2f}')

    # Totais
    totalfinal = float(venda['total'])
    linha('-' * 40, s=10)
    linha(f'{"BRUTO:":>26} R${venda["bruto"]:>8.2f}')
    linha(f'{"DESCONTO:":>26} R${venda["desconto"]:>8.2f}')
    linha(f'{"FINAL:":>26} R${totalfinal:>8.2f}')
    linha('-' * 40, s=8)

    # Formas de pagamento
    linha('PAGAMENTOS', centro=True)
    linha('-' * 40, s=8)
    linha(f'{"TIPO":<15}{"VALOR":>10}')
    linha('-' * 40, s=8)
    for k, v in venda['pagamento'].items():
        forma = k
        valor = 0
        if forma == 'Credito':
            for pag in v:
                valor = float(pag['valor'])
                linha(f'{forma[:15]:<15}{valor:>10.2f}')
        elif forma == 'Pix' or forma == 'Debito':
            valor = sum(v)
            if valor > 0:
                linha(f'{forma[:15]:<15}{valor:>10.2f}')
        else:
            valor = v
            if valor > 0:
                linha(f'{forma[:15]:<15}{valor:>10.2f}')

    # Troco
    linha('-' * 40, s=8)
    linha(f'{"TROCO:":<15} R${troco:>10.2f}')

    recibo.setFont('Courier', 6)

    recibo.save()
    os.startfile(arq)  # Abre o PDF (só funciona no Windows)


def desc(e, j, d, t, pago, entryTotal, restante):
    # Atualiza os totais quando o desconto é alterado
    try:
        desconto = float(d.get()) if d.get() else 0
    except ValueError:
        desconto = 0

    novoTotal = t - desconto
    novoRestante = novoTotal - pago

    if novoTotal < 0:
        messagebox.showerror('Erro', 'Desconto maior que o total', parent=j)
        return

    entryTotal.configure(state='normal')
    entryTotal.delete(0, tk.END)
    entryTotal.insert(0, f'{novoTotal:.2f}')
    entryTotal.configure(state='disabled')

    restante.configure(state='normal')
    restante.delete(0, tk.END)
    restante.insert(0, f'{novoRestante:.2f}')
    restante.configure(state='disabled')


def itemEstoque():
    # Janela pra adicionar item do estoque
    janela = tk.Toplevel(root)
    janela.title('MELLK - Adicionar Item do Estoque')
    janela.configure(bg='#1A3C34')
    janela.resizable(False, False)
    janela.grab_set()

    # Centraliza a janela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - 400) // 2
    pos_y = (altura_tela - 400) // 2
    janela.geometry(f'400x500+{pos_x}+{pos_y}')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    num_float = (janela.register(entryNumFloat), '%P')

    cod = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')
    nome = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')
    venda = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    qtd = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    total = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')
    disp = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')

    tk.Label(frame, text='Código do produto:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    cod.pack(pady=2)
    tk.Label(frame, text='Item:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    nome.pack(pady=2)
    tk.Label(frame, text='Valor:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    venda.pack(pady=2)
    tk.Label(frame, text='Quantidade:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    qtd.insert(0, '1.00')
    qtd.pack(pady=2)
    tk.Label(frame, text='Total:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    total.pack(pady=2)
    tk.Label(frame, text='Disponível:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    disp.pack(pady=2)

    venda.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))
    qtd.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))

    dados = [cod, nome, venda, qtd, total, disp]

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Procurar', command=lambda: procurarItem(dados, janela), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Adicionar', command=lambda: addItemEstoque(dados, janela), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)


def addItemEstoque(dados, j):
    # Adiciona item do estoque à venda
    global itens

    cod = dados[0].get()
    nome = dados[1].get()
    venda = dados[2].get()
    qtd = dados[3].get()
    disp = dados[5].get()

    if not cod or not nome or not venda or not qtd or not disp:
        messagebox.showerror('Erro', 'Preencha todos os campos do item', parent=j)
        return

    try:
        venda_val = float(venda)
        qtd_val = float(qtd)
        disp_val = float(disp)
    except ValueError:
        messagebox.showerror('Erro', 'Valores de venda ou quantidade inválidos', parent=j)
        return

    if qtd_val <= 0:
        messagebox.showerror('Erro', 'A quantidade deve ser maior que zero', parent=j)
        return

    if qtd_val > disp_val:
        messagebox.showerror('Erro', f'Quantidade solicitada ({qtd_val}) excede o estoque disponível ({disp_val})',
                             parent=j)
        return

    for i in itens:
        if i['cod'] == cod:
            messagebox.showerror('Erro', 'Item já adicionado ao pedido', parent=j)
            return

    total = venda_val * qtd_val
    item = {
        'cod': cod,
        'nome': nome,
        'preco_venda': venda_val,
        'qtd': qtd_val,
        'total': total
    }
    itens.append(item)
    atualizarItensLista()
    atualizarValorTotal()
    j.destroy()


def totalItem(e, v, q, t):
    # Calcula o total do item (preço x quantidade)
    try:
        venda = float(v.get())
        qtd = float(q.get())
    except:
        t.configure(state='normal')
        t.delete(0, tk.END)
        t.configure(state='disabled')
    else:
        total = venda * qtd
        t.configure(state='normal')
        t.delete(0, tk.END)
        t.insert(0, f'R$ {total:.2f}')
        t.configure(state='disabled')


def itemAvulso():
    # Janela pra adicionar item que não tá no estoque
    janela = tk.Toplevel(root)
    janela.title('MELLK - Adicionar Item Avulso')
    janela.geometry('400x300')
    janela.configure(bg='#1A3C34')
    janela.resizable(False, False)
    janela.grab_set()

    # Centraliza a janela
    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - 400) // 2
    pos_y = (altura_tela - 300) // 2
    janela.geometry(f'400x300+{pos_x}+{pos_y}')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    num_float = (janela.register(entryNumFloat), '%P')

    nome = tk.Entry(frame, font=fonte, width=30)
    venda = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    qtd = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    total = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')

    tk.Label(frame, text='Nome:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    nome.pack(pady=2)
    tk.Label(frame, text='Valor de Venda:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    venda.pack(pady=2)
    tk.Label(frame, text='Quantidade:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    qtd.insert(0, '1.00')
    qtd.pack(pady=2)
    tk.Label(frame, text='Total:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    total.pack(pady=2)

    venda.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))
    qtd.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))

    dados = [nome, venda, qtd]

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Adicionar', command=lambda: addItemAvulso(dados, janela), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)


def addItemAvulso(dados, j):
    # Adiciona item avulso à venda
    global itens

    nome = dados[0].get()
    venda = dados[1].get()
    qtd = dados[2].get()

    if not nome or not venda or not qtd:
        messagebox.showerror('Erro', 'Preencha todos os campos do item', parent=j)
        return

    try:
        venda_val = float(venda)
        qtd_val = float(qtd)
    except ValueError:
        messagebox.showerror('Erro', 'Valores de venda ou quantidade inválidos', parent=j)
        return

    item = {
        'univ_cod': None,
        'cod': 'Avulso',
        'nome': nome,
        'preco_venda': venda_val,
        'qtd': qtd_val,
        'total': venda_val * qtd_val
    }
    itens.append(item)
    atualizarItensLista()
    atualizarValorTotal()
    j.destroy()


def excluirItem(l, f):
    # Remove um item da venda
    global itens

    try:
        ind = int(l.focus())
    except:
        messagebox.showerror('Erro', 'Selecione um item pra remover', parent=f)
        return

    item = itens[ind]
    confirm = messagebox.askokcancel('Confirmar', f'Tem certeza que deseja remover o item {item["nome"]}?', parent=f)
    if confirm:
        itens.pop(ind)
        atualizarItensLista()
        atualizarValorTotal()


def cancelarVenda(f):
    # Cancela a venda e volta pra tela inicial
    global num_venda
    confirm = messagebox.askyesno('Cancelar', f'Tem certeza que deseja cancelar a venda N°{num_venda}?', parent=f)
    if confirm:
        root.geometry('1000x500')
        f.destroy()
        frameInicial.tkraise()


def atualizarItensLista():
    # Atualiza a tabela de itens na tela
    global itensLista, itens

    for i in itensLista.get_children():
        itensLista.delete(i)

    for item in itens:
        itensLista.insert('', 'end', iid=itens.index(item), values=(
            item['cod'],
            item['nome'],
            f"{item['preco_venda']:.2f}",
            f"{item['qtd']:.2f}",
            f"{item['total']:.2f}",
        ))


def atualizarValorTotal():
    # Atualiza o valor total mostrado na tela
    global itens, valorTotal, valorTotalLabel
    valorTotal = sum(item['total'] for item in itens)
    valorTotalLabel.configure(text=f'R$ {valorTotal:.2f}')


def procurarItem(d, j):
    # Janela pra buscar itens no estoque
    estq = receberEstoque()

    janela = tk.Toplevel(j)
    janela.title('MELLK - Procurar Item')
    janela.geometry('700x700')
    janela.configure(bg='#1A3C34')
    janela.state('zoomed')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)

    cod = tk.Entry(frame, font=fonte, width=30)
    nome = tk.Entry(frame, font=fonte, width=30)
    obs = tk.Entry(frame, font=fonte, width=30)

    tk.Label(frame, text='Código:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    cod.pack(pady=2)
    tk.Label(frame, text='Nome do produto:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    nome.pack(pady=2)
    tk.Label(frame, text='Obs.:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    obs.pack(pady=2)

    pesq = [cod, nome, obs]

    dados = ['cod', 'nome', 'preco_venda', 'qtd', 'obs']
    tabela = ttk.Treeview(frame, columns=dados, show='headings', height=15)
    tabela.heading('cod', text='Código')
    tabela.heading('nome', text='Nome')
    tabela.heading('preco_venda', text='Valor Unit.')
    tabela.heading('qtd', text='Disponível')
    tabela.heading('obs', text='Observação')
    tabela.column('cod', width=100)
    tabela.column('nome', width=300)
    tabela.column('preco_venda', width=100)
    tabela.column('qtd', width=100)
    tabela.column('obs', width=200)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    tabela.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    def procurar(tabela, pesq, estq):
        cod = pesq[0].get()
        nome = pesq[1].get().upper()
        obs = pesq[2].get().upper()
        result = [
            item for item in estq
            if (cod == '' or cod in str(item['cod'])) and
               (nome == '' or nome in item['nome'].upper()) and
               (obs == '' or obs in item['obs'].upper())
        ]

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

    def selecionar(tabela, estq, d, j, e=None):
        if tabela.focus():
            cod = int(tabela.focus())
            for item in estq:
                if cod == item['cod']:
                    d[0].configure(state='normal')
                    d[0].delete(0, tk.END)
                    d[0].insert(0, item['cod'])
                    d[0].configure(state='disabled')
                    d[1].configure(state='normal')
                    d[1].delete(0, tk.END)
                    d[1].insert(0, item['nome'])
                    d[1].configure(state='disabled')
                    d[2].delete(0, tk.END)
                    d[2].insert(0, f'{item["preco_venda"]:.2f}')
                    d[4].configure(state='normal')
                    d[4].delete(0, tk.END)
                    d[4].insert(0, f'{item["preco_venda"] * float(d[3].get()):.2f}')
                    d[4].configure(state='disabled')
                    d[5].configure(state='normal')
                    d[5].delete(0, tk.END)
                    d[5].insert(0, f'{item["qtd"]:.2f}')
                    d[5].configure(state='disabled')
                    j.destroy()

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Procurar', command=lambda: procurar(tabela, pesq, estq), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Selecionar', command=lambda: selecionar(tabela, estq, d, janela),
              **button_style).pack(side=tk.LEFT, padx=5)
    tabela.bind('<Double-1>', lambda event: selecionar(tabela, estq, d, janela, event))

    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)


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


def validar_data(data_str):
    if not data_str:
        return True
    try:
        datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False


def exportar_vendas_pdf(vendas, data_inicio='', data_fim=''):
    arq = 'relatorio_vendas.pdf'
    page_size = (595, 842)
    pdf = canvas.Canvas(arq, pagesize=page_size)
    largura, altura = page_size
    margem = 20
    pdf.setFont('Courier', 10)
    pdf.setTitle('Relatório de Vendas')
    y = altura - margem - 20

    def linha(t, s=12, centro=False):
        nonlocal y
        if y < margem + 30:
            pdf.showPage()
            pdf.setFont('Courier', 10)
            y = altura - margem - 20
        if centro:
            pdf.drawCentredString(largura / 2, y, t)
        else:
            pdf.drawString(margem, y, t)
        y -= s

    pdf.setFont('Courier-Bold', 12)
    linha('RELATÓRIO DE VENDAS', centro=True, s=15)
    pdf.setFont('Courier', 10)
    periodo = f'Período: {data_inicio} a {data_fim}' if data_inicio and data_fim else 'Período: Todas as Vendas'
    linha(periodo)
    linha('-' * 80, s=12)
    linha(f'{"N°":<6}{"Cliente":<20}{"Telefone":<15}{"Data":<12}{"Total":>12}')
    linha('-' * 80)
    for venda in vendas:
        cliente = venda['cliente']['nome'][:19]
        telefone = venda['cliente']['telefone'][:14]
        data = venda.get('data', 'N/A')
        total = f"R$ {venda['total']:.2f}"
        linha(f"{venda['num_venda']:<6}{cliente:<20}{telefone:<15}{data:<12}{total:>12}")
    linha('-' * 80, s=10)
    total_vendas = sum(venda['total'] for venda in vendas)
    linha(f'Total Geral: R$ {total_vendas:.2f}', s=10)
    pdf.save()
    try:
        os.startfile(arq)
    except:
        messagebox.showinfo('Sucesso', f'Relatório salvo em {arq}')


def receberVendas():
    try:
        with open('vendas.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)
    except FileNotFoundError:
        return []


def gerarRecibo(venda, troco=0):
    arq = f'recibo_venda{venda["num_venda"]}.pdf'
    page_size = (227, 280)
    recibo = canvas.Canvas(arq, pagesize=page_size)
    largura, altura = page_size
    margem = 10
    recibo.setFont('Courier', 6)
    recibo.setTitle(f'Recibo de Venda N°{venda["num_venda"]}')
    y = altura - margem - 20

    def linha(t, s=10, centro=False):
        nonlocal y
        if y < margem + 20:
            recibo.showPage()
            recibo.setFont('Courier', 8)
            y = altura - margem - 20
        if centro:
            recibo.drawCentredString(largura / 2, y, t)
        else:
            recibo.drawString(margem, y, t)
        y -= s

    recibo.setFont('Courier-Bold', 10)
    linha(f'RECIBO VENDA {venda["num_venda"]}', centro=True, s=12)
    recibo.setFont('Courier', 8)
    linha(f'Data: {venda["data"]}', s=10)
    linha('-' * 40, s=10)
    linha(f'CLIENTE: {venda["cliente"]["nome"][:20]:<20}')
    linha(f'CPF/CNPJ: {venda["cliente"]["cpf_cnpj"]:<20}')
    linha('-' * 40, s=10)
    linha(f'{"ITEM":<20}{"VAL":>8}{"QTD":>6}{"TOTAL":>8}')
    linha('-' * 40, s=8)
    for item in venda['itens']:
        nome = item['nome'][:20]
        valor = float(item['preco_venda'])
        qtd = float(item['qtd'])
        total = float(item['total'])
        linha(f'{nome:<20}{valor:>8.2f}{qtd:>6.1f}{total:>8.2f}')
    total_final = float(venda['total'])
    linha('-' * 40, s=10)
    linha(f'{"BRUTO:":>26} R${venda["bruto"]:>8.2f}')
    linha(f'{"DESCONTO:":>26} R${venda["desconto"]:>8.2f}')
    linha(f'{"FINAL:":>26} R${total_final:>8.2f}')
    linha('-' * 40, s=8)
    linha('PAGAMENTOS', centro=True)
    linha('-' * 40, s=8)
    linha(f'{"TIPO":<15}{"VALOR":>10}')
    linha('-' * 40, s=8)
    for k, v in venda['pagamento'].items():
        forma = k
        valor = 0
        if forma == 'Credito':
            for pag in v:
                valor = float(pag['valor'])
                linha(f'{forma[:15]:<15}{valor:>10.2f}')
        elif forma == 'Pix' or forma == 'Debito':
            valor = sum(v)
            if valor > 0:
                linha(f'{forma[:15]:<15}{valor:>10.2f}')
        else:
            valor = v
            if valor > 0:
                linha(f'{forma[:15]:<15}{valor:>10.2f}')
    linha('-' * 40, s=8)
    linha(f'{"TROCO:":<15} R${troco:>10.2f}')
    recibo.setFont('Courier', 6)
    recibo.save()
    os.startfile(arq)


def listar_vendas():
    janela = tk.Toplevel(root)
    janela.title('MELLK - Listar Vendas')
    janela.state('zoomed')
    janela.configure(bg='#1A3C34')
    janela.grab_set()
    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    fonte_bold = ('Arial', 14, 'bold')

    # Cabeçalho
    header_frame = tk.Frame(frame, bg='#1A3C34')
    header_frame.pack(pady=10, fill='x')
    tk.Label(header_frame, text='Listar Vendas', font=fonte_bold, fg='white', bg='#1A3C34').pack()

    # Filtros
    filter_frame = tk.Frame(frame, bg='#1A3C34')
    filter_frame.pack(pady=10, fill='x', padx=20)

    tk.Label(filter_frame, text='N° Venda:', font=fonte, fg='white', bg='#1A3C34').grid(row=0, column=0, padx=5,
                                                                                        sticky='e')
    num_pesq = tk.Entry(filter_frame, font=fonte, width=10, validate='key',
                        validatecommand=(janela.register(entryNumInt), '%P'))
    num_pesq.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(filter_frame, text='Nome Cliente:', font=fonte, fg='white', bg='#1A3C34').grid(row=0, column=2, padx=5,
                                                                                            sticky='e')
    nome_pesq = tk.Entry(filter_frame, font=fonte, width=20)
    nome_pesq.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(filter_frame, text='Telefone:', font=fonte, fg='white', bg='#1A3C34').grid(row=0, column=4, padx=5,
                                                                                        sticky='e')
    telefone_pesq = tk.Entry(filter_frame, font=fonte, width=15)
    telefone_pesq.grid(row=0, column=5, padx=5, pady=5)

    tk.Label(filter_frame, text='Data Início (DD/MM/AAAA):', font=fonte, fg='white', bg='#1A3C34').grid(row=1, column=0,
                                                                                                        padx=5,
                                                                                                        sticky='e')
    data_inicio = tk.Entry(filter_frame, font=fonte, width=12)
    data_inicio.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(filter_frame, text='Data Fim (DD/MM/AAAA):', font=fonte, fg='white', bg='#1A3C34').grid(row=1, column=2,
                                                                                                     padx=5, sticky='e')
    data_fim = tk.Entry(filter_frame, font=fonte, width=12)
    data_fim.grid(row=1, column=3, padx=5, pady=5)

    # Tabela
    colunas = ['num_venda', 'cliente_nome', 'cliente_telefone', 'data', 'total', 'status']
    lista = ttk.Treeview(frame, columns=colunas, show='headings', height=15)
    lista.heading('num_venda', text='N°')
    lista.heading('cliente_nome', text='Cliente')
    lista.heading('cliente_telefone', text='Telefone')
    lista.heading('data', text='Data')
    lista.heading('total', text='Total')
    lista.heading('status', text='Status')
    lista.column('num_venda', width=50)
    lista.column('cliente_nome', width=250)
    lista.column('cliente_telefone', width=150)
    lista.column('data', width=100)
    lista.column('total', width=100)
    lista.column('status', width=100)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=lista.yview)
    lista.configure(yscrollcommand=scrollbar.set)
    lista.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    def pesquisar_venda(e=None):
        num = num_pesq.get()
        nome = nome_pesq.get().upper()
        telefone = ''.join(n for n in telefone_pesq.get() if n.isdigit())
        inicio = data_inicio.get()
        fim = data_fim.get()
        if not validar_data(inicio) or not validar_data(fim):
            messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA', parent=janela)
            return
        try:
            num = int(num) if num else None
            inicio_dt = datetime.strptime(inicio, '%d/%m/%Y') if inicio else None
            fim_dt = datetime.strptime(fim, '%d/%m/%Y') if fim else None
        except ValueError:
            messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA', parent=janela)
            return
        vendas = receberVendas()
        resultados = []
        for venda in vendas:
            tel_cliente = ''.join(n for n in venda['cliente']['telefone'] if n.isdigit())
            data_venda = venda.get('data', '')
            try:
                data_venda_dt = datetime.strptime(data_venda, '%d/%m/%Y') if data_venda else None
            except ValueError:
                data_venda_dt = None
            if (
                    (num is None or venda['num_venda'] == num) and
                    (not nome or nome in venda['cliente']['nome'].upper()) and
                    (not telefone or telefone in tel_cliente) and
                    (not inicio_dt or (data_venda_dt and data_venda_dt >= inicio_dt)) and
                    (not fim_dt or (data_venda_dt and data_venda_dt <= fim_dt))
            ):
                resultados.append(venda)
        for item in lista.get_children():
            lista.delete(item)
        for venda in resultados:
            status = 'Crédito' if venda['pagamento'].get('Credito') else 'Pago'
            lista.insert('', 'end', iid=venda['num_venda'], values=(
                venda['num_venda'],
                venda['cliente']['nome'],
                venda['cliente']['telefone'],
                venda.get('data', 'N/A'),
                f'R$ {venda["total"]:.2f}',
                status
            ))
        return resultados

    def excluir_venda():
        try:
            num = int(lista.focus())
        except:
            messagebox.showerror('Erro', 'Selecione uma venda para excluir', parent=janela)
            return
        confirm = messagebox.askyesno('Excluir', f'Tem certeza que deseja excluir a venda N°{num}?', parent=janela)
        if confirm:
            vendas = receberVendas()
            vendas = [v for v in vendas if v['num_venda'] != num]
            with open('vendas.json', 'w', encoding='utf-8') as arq:
                json.dump(vendas, arq, indent=4, ensure_ascii=False)
            pesquisar_venda()
            messagebox.showinfo('Sucesso', f'Venda N°{num} excluída', parent=janela)

    def abrir_venda(e=None):
        try:
            num_venda = int(lista.focus())
        except:
            return
        vendas = receberVendas()
        venda = next((v for v in vendas if v['num_venda'] == num_venda), None)
        if not venda:
            messagebox.showerror('Erro', 'Venda não encontrada', parent=janela)
            return
        detalhe_janela = tk.Toplevel(janela)
        detalhe_janela.title(f'Venda N°{num_venda}')
        detalhe_janela.geometry('1000x700')
        detalhe_janela.configure(bg='#1A3C34')
        detalhe_janela.grab_set()

        detalhe_frame = tk.Frame(detalhe_janela, bg='#1A3C34')
        detalhe_frame.pack(fill='both', expand=True, padx=10, pady=10)

        info_frame = tk.Frame(detalhe_frame, bg='#1A3C34')
        info_frame.pack(fill='x', pady=10)
        tk.Label(info_frame, text=f'Venda N°{num_venda} - Cliente: {venda["cliente"]["nome"]}', font=fonte_bold,
                 fg='white', bg='#1A3C34').pack(anchor='w')
        tk.Label(info_frame, text=f'Data: {venda.get("data", "N/A")}', font=fonte, fg='white', bg='#1A3C34').pack(
            anchor='w')
        tk.Label(info_frame, text=f'Telefone: {venda["cliente"]["telefone"]}', font=fonte, fg='white',
                 bg='#1A3C34').pack(anchor='w')
        tk.Label(info_frame, text=f'CPF/CNPJ: {venda["cliente"]["cpf_cnpj"]}', font=fonte, fg='white',
                 bg='#1A3C34').pack(anchor='w')
        tk.Label(info_frame, text=f'CEP: {venda["cliente"]["cep"]}', font=fonte, fg='white', bg='#1A3C34').pack(
            anchor='w')
        tk.Label(info_frame, text=f'N° Casa: {venda["cliente"]["num_casa"]}', font=fonte, fg='white',
                 bg='#1A3C34').pack(anchor='w')
        tk.Label(info_frame, text=f'E-mail: {venda["cliente"]["email"]}', font=fonte, fg='white', bg='#1A3C34').pack(
            anchor='w')
        tk.Label(info_frame, text=f'Valor Bruto: R$ {venda["bruto"]:.2f}', font=fonte, fg='white', bg='#1A3C34').pack(
            anchor='w')
        tk.Label(info_frame, text=f'Desconto: R$ {venda["desconto"]:.2f}', font=fonte, fg='white', bg='#1A3C34').pack(
            anchor='w')
        tk.Label(info_frame, text=f'Total: R$ {venda["total"]:.2f}', font=fonte, fg='white', bg='#1A3C34').pack(
            anchor='w')

        tk.Label(detalhe_frame, text='Itens', font=fonte_bold, fg='white', bg='#1A3C34').pack(anchor='w', pady=5)
        colunas_itens = ['cod', 'nome', 'preco_venda', 'qtd', 'total']
        lista_itens = ttk.Treeview(detalhe_frame, columns=colunas_itens, show='headings')
        lista_itens.heading('cod', text='Cód.')
        lista_itens.heading('nome', text='Nome')
        lista_itens.heading('preco_venda', text='Valor Unit.')
        lista_itens.heading('qtd', text='Qtd.')
        lista_itens.heading('total', text='Total')
        lista_itens.column('cod', width=100)
        lista_itens.column('nome', width=300)
        lista_itens.column('preco_venda', width=100)
        lista_itens.column('qtd', width=100)
        lista_itens.column('total', width=100)
        lista_itens.pack(fill='both', expand=True, padx=10, pady=10)
        for item in venda['itens']:
            lista_itens.insert('', 'end', values=(
                item['cod'],
                item['nome'],
                f'R$ {item["preco_venda"]:.2f}',
                f'{item["qtd"]:.2f}',
                f'R$ {item["total"]:.2f}'
            ))

        tk.Label(detalhe_frame, text='Formas de Pagamento', font=fonte_bold, fg='white', bg='#1A3C34').pack(anchor='w',
                                                                                                            pady=5)
        colunas_pag = ['forma', 'valor', 'obs']
        lista_pag = ttk.Treeview(detalhe_frame, columns=colunas_pag, show='headings', height=5)
        lista_pag.heading('forma', text='Forma')
        lista_pag.heading('valor', text='Valor')
        lista_pag.heading('obs', text='Observação')
        lista_pag.column('forma', width=150)
        lista_pag.column('valor', width=100)
        lista_pag.column('obs', width=200)
        lista_pag.pack(fill='x', padx=10, pady=5)
        for forma, valor in venda['pagamento'].items():
            if forma == 'Credito':
                for p in valor:
                    lista_pag.insert('', 'end', values=(
                        'Cartão de Crédito',
                        f'R$ {p["valor"]:.2f}',
                        f'Parcelas: {p["parcelas"]}'
                    ))
            elif forma == 'Pix' or forma == 'Debito':
                if sum(valor) > 0:
                    lista_pag.insert('', 'end', values=(
                        forma,
                        f'R$ {sum(valor):.2f}',
                        ''
                    ))
            elif valor > 0:
                lista_pag.insert('', 'end', values=(
                    forma,
                    f'R$ {valor:.2f}',
                    ''
                ))

        button_frame = tk.Frame(detalhe_frame, bg='#1A3C34')
        button_frame.pack(pady=10)
        tk.Button(button_frame, text='Gerar Recibo', command=lambda: gerarRecibo(venda), **button_style).pack(
            side=tk.LEFT, padx=5)
        tk.Button(button_frame, text='Excluir', command=lambda: [excluir_venda(), detalhe_janela.destroy()],
                  **button_style).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text='Fechar', command=detalhe_janela.destroy, **button_style).pack(side=tk.LEFT,
                                                                                                    padx=5)

    def exportar_vendas():
        resultados = pesquisar_venda()
        exportar_vendas_pdf(resultados, data_inicio.get(), data_fim.get())

    # Botões de ação
    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Pesquisar', command=pesquisar_venda, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Gerar Relatório', command=exportar_vendas, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Abrir Venda', command=abrir_venda, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Excluir', command=excluir_venda, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Fechar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)

    # Bindings
    num_pesq.bind('<Return>', pesquisar_venda)
    nome_pesq.bind('<Return>', pesquisar_venda)
    telefone_pesq.bind('<Return>', pesquisar_venda)
    data_inicio.bind('<Return>', pesquisar_venda)
    data_fim.bind('<Return>', pesquisar_venda)
    lista.bind('<Double-1>', abrir_venda)
    lista.bind('<Return>', abrir_venda)

    # Carregar vendas iniciais
    pesquisar_venda()


def novoOrcamento():
    global num_orcamento, cliente, itens, itensLista, valorTotal, valorTotalLabel
    itens = []
    valorTotal = 0.0

    try:
        with open('orcamentos.json', 'r', encoding='utf-8') as arq:
            orcamentos = json.load(arq)
        num_orcamento = 1 if not orcamentos else orcamentos[-1].get('num_orcamento', 0) + 1
    except (FileNotFoundError, json.JSONDecodeError):
        num_orcamento = 1

    # Janela para selecionar cliente ou prosseguir sem cliente
    janela = tk.Toplevel(root)
    janela.transient(root)
    janela.grab_set()
    janela.title('MELLK - Novo Orçamento')
    janela.geometry('900x400')
    janela.configure(bg='#1A3C34')

    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - 900) // 2
    pos_y = (altura_tela - 400) // 2
    janela.geometry(f'900x400+{pos_x}+{pos_y}')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    tk.Label(frame, text='Selecionar Cliente para Orçamento', font=('Arial', 14, 'bold'), fg='white',
             bg='#1A3C34').pack(pady=10)

    search_frame = tk.Frame(frame, bg='#1A3C34')
    search_frame.pack(pady=10, fill='x', padx=20)
    tk.Label(search_frame, text='Pesquisar por:', font=('Arial', 12), fg='white', bg='#1A3C34').pack()
    opc = ttk.Combobox(search_frame, values=['Nome', 'Telefone', 'CPF/CNPJ'], state='readonly', font=('Arial', 12))
    opc.set('Nome')
    opc.pack(pady=5)
    pesquisa = tk.Entry(search_frame, font=('Arial', 12), width=30)
    pesquisa.pack(pady=5)

    dados = ['cod', 'nome', 'telefone', 'cpf_cnpj']
    lista = ttk.Treeview(frame, columns=dados, show='headings', height=10)
    lista.heading('cod', text='Cód.')
    lista.heading('nome', text='Nome')
    lista.heading('telefone', text='Telefone')
    lista.heading('cpf_cnpj', text='CPF/CNPJ')
    lista.column('cod', width=100)
    lista.column('nome', width=300)
    lista.column('telefone', width=150)
    lista.column('cpf_cnpj', width=150)
    scrollbar = ttk.Scrollbar(frame, orient='vertical', command=lista.yview)
    lista.configure(yscrollcommand=scrollbar.set)
    lista.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Procurar', command=lambda: buscaCliente(janela, opc, pesquisa, lista),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Sem Cliente', command=lambda: selecionarSemCliente(janela), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Selecionar', command=lambda: selecionarClienteOrcamento(janela, lista),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)
    janela.bind('<Return>', lambda event: buscaCliente(janela, opc, pesquisa, lista, event))
    lista.bind('<Double-1>', lambda event: selecionarClienteOrcamento(janela, lista))


def selecionarSemCliente(janela):
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
    janela.destroy()
    criarOrcamento()


def selecionarClienteOrcamento(janela, lista):
    global cliente
    clientes = receberClientes()
    try:
        codCliente = int(lista.focus())
        for c in clientes:
            if c['cod'] == codCliente:
                cliente = c
                janela.destroy()
                criarOrcamento()
                break
    except:
        messagebox.showerror('Erro', 'Selecione um cliente válido', parent=janela)


def criarOrcamento():
    global num_orcamento, itens, itensLista, valorTotal, valorTotalLabel
    root.geometry('1000x700')
    frame = tk.Frame(root, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    fonte_bold = ('Arial', 14, 'bold')

    header_frame = tk.Frame(frame, bg='#1A3C34')
    header_frame.pack(pady=10, fill='x')
    tk.Label(header_frame, text=f'Orçamento N°{num_orcamento} - Cliente: {cliente["nome"]}', font=fonte_bold,
             fg='white', bg='#1A3C34').pack()

    cliente_frame = tk.Frame(frame, bg='#1A3C34')
    cliente_frame.pack(pady=10, fill='x', padx=20)
    tk.Label(cliente_frame, text=f'Telefone: {cliente["telefone"]}', font=fonte, fg='white', bg='#1A3C34').pack(
        anchor='w')
    tk.Label(cliente_frame, text=f'CPF/CNPJ: {cliente["cpf_cnpj"]}', font=fonte, fg='white', bg='#1A3C34').pack(
        anchor='w')
    tk.Label(cliente_frame, text=f'CEP: {cliente["cep"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')
    tk.Label(cliente_frame, text=f'N°: {cliente["num_casa"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')
    tk.Label(cliente_frame, text=f'E-mail: {cliente["email"]}', font=fonte, fg='white', bg='#1A3C34').pack(anchor='w')

    item_frame = tk.Frame(frame, bg='#1A3C34')
    item_frame.pack(pady=10, fill='x', padx=20)

    tk.Label(item_frame, text='Código:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    cod_entry = tk.Entry(item_frame, font=fonte, width=10, bg='#E5E5E5', fg='#000000', insertbackground='#000000')
    cod_entry.pack(side=tk.LEFT, padx=5)

    tk.Label(item_frame, text='Quantidade:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT, padx=(10, 5))
    qtd_entry = tk.Entry(item_frame, font=fonte, width=10, bg='#E5E5E5', fg='#000000', insertbackground='#000000')
    qtd_entry.insert(0, '1.00')
    qtd_entry.pack(side=tk.LEFT, padx=5)

    tk.Label(item_frame, text='Nome do Produto:', font=fonte, fg='white', bg="#1A3C34").pack(side=tk.LEFT, padx=(10, 5))
    nome_label = tk.Label(item_frame, text='', font=fonte, fg='white', bg='#3b3b3b', width=30, relief="sunken", bd=3)
    nome_label.pack(side=tk.LEFT, padx=5)

    tk.Label(item_frame, text='Valor Unit.:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT, padx=(10, 5))
    preco_label = tk.Label(item_frame, text='', font=fonte, fg='white', bg='#3b3b3b', width=10, relief="sunken", bd=3)
    preco_label.pack(side=tk.LEFT, padx=5)

    tk.Label(item_frame, text='Disponível:', font=fonte, fg='white', bg='#1A3C34').pack(side=tk.LEFT, padx=(10, 5))
    disp_label = tk.Label(item_frame, text='', font=fonte, fg='white', bg='#3b3b3b', width=10, relief="sunken", bd=3)
    disp_label.pack(side=tk.LEFT, padx=5)

    tk.Button(item_frame, text='Adicionar',
              command=lambda: adicionarItemPorCodigoOrcamento(cod_entry, nome_label, preco_label, qtd_entry, disp_label,
                                                              frame), **button_style).pack(side=tk.LEFT, padx=5)

    cod_entry.bind('<KeyRelease>', lambda event: item_por_cod(event, cod_entry, nome_label, preco_label, disp_label))
    cod_entry.bind('<Return>',
                   lambda event: adicionarItemPorCodigoOrcamento(cod_entry, nome_label, preco_label, qtd_entry,
                                                                 disp_label, frame))

    total_frame = tk.Frame(frame, bg='#1A3C34')
    total_frame.pack(pady=10)
    tk.Label(total_frame, text='Valor Total:', font=fonte_bold, fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    valorTotalLabel = tk.Label(total_frame, text=f'R$ {valorTotal:.2f}', font=fonte_bold, fg='white', bg='#1A3C34',
                               bd=1, relief="raised")
    valorTotalLabel.pack(side=tk.LEFT, padx=5)

    table_frame = tk.Frame(frame, bg='#1A3C34')
    table_frame.pack(fill='both', expand=True, padx=20, pady=10)

    colunas = ['cod', 'nome', 'preco_venda', 'qtd', 'total']
    itensLista = ttk.Treeview(table_frame, columns=colunas, show='headings', height=10)
    itensLista.heading('cod', text='Código')
    itensLista.heading('nome', text='Nome')
    itensLista.heading('preco_venda', text='Valor Unit.')
    itensLista.heading('qtd', text='Qtd')
    itensLista.heading('total', text='Total')
    itensLista.column('cod', width=100)
    itensLista.column('nome', width=300)
    itensLista.column('preco_venda', width=100)
    itensLista.column('qtd', width=100)
    itensLista.column('total', width=100)

    scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=itensLista.yview)
    itensLista.configure(yscrollcommand=scrollbar.set)
    itensLista.pack(side=tk.LEFT, fill='both', expand=True)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Add. Item do Estoque', command=lambda: itemEstoqueOrcamento(frame),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Add. Item Avulso', command=lambda: itemAvulsoOrcamento(frame), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Excluir Item', command=lambda: excluirItemOrcamento(itensLista, frame),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar Orçamento', command=lambda: cancelarOrcamento(frame), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Finalizar Orçamento', command=lambda: finalizarOrcamento(frame), **button_style).pack(
        side=tk.LEFT, padx=5)

    itensLista.bind('<Delete>', lambda event: excluirItemOrcamento(itensLista, frame))


def adicionarItemPorCodigoOrcamento(cod_entry, nome_label, preco_label, qtd_entry, disp_label, parent):
    global itens
    estoque = receberEstoque()
    cod = cod_entry.get()
    nome = nome_label['text']
    preco = preco_label['text'].replace('R$ ', '') if preco_label['text'] else ''
    qtd = qtd_entry.get()

    if not cod or not nome or not preco or not qtd:
        messagebox.showerror('Erro', 'Preencha ou selecione um item válido', parent=parent)
        return

    try:
        cod_val = int(cod)
        preco_val = float(preco)
        qtd_val = float(qtd)
    except (ValueError):
        messagebox.showerror('Erro', 'Valores inválidos para preço ou quantidade', parent=parent)
        return

    if qtd_val <= 0:
        messagebox.showerror('Erro', 'A quantidade deve ser maior que zero', parent=parent)
        return

    total = preco_val * qtd_val
    for item in itens:
        if item['cod'] == cod:
            messagebox.showerror('Erro', 'Item já adicionado ao orçamento', parent=parent)
            return

    for i in estoque:
        if cod_val == i['cod']:
            univ_cod = i['univ_cod']
            break
    else:
        univ_cod = ''

    item = {
        'univ_cod': univ_cod,
        'cod': cod,
        'nome': nome,
        'preco_venda': preco_val,
        'qtd': qtd_val,
        'total': total
    }
    itens.append(item)
    atualizarItensListaOrcamento()
    atualizarValorTotalOrcamento()

    cod_entry.delete(0, tk.END)
    nome_label.config(text='')
    preco_label.config(text='')
    qtd_entry.delete(0, tk.END)
    qtd_entry.insert(0, '1.00')
    disp_label.config(text='')


def itemEstoqueOrcamento(parent):
    janela = tk.Toplevel(root)
    janela.title('MELLK - Adicionar Item do Estoque ao Orçamento')
    janela.configure(bg='#1A3C34')
    janela.resizable(False, False)
    janela.grab_set()

    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - 400) // 2
    pos_y = (altura_tela - 400) // 2
    janela.geometry(f'400x500+{pos_x}+{pos_y}')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    num_float = (janela.register(entryNumFloat), '%P')

    cod = tk.Entry(frame, font=fonte, width=30)
    nome = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')
    venda = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    qtd = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    total = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')
    disp = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')

    tk.Label(frame, text='Código do produto:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    cod.pack(pady=2)
    tk.Label(frame, text='Item:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    nome.pack(pady=2)
    tk.Label(frame, text='Valor:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    venda.pack(pady=2)
    tk.Label(frame, text='Quantidade:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    qtd.pack(pady=2)
    tk.Label(frame, text='Total:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    total.pack(pady=2)
    tk.Label(frame, text='Disponível:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    disp.pack(pady=2)

    cod.bind('<KeyRelease>', lambda event: item_por_cod(event, cod, nome, venda, disp))
    cod.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))
    venda.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))
    qtd.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))

    dados = [cod, nome, venda, qtd, total, disp]

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Procurar', command=lambda: procurarItem(dados, janela), **button_style).pack(
        side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Adicionar', command=lambda: addItemEstoqueOrcamento(dados, janela, parent),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)


def addItemEstoqueOrcamento(dados, janela, parent):
    global itens
    cod = dados[0].get()
    nome = dados[1].get()
    venda = dados[2].get()
    qtd = dados[3].get()
    disp = dados[5].get()

    if not cod or not nome or not venda or not qtd:
        messagebox.showerror('Erro', 'Preencha todos os campos do item', parent=janela)
        return

    try:
        venda_val = float(venda)
        qtd_val = float(qtd)
        disp_val = float(disp) if disp else 0
    except ValueError:
        messagebox.showerror('Erro', 'Valores de venda ou quantidade inválidos', parent=janela)
        return

    if qtd_val <= 0:
        messagebox.showerror('Erro', 'A quantidade deve ser maior que zero', parent=janela)
        return

    if qtd_val > disp_val:
        messagebox.showwarning('Aviso',
                               f'Quantidade solicitada ({qtd_val}) excede o estoque disponível ({disp_val}). O item será adicionado mesmo assim.',
                               parent=janela)

    for i in itens:
        if i['cod'] == cod:
            messagebox.showerror('Erro', 'Item já adicionado ao orçamento', parent=janela)
            return

    total = venda_val * qtd_val
    item = {
        'univ_cod': cod,
        'cod': cod,
        'nome': nome,
        'preco_venda': venda_val,
        'qtd': qtd_val,
        'total': total
    }
    itens.append(item)
    atualizarItensListaOrcamento()
    atualizarValorTotalOrcamento()
    janela.destroy()


def itemAvulsoOrcamento(parent):
    janela = tk.Toplevel(root)
    janela.title('MELLK - Adicionar Item Avulso ao Orçamento')
    janela.geometry('400x300')
    janela.configure(bg='#1A3C34')
    janela.resizable(False, False)
    janela.grab_set()

    largura_tela = root.winfo_screenwidth()
    altura_tela = root.winfo_screenheight()
    pos_x = (largura_tela - 400) // 2
    pos_y = (altura_tela - 300) // 2
    janela.geometry(f'400x300+{pos_x}+{pos_y}')

    frame = tk.Frame(janela, bg='#1A3C34')
    frame.place(relx=0, rely=0, relwidth=1, relheight=1)

    fonte = ('Arial', 12)
    num_float = (janela.register(entryNumFloat), '%P')

    nome = tk.Entry(frame, font=fonte, width=30)
    venda = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    qtd = tk.Entry(frame, font=fonte, width=30, validate='key', validatecommand=num_float)
    total = tk.Entry(frame, font=fonte, width=30, state='disabled', disabledbackground='#E5E5E5')

    tk.Label(frame, text='Nome do Item:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    nome.pack(pady=2)
    tk.Label(frame, text='Valor de Venda:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    venda.pack(pady=2)
    tk.Label(frame, text='Quantidade:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    qtd.pack(pady=2)
    qtd.insert(0, '1.00')
    tk.Label(frame, text='Total:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    total.pack(pady=2)

    venda.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))
    qtd.bind('<KeyRelease>', lambda event: totalItem(event, venda, qtd, total))

    dados = [nome, venda, qtd, total]

    def addItemAvulsoOrcamento(dados, janela):
        nome = dados[0].get()
        venda = dados[1].get()
        qtd = dados[2].get()

        if not nome or not venda or not qtd:
            messagebox.showerror('Erro', 'Preencha todos os campos', parent=janela)
            return

        try:
            venda_val = float(venda)
            qtd_val = float(qtd)
        except ValueError:
            messagebox.showerror('Erro', 'Valores de venda ou quantidade inválidos', parent=janela)
            return

        if qtd_val <= 0:
            messagebox.showerror('Erro', 'A quantidade deve ser maior que zero', parent=janela)
            return

        total = venda_val * qtd_val
        item = {
            'univ_cod': None,
            'cod': f'AVULSO_{len(itens) + 1}',
            'nome': nome,
            'preco_venda': venda_val,
            'qtd': qtd_val,
            'total': total
        }
        itens.append(item)
        atualizarItensListaOrcamento()
        atualizarValorTotalOrcamento()
        janela.destroy()

    button_frame = tk.Frame(frame, bg='#1A3C34')
    button_frame.pack(pady=10)
    tk.Button(button_frame, text='Adicionar', command=lambda: addItemAvulsoOrcamento(dados, janela),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Cancelar', command=janela.destroy, **button_style).pack(side=tk.LEFT, padx=5)


def excluirItemOrcamento(lista, parent):
    global itens
    try:
        ind = int(lista.focus())
        item = itens[ind]
        confirm = messagebox.askokcancel('Confirmar', f'Tem certeza que deseja remover o item {item["nome"]}?',
                                         parent=parent)
        if confirm:
            itens.pop(ind)
            atualizarItensListaOrcamento()
            atualizarValorTotalOrcamento()
    except:
        messagebox.showerror('Erro', 'Selecione um item para remover', parent=parent)


def cancelarOrcamento(frame):
    global num_orcamento
    confirm = messagebox.askyesno('Cancelar', f'Tem certeza que deseja cancelar o orçamento N°{num_orcamento}?',
                                  parent=frame)
    if confirm:
        root.geometry('1000x500')
        frame.destroy()
        frameInicial.tkraise()


def atualizarItensListaOrcamento():
    global itensLista, itens
    for i in itensLista.get_children():
        itensLista.delete(i)
    for item in itens:
        itensLista.insert('', 'end', iid=itens.index(item), values=(
            item['cod'],
            item['nome'],
            f"{item['preco_venda']:.2f}",
            f"{item['qtd']:.2f}",
            f"{item['total']:.2f}",
        ))


def atualizarValorTotalOrcamento():
    global itens, valorTotal, valorTotalLabel
    valorTotal = sum(item['total'] for item in itens)
    valorTotalLabel.configure(text=f'R$ {valorTotal:.2f}')


def finalizarOrcamento(frame):
    global num_orcamento, cliente, itens, valorTotal
    if not itens:
        messagebox.showerror('Erro', 'Nenhum item adicionado ao orçamento', parent=frame)
        return

    orcamento = {
        'num_orcamento': num_orcamento,
        'cliente': cliente,
        'itens': itens,
        'total': valorTotal,
        'data': datetime.now().strftime("%d/%m/%Y")
    }

    try:
        with open('orcamentos.json', 'r+', encoding='utf-8') as arq:
            orcamentos = json.load(arq)
            orcamentos.append(orcamento)
            arq.seek(0)
            json.dump(orcamentos, arq, indent=4, ensure_ascii=False)
            arq.truncate()
    except FileNotFoundError:
        with open('orcamentos.json', 'w', encoding='utf-8') as arq:
            json.dump([orcamento], arq, indent=4, ensure_ascii=False)

    recibo = messagebox.askyesno('Recibo', 'Deseja gerar um PDF do orçamento?', parent=frame)
    if recibo:
        gerarReciboOrcamento(orcamento)

    messagebox.showinfo('Sucesso', f'Orçamento N°{num_orcamento} finalizado com sucesso!', parent=frame)
    root.geometry('1000x500')
    frame.destroy()
    frameInicial.tkraise()


def gerarReciboOrcamento(orcamento):
    arq = f'orcamento_{orcamento["num_orcamento"]}.pdf'
    page_size = (227, 280)
    recibo = canvas.Canvas(arq, pagesize=page_size)
    largura, altura = page_size
    margem = 10
    recibo.setFont('Courier', 6)
    recibo.setTitle(f'Orçamento N°{orcamento["num_orcamento"]}')

    y = altura - margem - 20

    def linha(t, s=10, centro=False):
        nonlocal y
        if y < margem + 20:
            recibo.showPage()
            recibo.setFont('Courier', 8)
            y = altura - margem - 20
        if centro:
            recibo.drawCentredString(largura / 2, y, t)
        else:
            recibo.drawString(margem, y, t)
        y -= s

    recibo.setFont('Courier-Bold', 10)
    linha(f'ORÇAMENTO N°{orcamento["num_orcamento"]}', centro=True, s=12)
    recibo.setFont('Courier', 8)
    linha(f'Data: {orcamento["data"]}', s=10)
    linha('-' * 40, s=10)
    linha(f'CLIENTE: {orcamento["cliente"]["nome"][:20]:<20}')
    linha(f'CPF/CNPJ: {orcamento["cliente"]["cpf_cnpj"]:<20}')
    linha('-' * 40, s=10)
    linha(f'{"ITEM":<20}{"VAL":>8}{"QTD":>6}{"TOTAL":>8}')
    linha('-' * 40, s=8)
    for item in orcamento['itens']:
        nome = item['nome'][:20]
        valor = float(item['preco_venda'])
        qtd = float(item['qtd'])
        total = float(item['total'])
        linha(f'{nome:<20}{valor:>8.2f}{qtd:>6.1f}{total:>8.2f}')
    totalfinal = float(orcamento['total'])
    linha('-' * 40, s=10)
    linha(f'{"TOTAL:":>26} R${totalfinal:>8.2f}')
    recibo.setFont('Courier', 6)
    recibo.save()
    try:
        os.startfile(arq)
    except:
        messagebox.showinfo('Sucesso', f'Orçamento salvo em {arq}')

import json
import tkinter as tk
from tkinter import ttk, messagebox

# Índice global para navegação. Inicializei como 0, mas não está sendo usado diretamente aqui,
# mantive para compatibilidade com possíveis expansões ou navegação sequencial.
i = 0

def inicio():
    # Declaro variáveis globais para acessar a tabela, janela principal e código universal
    # em outras funções. Isso centraliza o controle desses elementos.
    global tabela, root, univ_cod

    # Crio a janela principal como Toplevel para integrar com outras partes do sistema
    # (ex.: clientes.py). Defino um tamanho inicial, título e fundo escuro (#1A3C34) para o tema.
    root = tk.Toplevel()
    root.geometry('1500x500')
    root.title('MELLK - Estoque')
    root.configure(bg='#1A3C34')
    root.resizable(True, True)
    root.state("zoomed")  # Maximiza a janela para melhor visualização da tabela.

    # Defino o estilo dos botões em um dicionário para reutilização. Escolhi um visual limpo
    # com fundo branco, texto preto e cursor de mão para indicar interatividade.
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

    # Crio um frame principal para organizar todos os elementos da interface. Ele ocupa
    # toda a janela com posicionamento relativo para ser responsivo.
    frame_estoque = tk.Frame(root, bg='#1A3C34')
    frame_estoque.place(relx=0, rely=0, relwidth=1, relheight=1)

    # Frame para os campos de pesquisa. Usei pack com preenchimento horizontal (fill='x')
    # para alinhar os campos de busca no topo da janela.
    search_frame = tk.Frame(frame_estoque, bg='#1A3C34')
    search_frame.pack(pady=10, fill='x', padx=20)

    # Defino a fonte padrão (Arial, 12) para consistência visual. Registro a função
    # entryNumInt para validar entradas numéricas inteiras nos campos.
    fonte = ('Arial', 12)
    num_int = (frame_estoque.register(entryNumInt), '%P')

    # Campo de pesquisa por código. Adicionei validação para aceitar apenas números inteiros.
    tk.Label(search_frame, text='Código:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    codPesq = tk.Entry(search_frame, font=fonte, width=30, validate='key', validatecommand=num_int)
    codPesq.pack(pady=2)

    # Campo de pesquisa por nome. Sem validação específica, já que aceita texto livre.
    tk.Label(search_frame, text='Nome:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    nomePesq = tk.Entry(search_frame, font=fonte, width=30)
    nomePesq.pack(pady=2)

    # Campo de pesquisa por observações. Também aceita texto livre.
    tk.Label(search_frame, text='Obs.:', font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
    obsPesq = tk.Entry(search_frame, font=fonte, width=30)
    obsPesq.pack(pady=2)

    # Armazeno os campos de pesquisa em uma lista para passar como argumento para as funções
    # de busca e limpeza, facilitando a manipulação.
    pesq = [codPesq, nomePesq, obsPesq]

    # Frame para os botões de ação. Organizei com pack e side=LEFT para alinhá-los horizontalmente.
    action_frame = tk.Frame(frame_estoque, bg='#1A3C34')
    action_frame.pack(pady=10)
    tk.Button(action_frame, text='Procurar', command=lambda: botaoProcurar(pesq), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(action_frame, text='Limpar', command=lambda: limpar(pesq), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(action_frame, text='Novo Item', command=novoItem, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(action_frame, text='Excluir', command=botaoExcluir, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(action_frame, text='Editar', command=editar, **button_style).pack(side=tk.LEFT, padx=5)

    # Vinculo a tecla Enter à função de busca para agilizar a pesquisa sem clicar no botão.
    root.bind('<Return>', lambda event: botaoProcurar(pesq))

    # Configuro a tabela (Treeview) para exibir os itens do estoque. Defini colunas específicas
    # e cabeçalhos claros para cada campo. Ajustei larguras para melhor legibilidade.
    colunas = ['cod', 'nome', 'preco_venda', 'preco_custo', 'lucro', 'qtd', 'obs']
    tabela = ttk.Treeview(frame_estoque, columns=colunas, show='headings', height=15)
    tabela.heading('cod', text='Cód.')
    tabela.heading('nome', text='Descrição')
    tabela.heading('preco_venda', text='Venda')
    tabela.heading('preco_custo', text='Custo')
    tabela.heading('lucro', text='Lucro (%)')
    tabela.heading('qtd', text='Disponível')
    tabela.heading('obs', text='Observação')
    tabela.column('cod', width=100)
    tabela.column('nome', width=300)
    tabela.column('preco_venda', width=100)
    tabela.column('preco_custo', width=100)
    tabela.column('lucro', width=100)
    tabela.column('qtd', width=100)
    tabela.column('obs', width=300)

    # Adicionei uma scrollbar vertical para a tabela, essencial para grandes quantidades de itens.
    scrollbar = ttk.Scrollbar(frame_estoque, orient='vertical', command=tabela.yview)
    tabela.configure(yscrollcommand=scrollbar.set)
    tabela.pack(side=tk.LEFT, fill='both', expand=True, padx=10, pady=10)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    # Vinculo o evento de duplo clique na tabela à função de edição, permitindo editar itens rapidamente.
    tabela.bind('<Double-1>', editar)

    # Carrego os dados iniciais do estoque na tabela ao abrir a janela.
    atualizarTabela()
    frame_estoque.tkraise()  # Garanto que o frame principal esteja visível.

def botaoProcurar(pesq, event=None):
    # Função para filtrar itens do estoque com base nos campos de pesquisa.
    # Carrega o estoque do arquivo JSON.
    estoque = receberEstoque()

    # Obtenho os valores dos campos de pesquisa. Converto o nome para maiúsculas para busca case-insensitive.
    cod = pesq[0].get()
    nome = pesq[1].get().upper()
    obs = pesq[2].get()

    # Filtro os itens que correspondem aos critérios de busca. Se o campo estiver vazio,
    # ignoro o filtro para aquele campo.
    resultados = [
        item for item in estoque
        if (cod == '' or cod in str(item['cod'])) and
           (nome == '' or nome in item['nome']) and
           (obs == '' or obs in item['obs'])
    ]

    # Limpo a tabela antes de exibir os resultados.
    for produto in tabela.get_children():
        tabela.delete(produto)

    # Preencho a tabela com os itens filtrados, formatando valores numéricos com 2 casas decimais.
    for item in resultados:
        tabela.insert('', 'end', iid=estoque.index(item), values=(
            item['cod'],
            item['nome'],
            f"{item['preco_venda']:.2f}",
            f"{item['preco_custo']:.2f}",
            f"{item['lucro']:.2f}",
            f"{item['qtd']:.2f}",
            item['obs']
        ))

def limpar(pesq):
    # Limpa todos os campos de pesquisa e atualiza a tabela para mostrar todos os itens.
    for p in pesq:
        p.delete(0, tk.END)
    botaoProcurar(pesq)

def editar(event=None):
    # Função para editar um item selecionado na tabela.
    # Verifico se um item está selecionado.
    ind = tabela.focus()
    if not ind:
        messagebox.showinfo('Aviso', 'Selecione um item para editar.')
        return

    # Carrego o estoque e tento acessar o item pelo índice selecionado.
    estoque = receberEstoque()
    try:
        item = estoque[int(ind)]
    except (ValueError, IndexError):
        messagebox.showerror('Erro', 'Item inválido selecionado.')
        return

    # Crio uma janela modal para edição, com tamanho fixo e tema consistente.
    janela = tk.Toplevel(root)
    janela.geometry('500x600')
    janela.title('Editar Item')
    janela.configure(bg='#1A3C34')
    janela.resizable(False, False)
    janela.grab_set()

    # Defino a fonte e validoções para números inteiros e flutuantes.
    fonte = ('Arial', 12)
    num_int = (janela.register(entryNumInt), '%P')
    num_float = (janela.register(entryNumFloat), '%P')

    # Lista de campos para a janela de edição. Cada tupla contém o rótulo, função para criar o campo,
    # valor inicial e função de validação (se aplicável).
    fields = [
        ('*Cód.:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_int), item['cod'], None),
        ('*Nome:', lambda: tk.Entry(janela, font=fonte, width=30), item['nome'], lambda e, entry: formNome(e, entry)),
        ('*Custo:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), item['preco_custo'], lambda e, entry: [formFloat(e, entry), formCustoCor(e, entry)]),
        ('*Venda:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), item['preco_venda'], lambda e, entry: formFloat(e, entry)),
        ('*Lucro (%):', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), item['lucro'], lambda e, entry: formFloat(e, entry)),
        ('*Disponível:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), item['qtd'], lambda e, entry: formFloat(e, entry)),
        ('Observações:', lambda: tk.Text(janela, font=fonte, height=5, width=30), item['obs'], None)
    ]

    # Crio os campos dinamicamente e armazeno em um dicionário para fácil acesso.
    entries = {}
    for label_text, entry_func, value, bind_func in fields:
        tk.Label(janela, text=label_text, font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        entry = entry_func()
        if isinstance(entry, tk.Text):
            entry.insert('1.0', value)
        else:
            entry.insert(0, value)
        entry.pack(pady=2)
        # Vinculo funções de validação, se existirem. Para 'Nome' e 'Custo', trato casos especiais.
        if bind_func:
            if label_text == '*Nome:':
                entry.bind('<FocusOut>', lambda e, ent=entry: bind_func(e, ent))
            elif label_text == '*Custo:':
                entry.bind('<FocusOut>', lambda e, ent=entry: bind_func(e, ent)[0])
                entry.bind('<KeyRelease>', lambda e, ent=entry: bind_func(e, ent)[1])
            elif bind_func and callable(bind_func):  # Verifico se bind_func é uma função válida
                entry.bind('<FocusOut>', lambda e, ent=entry: bind_func(e, ent))
        # Normalizo as chaves do dicionário, removendo asteriscos e texto extra.
        key = label_text.strip(':').replace('*', '').replace(' (%)', '')
        entries[key] = entry

    # Vinculo eventos para atualizar os campos de venda e lucro automaticamente.
    entries['Custo'].bind('<FocusOut>', lambda e: vendaAlt(e, entries['Custo'], entries['Venda'], entries['Lucro']), add='+')
    entries['Venda'].bind('<FocusOut>', lambda e: vendaAlt(e, entries['Custo'], entries['Venda'], entries['Lucro']), add='+')
    entries['Lucro'].bind('<FocusOut>', lambda e: lucroAlt(e, entries['Custo'], entries['Venda'], entries['Lucro']), add='+')

    # Crio um dicionário com os campos para passar para a função de salvamento.
    item_edt = {
        'univ_cod': item['univ_cod'],
        'cod': entries['Cód.'],
        'nome': entries['Nome'],
        'preco_venda': entries['Venda'],
        'preco_custo': entries['Custo'],
        'lucro': entries['Lucro'],
        'qtd': entries['Disponível'],
        'obs': entries['Observações']
    }

    # Botões para salvar ou cancelar a edição.
    tk.Button(janela, text='Salvar', command=lambda: salvar(janela, item_edt, False), **button_style).pack(pady=10)
    tk.Button(janela, text='Cancelar', command=janela.destroy, **button_style).pack(pady=5)

def botaoExcluir():
    # Função para excluir um item selecionado na tabela.
    ind = tabela.focus()
    if not ind:
        messagebox.showinfo('Aviso', 'Selecione um item para excluir.')
        return

    estoque = receberEstoque()
    try:
        item = estoque[int(ind)]
    except (ValueError, IndexError):
        messagebox.showerror('Erro', 'Item inválido selecionado.')
        return

    # Crio uma janela de confirmação para evitar exclusões acidentais.
    janela = tk.Toplevel(root)
    janela.geometry('400x150')
    janela.title('Excluir Item')
    janela.configure(bg='#1A3C34')
    janela.grab_set()
    janela.resizable(False, False)

    tk.Label(janela, text=f'Tem certeza que deseja excluir o item "{item["nome"]}"?', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=20)
    tk.Button(janela, text='Excluir', command=lambda: excluir(janela, int(ind)), **button_style).pack(pady=5)
    tk.Button(janela, text='Cancelar', command=janela.destroy, **button_style).pack(pady=5)

def excluir(janela, ind):
    # Remove o item do estoque e atualiza o arquivo JSON.
    estoque = receberEstoque()
    try:
        nome = estoque[ind]['nome']
        estoque.pop(ind)
        with open('estoque.json', 'w', encoding='utf-8') as arq:
            json.dump(estoque, arq, indent=4, ensure_ascii=False)
        messagebox.showinfo('Sucesso', f'Item "{nome}" excluído com sucesso!')
        atualizarTabela()
    except Exception as e:
        messagebox.showerror('Erro', f'Erro ao excluir o item: {str(e)}')
    janela.destroy()

def novoItem():
    # Função para adicionar um novo item ao estoque.
    global univ_cod

    # Carrego o estoque e gero um novo código universal (univ_cod) baseado no último item.
    with open('estoque.json', 'r', encoding='utf-8') as arq:
        estoque = json.load(arq)
        univ_cod = 1 if not estoque else estoque[-1]['univ_cod'] + 1

    # Crio uma janela modal para cadastro, similar à janela de edição.
    janela = tk.Toplevel(root)
    janela.geometry('500x600')
    janela.title('Novo Item')
    janela.configure(bg='#1A3C34')
    janela.resizable(False, False)
    janela.grab_set()

    fonte = ('Arial', 12)
    num_int = (janela.register(entryNumInt), '%P')
    num_float = (janela.register(entryNumFloat), '%P')

    # Lista de campos para o cadastro, com valores iniciais padrão.
    fields = [
        ('*Cód.:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_int), str(univ_cod), None),
        ('*Nome:', lambda: tk.Entry(janela, font=fonte, width=30), '', lambda e, entry: formNome(e, entry)),
        ('*Custo:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), '0.00', lambda e, entry: [formFloat(e, entry), formCustoCor(e, entry)]),
        ('*Venda:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), '0.00', lambda e, entry: formFloat(e, entry)),
        ('*Lucro (%):', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), '0.00', lambda e, entry: formFloat(e, entry)),
        ('*Disponível:', lambda: tk.Entry(janela, font=fonte, width=30, validate='key', validatecommand=num_float), '0.00', lambda e, entry: formFloat(e, entry)),
        ('Observações:', lambda: tk.Text(janela, font=fonte, height=5, width=30), '', None)
    ]

    # Configuro os campos dinamicamente, com validações específicas.
    entries = {}
    for label_text, entry_func, value, bind_func in fields:
        tk.Label(janela, text=label_text, font=fonte, fg='white', bg='#1A3C34').pack(pady=(10, 2))
        entry = entry_func()
        if isinstance(entry, tk.Text):
            entry.insert('1.0', value)
        else:
            entry.insert(0, value)
        entry.pack(pady=2)
        if bind_func:
            if label_text == '*Nome:':
                entry.bind('<FocusOut>', lambda e, ent=entry: bind_func(e, ent))
            elif label_text == '*Custo:':
                entry.bind('<FocusOut>', lambda e, ent=entry: bind_func(e, ent)[0])
                entry.bind('<KeyRelease>', lambda e, ent=entry: bind_func(e, ent)[1])
            elif bind_func and callable(bind_func):
                entry.bind('<FocusOut>', lambda e, ent=entry: bind_func(e, ent))
        key = label_text.strip(':').replace('*', '').replace(' (%)', '')
        entries[key] = entry

    # Vinculo os cálculos automáticos de lucro e venda.
    entries['Custo'].bind('<FocusOut>', lambda e: vendaAlt(e, entries['Custo'], entries['Venda'], entries['Lucro']), add='+')
    entries['Venda'].bind('<FocusOut>', lambda e: vendaAlt(e, entries['Custo'], entries['Venda'], entries['Lucro']), add='+')
    entries['Lucro'].bind('<FocusOut>', lambda e: lucroAlt(e, entries['Custo'], entries['Venda'], entries['Lucro']), add='+')

    # Dicionário com os campos para salvamento.
    item_entry = {
        'univ_cod': univ_cod,
        'cod': entries['Cód.'],
        'nome': entries['Nome'],
        'preco_venda': entries['Venda'],
        'preco_custo': entries['Custo'],
        'lucro': entries['Lucro'],
        'qtd': entries['Disponível'],
        'obs': entries['Observações']
    }

    tk.Button(janela, text='Salvar', command=lambda: salvar(janela, item_entry, True), **button_style).pack(pady=10)
    tk.Button(janela, text='Cancelar', command=janela.destroy, **button_style).pack(pady=5)

def entryNumInt(n):
    # Valida se a entrada é um número inteiro ou vazia. Usado no campo de código.
    if n == '':
        return True
    try:
        int(n)
        return True
    except:
        return False

def entryNumFloat(n):
    # Valida se a entrada é um número flutuante ou vazia. Usado para preços, lucro e quantidade.
    if n == '':
        return True
    try:
        float(n)
        return True
    except:
        return False

def formNome(e, entry):
    # Converte o nome para maiúsculas ao sair do campo, para padronização.
    nome = entry.get().upper()
    entry.delete(0, tk.END)
    entry.insert(0, nome)

def formFloat(e, entry):
    # Formata números flutuantes com 2 casas decimais. Insere 0.00 se o campo for inválido.
    value = entry.get()
    entry.delete(0, tk.END)
    if value == '':
        entry.insert(0, '0.00')
    else:
        try:
            entry.insert(0, f'{float(value):.2f}')
        except ValueError:
            entry.insert(0, '0.00')

def formCustoCor(e, entry):
    # Destaca o campo de custo em rosa se estiver vazio ou zerado, para indicar erro visualmente.
    value = entry.get()
    entry.configure(bg='pink' if value == '' or value == '0.00' else 'white')

def lucroAlt(e, custo_entry, venda_entry, lucro_entry):
    # Calcula o preço de venda com base no custo e percentual de lucro.
    custo = float(custo_entry.get() or 0)
    lucro = float(lucro_entry.get() or 0)
    venda = custo + (custo * lucro / 100)
    venda_entry.delete(0, tk.END)
    venda_entry.insert(0, f'{venda:.2f}')

def vendaAlt(e, custo_entry, venda_entry, lucro_entry):
    # Calcula o percentual de lucro com base no custo e preço de venda.
    custo = float(custo_entry.get() or 0)
    venda = float(venda_entry.get() or 0)
    lucro_entry.delete(0, tk.END)
    if custo == 0:
        lucro_entry.insert(0, '100.00' if venda != 0 else '0.00')
    else:
        lucro = ((venda - custo) / custo) * 100 if custo != 0 else 0
        lucro_entry.insert(0, f'{lucro:.2f}')

def receberEstoque():
    # Carrega o estoque do arquivo JSON. Retorna lista vazia se o arquivo não existir.
    try:
        with open('estoque.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)
    except FileNotFoundError:
        return []

def atualizarTabela():
    # Atualiza a tabela com todos os itens do estoque, formatando valores numéricos.
    estoque = receberEstoque()
    for item in tabela.get_children():
        tabela.delete(item)
    for item in estoque:
        tabela.insert('', 'end', iid=estoque.index(item), values=(
            item['cod'],
            item['nome'],
            f"{item['preco_venda']:.2f}",
            f"{item['preco_custo']:.2f}",
            f"{item['lucro']:.2f}",
            f"{item['qtd']:.2f}",
            item['obs']
        ))

def salvar(janela, entry, novo=True):
    # Salva um item novo ou editado no arquivo JSON.
    estoque = receberEstoque()
    ind = int(tabela.focus()) if not novo and tabela.focus() else None

    k = ['cod', 'nome', 'preco_venda', 'preco_custo', 'lucro', 'qtd']
    obrig = ['cod', 'nome', 'preco_venda', 'preco_custo', 'lucro', 'qtd']
    item = {'univ_cod': entry['univ_cod']}

    # Coleto os dados dos campos, convertendo tipos conforme necessário.
    for key in k:
        if key in ['cod', 'preco_venda', 'preco_custo', 'lucro', 'qtd']:
            value = entry[key].get()
            item[key] = int(value) if key == 'cod' and value else float(value or 0)
        else:
            item[key] = entry[key].get().upper()
    item['obs'] = entry['obs'].get('1.0', 'end-1c')

    # Valido se o código já existe (exceto para o próprio item em edição) e se os campos obrigatórios estão preenchidos.
    flagCod = any(produto['cod'] == item['cod'] and (novo or estoque.index(produto) != ind) for produto in estoque)
    flagNull = any(not item[o] for o in obrig)

    if flagCod:
        messagebox.showerror('Erro', 'Código já cadastrado!')
    elif flagNull:
        messagebox.showerror('Erro', 'Preencha todos os campos obrigatórios (*)!')
    else:
        try:
            with open('estoque.json', 'r+', encoding='utf-8') as arq:
                estoque = json.load(arq)
                if novo:
                    estoque.append(item)
                else:
                    estoque[ind] = item
                arq.seek(0)
                json.dump(estoque, arq, indent=4, ensure_ascii=False)
                arq.truncate()
            messagebox.showinfo('Sucesso', f'Item "{item["nome"]}" {"cadastrado" if novo else "alterado"} com sucesso!')
            atualizarTabela()
            janela.destroy()
        except Exception as e:
            messagebox.showerror('Erro', f'Erro ao salvar o item: {str(e)}')
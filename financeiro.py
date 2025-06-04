import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
import json, os, sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

# Estilo dos botões
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

def receberVendas():
    try:
        with open('vendas.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)
    except FileNotFoundError:
        return []

def receberFinanceiro():
    try:
        with open('financeiro.json', 'r', encoding='utf-8') as arq:
            return json.load(arq)
    except FileNotFoundError:
        return {"contas_receber": [], "contas_pagar": []}

def salvarFinanceiro(dados):
    with open('financeiro.json', 'w', encoding='utf-8') as arq:
        json.dump(dados, arq, indent=4, ensure_ascii=False)

def validar_data(data_str):
    if not data_str:
        return True
    try:
        datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def validar_numero(valor):
    if not valor:
        return True
    try:
        float(valor)
        return True
    except ValueError:
        return False

def criarContasReceberVenda(venda, atualizar_tabela=True):
    """Cria contas a receber para uma única venda com pagamento a crédito."""
    financeiro = receberFinanceiro()
    contas_receber = financeiro['contas_receber']
    ids = [c['id'] for c in contas_receber]
    novo_id = max(ids) + 1 if ids else 1

    pagamento = venda.get('pagamento', {})
    credito = pagamento.get('Credito', [])
    if not credito:
        return False  # Sem crédito

    num_venda = str(venda.get('num_venda', ''))
    cliente_nome = venda.get('cliente', {}).get('nome', 'Desconhecido')
    data_venda = venda.get('data', '01/01/1970')
    try:
        data_venda_dt = datetime.strptime(data_venda, '%d/%m/%Y')
    except ValueError:
        with open('sincronizacao_log.txt', 'a', encoding='utf-8') as log:
            log.write(f"{datetime.now()}: Ignorada venda {num_venda} - Data inválida\n")
        return False

    contas_criadas = False
    for credito_item in credito:
        valor_total = credito_item.get('valor', 0)
        parcelas = credito_item.get('parcelas', 1)
        if parcelas <= 0:
            parcelas = 1
        valor_parcela = valor_total / parcelas

        for i in range(parcelas):
            vencimento = (data_venda_dt + timedelta(days=30 * (i + 1))).strftime('%d/%m/%Y')
            existe = any(
                c.get('num_venda') == num_venda and
                abs(c.get('valor', 0) - valor_parcela) < 0.01 and
                c.get('vencimento') == vencimento
                for c in contas_receber
            )
            if existe:
                continue

            conta = {
                'id': novo_id,
                'num_venda': num_venda,
                'cliente_nome': cliente_nome,
                'valor': valor_parcela,
                'vencimento': vencimento,
                'status': 'Pendente'
            }
            contas_receber.append(conta)
            novo_id += 1
            contas_criadas = True

    if contas_criadas:
        financeiro['contas_receber'] = contas_receber
        salvarFinanceiro(financeiro)
        if atualizar_tabela:
            try:
                atualizarReceber('Todos', '')
            except (NameError, tk.TclError):
                pass  # Tabela não inicializada ou inválida, ignora
        return True
    return False

def sincronizarContasReceber():
    """Sincroniza todas as vendas a crédito com contas a receber."""
    vendas = receberVendas()
    for venda in vendas:
        criarContasReceberVenda(venda, atualizar_tabela=False)  # Não atualiza tabela aqui
    try:
        atualizarReceber('Todos', '')  # Atualiza tabela uma vez no final
    except (NameError, tk.TclError):
        pass  # Tabela não inicializada ou inválida

def inicio():
    global root, canvas_grafico, resumo_labels, tabela_pagamentos, tabela_receber, tabela_pagar, grafico_frame

    root = tk.Toplevel()
    root.geometry('1000x700')
    root.title('FINANCEIRO')
    root.state('zoomed')
    root.configure(bg='#1A3C34')

    def on_closing():
        global canvas_grafico, tabela_receber, tabela_pagar
        if canvas_grafico:
            canvas_grafico.get_tk_widget().destroy()
            canvas_grafico = None
        tabela_receber = None
        tabela_pagar = None
        plt.close('all')
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    main_frame = tk.Frame(root, bg='#1A3C34')
    main_frame.pack(fill='both', expand=True)

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # Tab 1: Contas a Receber
    receber_frame = tk.Frame(notebook, bg='#1A3C34')
    notebook.add(receber_frame, text='Contas a Receber')

    receber_frame.grid_rowconfigure(0, weight=0)
    receber_frame.grid_rowconfigure(1, weight=0)
    receber_frame.grid_rowconfigure(2, weight=1)
    receber_frame.grid_columnconfigure(0, weight=1)

    tk.Label(receber_frame, text='Contas a Receber', font=('Arial', 16, 'bold'), fg='white', bg='#1A3C34').grid(row=0, column=0, pady=10)

    filter_receber = tk.Frame(receber_frame, bg='#1A3C34')
    filter_receber.grid(row=1, column=0, pady=10, padx=20, sticky='ew')
    tk.Label(filter_receber, text='Status:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    status_filtro = ttk.Combobox(filter_receber, values=['Todos', 'Pendente', 'Pago'], state='readonly', width=10)
    status_filtro.set('Todos')
    status_filtro.pack(side=tk.LEFT, padx=5)
    tk.Label(filter_receber, text='Vencimento (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    vencimento_filtro = tk.Entry(filter_receber, font=('Arial', 12), width=12)
    vencimento_filtro.pack(side=tk.LEFT, padx=5)
    tk.Button(filter_receber, text='Filtrar', command=lambda: atualizarReceber(status_filtro.get(), vencimento_filtro.get()),
              **button_style).pack(side=tk.LEFT, padx=5)

    colunas_receber = ['id', 'num_venda', 'cliente', 'valor', 'vencimento', 'status']
    tabela_receber = ttk.Treeview(receber_frame, columns=colunas_receber, show='headings')
    tabela_receber.heading('id', text='ID')
    tabela_receber.heading('num_venda', text='Venda')
    tabela_receber.heading('cliente', text='Cliente')
    tabela_receber.heading('valor', text='Valor')
    tabela_receber.heading('vencimento', text='Vencimento')
    tabela_receber.heading('status', text='Status')
    tabela_receber.column('id', width=50)
    tabela_receber.column('num_venda', width=100)
    tabela_receber.column('cliente', width=200)
    tabela_receber.column('valor', width=100)
    tabela_receber.column('vencimento', width=100)
    tabela_receber.column('status', width=100)
    tabela_receber.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
    scrollbar_receber = ttk.Scrollbar(receber_frame, orient='vertical', command=tabela_receber.yview)
    tabela_receber.configure(yscrollcommand=scrollbar_receber.set)
    scrollbar_receber.grid(row=2, column=1, sticky='ns')

    receber_buttons = tk.Frame(receber_frame, bg='#1A3C34')
    receber_buttons.grid(row=3, column=0, pady=10)
    tk.Button(receber_buttons, text='Adicionar', command=adicionarReceber, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(receber_buttons, text='Editar', command=lambda: editarReceber(tabela_receber), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(receber_buttons, text='Marcar Pago', command=lambda: marcarPagoReceber(tabela_receber), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(receber_buttons, text='Excluir', command=lambda: excluirReceber(tabela_receber), **button_style).pack(side=tk.LEFT, padx=5)

    # Tab 2: Contas a Pagar
    pagar_frame = tk.Frame(notebook, bg='#1A3C34')
    notebook.add(pagar_frame, text='Contas a Pagar')

    pagar_frame.grid_rowconfigure(0, weight=0)
    pagar_frame.grid_rowconfigure(1, weight=0)
    pagar_frame.grid_rowconfigure(2, weight=1)
    pagar_frame.grid_columnconfigure(0, weight=1)

    tk.Label(pagar_frame, text='Contas a Pagar', font=('Arial', 16, 'bold'), fg='white', bg='#1A3C34').grid(row=0, column=0, pady=10)

    filter_pagar = tk.Frame(pagar_frame, bg='#1A3C34')
    filter_pagar.grid(row=1, column=0, pady=10, padx=20, sticky='ew')
    tk.Label(filter_pagar, text='Status:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    status_pagar = ttk.Combobox(filter_pagar, values=['Todos', 'Pendente', 'Pago'], state='readonly', width=10)
    status_pagar.set('Todos')
    status_pagar.pack(side=tk.LEFT, padx=5)
    tk.Label(filter_pagar, text='Vencimento (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    vencimento_pagar = tk.Entry(filter_pagar, font=('Arial', 12), width=12)
    vencimento_pagar.pack(side=tk.LEFT, padx=5)
    tk.Button(filter_pagar, text='Filtrar', command=lambda: atualizarPagar(status_pagar.get(), vencimento_pagar.get()),
              **button_style).pack(side=tk.LEFT, padx=5)

    colunas_pagar = ['id', 'credor', 'tipo', 'valor', 'vencimento', 'status']
    tabela_pagar = ttk.Treeview(pagar_frame, columns=colunas_pagar, show='headings')
    tabela_pagar.heading('id', text='ID')
    tabela_pagar.heading('credor', text='Credor')
    tabela_pagar.heading('tipo', text='Tipo')
    tabela_pagar.heading('valor', text='Valor')
    tabela_pagar.heading('vencimento', text='Vencimento')
    tabela_pagar.heading('status', text='Status')
    tabela_pagar.column('id', width=50)
    tabela_pagar.column('credor', width=150)
    tabela_pagar.column('tipo', width=100)
    tabela_pagar.column('valor', width=100)
    tabela_pagar.column('vencimento', width=100)
    tabela_pagar.column('status', width=100)
    tabela_pagar.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)
    scrollbar_pagar = ttk.Scrollbar(pagar_frame, orient='vertical', command=tabela_pagar.yview)
    tabela_pagar.configure(yscrollcommand=scrollbar_pagar.set)
    scrollbar_pagar.grid(row=2, column=1, sticky='ns')

    pagar_buttons = tk.Frame(pagar_frame, bg='#1A3C34')
    pagar_buttons.grid(row=3, column=0, pady=10)
    tk.Button(pagar_buttons, text='Adicionar', command=adicionarPagar, **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(pagar_buttons, text='Editar', command=lambda: editarPagar(tabela_pagar), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(pagar_buttons, text='Marcar Pago', command=lambda: marcarPagoPagar(tabela_pagar), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(pagar_buttons, text='Excluir', command=lambda: excluirPagar(tabela_pagar), **button_style).pack(side=tk.LEFT, padx=5)

    # Tab 3: Resumo Financeiro
    resumo_frame = tk.Frame(notebook, bg='#1A3C34')
    notebook.add(resumo_frame, text='Resumo Financeiro')

    resumo_frame.grid_rowconfigure(0, weight=0)
    resumo_frame.grid_rowconfigure(1, weight=0)
    resumo_frame.grid_rowconfigure(2, weight=0)
    resumo_frame.grid_rowconfigure(3, weight=0)
    resumo_frame.grid_rowconfigure(4, weight=2)
    resumo_frame.grid_rowconfigure(5, weight=0)
    resumo_frame.grid_columnconfigure(0, weight=1)

    header_frame = tk.Frame(resumo_frame, bg='#1A3C34')
    header_frame.grid(row=0, column=0, pady=20, sticky='ew')
    tk.Label(header_frame, text="Sistema de Vendas - Módulo Financeiro", font=('Arial', 16, 'bold'), fg='white',
             bg='#1A3C34').pack()

    filter_frame = tk.Frame(resumo_frame, bg='#1A3C34')
    filter_frame.grid(row=1, column=0, pady=10, padx=20, sticky='ew')
    tk.Label(filter_frame, text='Data Início (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    data_inicio = tk.Entry(filter_frame, font=('Arial', 12), width=12)
    data_inicio.pack(side=tk.LEFT, padx=5)
    tk.Label(filter_frame, text='Data Fim (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    data_fim = tk.Entry(filter_frame, font=('Arial', 12), width=12)
    data_fim.pack(side=tk.LEFT, padx=5)
    tk.Button(filter_frame, text='Filtrar', command=lambda: atualizarResumoFinanceiro(data_inicio.get(), data_fim.get(), resumo_frame),
              **button_style).pack(side=tk.LEFT, padx=5)

    resumo_subframe = tk.Frame(resumo_frame, bg='#1A3C34')
    resumo_subframe.grid(row=2, column=0, pady=10, padx=20, sticky='ew')
    resumo_labels = {}
    labels = ['Faturamento Bruto', 'Descontos aplicados', 'Total líquido', 'Lucro estimado']
    for texto in labels:
        label = tk.Label(resumo_subframe, text=f'{texto}: R$ 0,00', font=('Arial', 12), fg='white', bg='#1A3C34')
        label.pack(anchor='w')
        resumo_labels[texto] = label

    pagamento_frame = tk.Frame(resumo_frame, bg='#1A3C34')
    pagamento_frame.grid(row=3, column=0, pady=10, padx=20, sticky='ew')
    pagamento_frame.grid_rowconfigure(1, weight=1)
    pagamento_frame.grid_columnconfigure(0, weight=1)

    tk.Label(pagamento_frame, text='Formas de Pagamento', font=('Arial', 14, 'bold'), fg='white', bg='#1A3C34').grid(row=0, column=0, columnspan=2, sticky='w')

    colunas = ['forma', 'valor', 'percentual']
    tabela_pagamentos = ttk.Treeview(pagamento_frame, columns=colunas, show='headings', height=5)
    tabela_pagamentos.heading('forma', text='Forma de Pagamento')
    tabela_pagamentos.heading('valor', text='Valor Total')
    tabela_pagamentos.heading('percentual', text='% do Total')
    tabela_pagamentos.column('forma', width=150)
    tabela_pagamentos.column('valor', width=100)
    tabela_pagamentos.column('percentual', width=100)
    tabela_pagamentos.grid(row=1, column=0, sticky='nsew')

    scrollbar = ttk.Scrollbar(pagamento_frame, orient='vertical', command=tabela_pagamentos.yview)
    tabela_pagamentos.configure(yscrollcommand=scrollbar.set)
    scrollbar.grid(row=1, column=1, sticky='ns')

    grafico_frame = tk.Frame(resumo_frame, bg='#1A3C34')
    grafico_frame.grid(row=4, column=0, pady=10, padx=20, sticky='nsew')
    grafico_frame.grid_rowconfigure(0, weight=1)
    grafico_frame.grid_columnconfigure(0, weight=1)
    canvas_grafico = None

    button_frame = tk.Frame(resumo_frame, bg='#1A3C34')
    button_frame.grid(row=5, column=0, pady=20, sticky='ew')
    tk.Button(button_frame, text='Atualizar', command=lambda: atualizarResumoFinanceiro(data_inicio.get(), data_fim.get(), resumo_frame), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Gerar Relatório', command=lambda: gerarRelatorio(data_inicio.get(), data_fim.get()), **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Voltar', command=on_closing, **button_style).pack(side=tk.LEFT, padx=5)

    try:
        sincronizarContasReceber()
        atualizarResumoFinanceiro('', '', resumo_frame)
        atualizarReceber('Todos', '')
        atualizarPagar('Todos', '')
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao inicializar: {str(e)}")
        
def atualizarResumoFinanceiro(data_inicio, data_fim, frame):
    global resumo_labels, tabela_pagamentos, canvas_grafico
    
    if not (validar_data(data_inicio) and validar_data(data_fim)):
        messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA')
        return

    vendas = receberVendas()
    faturamento_bruto = 0.0
    descontos = 0.0
    total_liquido = 0.0
    pagamentos = {'Dinheiro': 0.0, 'Pix': 0.0, 'Credito': 0.0, 'Debito': 0.0}

    try:
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y')
        else:
            data_inicio_dt = None
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%d/%m/%Y')
        else:
            data_fim_dt = None
    except ValueError:
        messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA')
        return

    for venda in vendas:
        try:
            data_venda_dt = datetime.strptime(venda.get('data', '01/01/1970'), '%d/%m/%Y')
        except ValueError:
            continue

        if data_inicio_dt and data_venda_dt < data_inicio_dt:
            continue
        if data_fim_dt and data_venda_dt > data_fim_dt:
            continue

        faturamento_bruto += venda.get('bruto', 0)
        descontos += venda.get('desconto', 0)
        total_liquido += venda.get('total', 0)
        
        pagamento = venda.get('pagamento', {})
        for forma, valor in pagamento.items():
            if forma == 'Credito':
                pagamentos[forma] += sum(p['valor'] for p in valor) if isinstance(valor, list) else 0
            elif forma in ['Pix', 'Debito']:
                pagamentos[forma] += sum(valor) if isinstance(valor, list) else 0
            else:
                pagamentos[forma] += valor if isinstance(valor, (int, float)) else 0

    custo_estimado = faturamento_bruto * 0.4
    lucro_estimado = total_liquido - custo_estimado

    resumo_labels['Faturamento Bruto'].configure(text=f'Faturamento Bruto: R$ {faturamento_bruto:.2f}')
    resumo_labels['Descontos aplicados'].configure(text=f'Descontos aplicados: R$ {descontos:.2f}')
    resumo_labels['Total líquido'].configure(text=f'Total líquido: R$ {total_liquido:.2f}')
    resumo_labels['Lucro estimado'].configure(text=f'Lucro estimado: R$ {lucro_estimado:.2f}')

    for item in tabela_pagamentos.get_children():
        tabela_pagamentos.delete(item)
        
    total_pagamentos = sum(pagamentos.values())
    for forma, valor in pagamentos.items():
        if valor > 0:
            percentual = (valor / total_pagamentos * 100) if total_pagamentos > 0 else 0
            tabela_pagamentos.insert('', 'end', values=(forma, f'R$ {valor:.2f}', f'{percentual:.1f}%'))

    if canvas_grafico:
        canvas_grafico.get_tk_widget().destroy()
        canvas_grafico = None
    plt.close('all')

    # Aumentar tamanho do gráfico
    fig, ax = plt.subplots(figsize=(5, 3))  
    formas = [f for f in pagamentos if pagamentos[f] > 0]
    valores = [pagamentos[f] for f in formas]

    ax.bar(formas, valores, color="#4FE0CA")
    ax.set_title('Faturamento por Forma de Pagamento', fontsize=12, pad=10)
    ax.set_ylabel('Valor (R$)', fontsize=10)
    ax.grid(True, axis='y', linestyle='--')

    # Ajustar rótulos do eixo X
    ax.set_xticks(range(len(formas)))
    ax.set_xticklabels(formas, rotation=0, ha='right', fontsize=10)
    plt.tight_layout() 

    # Anexar ao grafico_frame diretamente
    canvas_grafico = FigureCanvasTkAgg(fig, master=grafico_frame)
    canvas_grafico.draw()
    canvas_grafico.get_tk_widget().grid(row=0, column=0, sticky='nsew')    
    
def gerarRelatorio(data_inicio, data_fim):
    if not (validar_data(data_inicio) and validar_data(data_fim)):
        messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA')
        return

    vendas = receberVendas()
    faturamento_bruto = 0.0
    descontos = 0.0
    total_liquido = 0.0
    pagamentos = {'Dinheiro': 0.0, 'Pix': 0.0, 'Credito': 0.0, 'Debito': 0.0}

    try:
        if data_inicio:
            data_inicio_dt = datetime.strptime(data_inicio, '%d/%m/%Y')
        else:
            data_inicio_dt = None
        if data_fim:
            data_fim_dt = datetime.strptime(data_fim, '%d/%m/%Y')
        else:
            data_fim_dt = None
    except ValueError:
        messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA')
        return

    for venda in vendas:
        try:
            data_venda_dt = datetime.strptime(venda.get('data', '01/01/1970'), '%d/%m/%Y')
        except ValueError:
            continue

        if data_inicio_dt and data_venda_dt < data_inicio_dt:
            continue
        if data_fim_dt and data_venda_dt > data_fim_dt:
            continue

        faturamento_bruto += venda.get('bruto', 0)
        descontos += venda.get('desconto', 0)
        total_liquido += venda.get('total', 0)
        
        pagamento = venda.get('pagamento', {})
        for forma, valor in pagamento.items():
            if forma == 'Credito':
                pagamentos[forma] += sum(p['valor'] for p in valor) if isinstance(valor, list) else 0
            elif forma in ['Pix', 'Debito']:
                pagamentos[forma] += sum(valor) if isinstance(valor, list) else 0
            else:
                pagamentos[forma] += valor if isinstance(valor, (int, float)) else 0

    custo_estimado = faturamento_bruto * 0.4
    lucro_estimado = total_liquido - custo_estimado

    arq = 'relatorio_financeiro.pdf'
    page_size = (227, 400)
    pdf = canvas.Canvas(arq, pagesize=page_size)
    largura, altura = page_size
    margem = 10
    pdf.setFont('Courier', 8)
    pdf.setTitle('Relatório Financeiro')
    y = altura - margem - 20

    def linha(t, s=10, centro=False):
        nonlocal y
        if y < margem + 20:
            pdf.showPage()
            pdf.setFont('Courier', 8)
            y = altura - margem - 20
        if centro:
            pdf.drawCentredString(largura / 2, y, t)
        else:
            pdf.drawString(margem, y, t)
        y -= s

    pdf.setFont('Courier-Bold', 10)
    linha('RELATÓRIO FINANCEIRO', centro=True, s=12)
    pdf.setFont('Courier', 8)
    linha('-' * 40, s=10)
    periodo = f'Período: {data_inicio} a {data_fim}' if data_inicio and data_fim else 'Período: Total'
    linha(periodo)
    linha('-' * 40, s=10)

    linha(f'Faturamento bruto: R$ {faturamento_bruto:.2f}')
    linha(f'Desconto aplicado: R$ {descontos:.2f}')
    linha(f'Total líquido: R$ {total_liquido:.2f}')
    linha(f'Lucro estimado: R$ {lucro_estimado:.2f}')
    linha('-' * 40, s=10)

    linha('FORMAS DE PAGAMENTO', centro=True)
    linha('-' * 40, s=8)
    linha(f"{'TIPO':<15}{'VALOR':>10}{'%':>15}")
    linha('-' * 40, s=8)
    total_pagamentos = sum(pagamentos.values())
    for forma, valor in pagamentos.items():
        if valor > 0:
            percentual = (valor / total_pagamentos * 100) if total_pagamentos > 0 else 0
            linha(f"{forma[:15]:<15}{valor:>10.2f}{percentual:>15.1f}")
    linha('-' * 40, s=8)

    pdf.save()
    os.startfile(arq)

def atualizarReceber(status_filtro='Todos', vencimento_filtro=''):
    global tabela_receber
    
    try:
        if not tabela_receber or not tabela_receber.winfo_exists():  # Verifica se tabela é válida
            return
    except NameError:
        return  # Tabela não inicializada, sai silenciosamente

    financeiro = receberFinanceiro()
    contas = financeiro['contas_receber']

    if vencimento_filtro and not validar_data(vencimento_filtro):
        messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA')
        return

    try:
        vencimento_dt = datetime.strptime(vencimento_filtro, '%d/%m/%Y') if vencimento_filtro else None
    except ValueError:
        vencimento_dt = None

    for item in tabela_receber.get_children():
        tabela_receber.delete(item)

    for conta in contas:
        if status_filtro != 'Todos' and conta['status'] != status_filtro:
            continue
        if vencimento_dt:
            try:
                conta_dt = datetime.strptime(conta['vencimento'], '%d/%m/%Y')
                if conta_dt.date() != vencimento_dt.date():
                    continue
            except ValueError:
                continue
                
        tabela_receber.insert('', 'end', values=(
            conta.get('id', ''),
            conta.get('num_venda', ''),
            conta.get('cliente_nome', ''),
            f"R$ {conta.get('valor', 0):.2f}",
            conta.get('vencimento', ''),
            conta.get('status', '')
        ))

def adicionarReceber():
    janela = tk.Toplevel(root)
    janela.title('Adicionar Conta a Receber')
    janela.geometry('400x300')
    janela.configure(bg='#1A3C34')
    janela.grab_set()

    tk.Label(janela, text='Venda:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    num_venda = tk.Entry(janela, font=('Arial', 12))
    num_venda.pack(pady=5)

    tk.Label(janela, text='Cliente:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    cliente = tk.Entry(janela, font=('Arial', 12))
    cliente.pack(pady=5)

    tk.Label(janela, text='Valor (R$):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    valor = tk.Entry(janela, font=('Arial', 12))
    valor.pack(pady=5)

    tk.Label(janela, text='Vencimento (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    vencimento = tk.Entry(janela, font=('Arial', 12))
    vencimento.pack(pady=5)

    def salvar():
        if not (num_venda.get() and cliente.get() and valor.get() and vencimento.get()):
            messagebox.showerror('Erro', 'Preencha todos os campos', parent=janela)
            return
        if not validar_numero(valor.get()):
            messagebox.showerror('Erro', 'Valor inválido', parent=janela)
            return
        if not validar_data(vencimento.get()):
            messagebox.showerror('Erro', 'Data inválida', parent=janela)
            return

        financeiro = receberFinanceiro()
        # Verifica duplicação
        if any(
            c.get('num_venda') == num_venda.get() and
            abs(c.get('valor', 0) - float(valor.get())) < 0.01 and
            c.get('vencimento') == vencimento.get()
            for c in financeiro['contas_receber']
        ):
            messagebox.showerror('Erro', 'Conta já existe para esta venda e vencimento', parent=janela)
            return

        ids = [c['id'] for c in financeiro['contas_receber']]
        novo_id = max(ids) + 1 if ids else 1

        conta = {
            'id': novo_id,
            'num_venda': num_venda.get(),
            'cliente_nome': cliente.get(),
            'valor': float(valor.get()),
            'vencimento': vencimento.get(),
            'status': 'Pendente'
        }

        financeiro['contas_receber'].append(conta)
        salvarFinanceiro(financeiro)
        atualizarReceber('Todos', '')
        messagebox.showinfo('Sucesso', 'Conta adicionada', parent=janela)
        janela.destroy()

    tk.Button(janela, text='Salvar', command=salvar, **button_style).pack(pady=10)

def editarReceber(tabela):
    try:
        selected = tabela.focus()
        if not selected:
            raise ValueError
        valores = tabela.item(selected, 'values')
        if not valores:
            raise ValueError
        conta_id = int(valores[0])
    except:
        messagebox.showerror('Erro', 'Selecione uma conta', parent=root)
        return

    financeiro = receberFinanceiro()
    conta = None
    for c in financeiro['contas_receber']:
        if c['id'] == conta_id:
            conta = c
            break

    if not conta:
        messagebox.showerror('Erro', 'Conta não encontrada', parent=root)
        return

    janela = tk.Toplevel(root)
    janela.title('Editar Conta a Receber')
    janela.geometry('400x300')
    janela.configure(bg='#1A3C34')
    janela.grab_set()

    tk.Label(janela, text='Venda:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    num_venda = tk.Entry(janela, font=('Arial', 12))
    num_venda.insert(0, conta.get('num_venda', ''))
    num_venda.pack(pady=5)

    tk.Label(janela, text='Cliente:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    cliente = tk.Entry(janela, font=('Arial', 12))
    cliente.insert(0, conta.get('cliente_nome', ''))
    cliente.pack(pady=5)

    tk.Label(janela, text='Valor (R$):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    valor = tk.Entry(janela, font=('Arial', 12))
    valor.insert(0, f"{conta.get('valor', 0):.2f}")
    valor.pack(pady=5)

    tk.Label(janela, text='Vencimento (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    vencimento = tk.Entry(janela, font=('Arial', 12))
    vencimento.insert(0, conta.get('vencimento', ''))
    vencimento.pack(pady=5)

    def salvar():
        if not (num_venda.get() and cliente.get() and valor.get() and vencimento.get()):
            messagebox.showerror('Erro', 'Preencha todos os campos', parent=janela)
            return
        if not validar_numero(valor.get()):
            messagebox.showerror('Erro', 'Valor inválido', parent=janela)
            return
        if not validar_data(vencimento.get()):
            messagebox.showerror('Erro', 'Data inválida', parent=janela)
            return

        conta['num_venda'] = num_venda.get()
        conta['cliente_nome'] = cliente.get()
        conta['valor'] = float(valor.get())
        conta['vencimento'] = vencimento.get()
        
        salvarFinanceiro(financeiro)
        atualizarReceber('Todos', '')
        messagebox.showinfo('Sucesso', 'Conta atualizada', parent=janela)
        janela.destroy()

    tk.Button(janela, text='Salvar', command=salvar, **button_style).pack(pady=10)

def marcarPagoReceber(tabela):
    try:
        selected = tabela.focus()
        if not selected:
            raise ValueError
        valores = tabela.item(selected, 'values')
        if not valores:
            raise ValueError
        conta_id = int(valores[0])
    except:
        messagebox.showerror('Erro', 'Selecione uma conta', parent=root)
        return

    financeiro = receberFinanceiro()
    for conta in financeiro['contas_receber']:
        if conta['id'] == conta_id:
            if conta.get('status') == 'Pago':
                messagebox.showinfo('Info', 'Conta já está paga', parent=root)
                return
            conta['status'] = 'Pago'
            salvarFinanceiro(financeiro)
            atualizarReceber('Todos', '')
            messagebox.showinfo('Sucesso', 'Conta marcada como paga', parent=root)
            return

    messagebox.showerror('Erro', 'Conta não encontrada', parent=root)

def excluirReceber(tabela):
    try:
        selected = tabela.focus()
        if not selected:
            raise ValueError
        valores = tabela.item(selected, 'values')
        if not valores:
            raise ValueError
        conta_id = int(valores[0])
    except:
        messagebox.showerror('Erro', 'Selecione uma conta', parent=root)
        return

    confirm = messagebox.askyesno('Confirmar', 'Confirma a exclusão?', parent=root)
    if not confirm:
        return

    financeiro = receberFinanceiro()
    financeiro['contas_receber'] = [c for c in financeiro['contas_receber'] if c['id'] != conta_id]

    salvarFinanceiro(financeiro)
    atualizarReceber('Todos', '')
    messagebox.showinfo('Sucesso', 'Conta excluída', parent=root)

def atualizarPagar(status_filtro='Todos', vencimento_filtro=''):
    global tabela_pagar
    
    try:
        if not tabela_pagar or not tabela_pagar.winfo_exists():  # Verifica se tabela é válida
            return
    except NameError:
        return  # Tabela não inicializada, sai silenciosamente

    financeiro = receberFinanceiro()
    contas = financeiro['contas_pagar']

    if vencimento_filtro and not validar_data(vencimento_filtro):
        messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA')
        return

    try:
        vencimento_dt = datetime.strptime(vencimento_filtro, '%d/%m/%Y') if vencimento_filtro else None
    except ValueError:
        vencimento_dt = None

    for item in tabela_pagar.get_children():
        tabela_pagar.delete(item)

    for conta in contas:
        if status_filtro != 'Todos' and conta['status'] != status_filtro:
            continue
        if vencimento_dt:
            try:
                conta_dt = datetime.strptime(conta['vencimento'], '%d/%m/%Y')
                if conta_dt.date() != vencimento_dt.date():
                    continue
            except ValueError:
                continue
                
        tabela_pagar.insert('', 'end', values=(
            conta.get('id', ''),
            conta.get('credor', ''),
            conta.get('tipo', ''),
            f"R$ {conta.get('valor', 0):.2f}",
            conta.get('vencimento', ''),
            conta.get('status', '')
        ))

def adicionarPagar():
    janela = tk.Toplevel(root)
    janela.title('Adicionar Conta a Pagar')
    janela.geometry('400x350')
    janela.configure(bg='#1A3C34')
    janela.grab_set()

    tk.Label(janela, text='Credor:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    credor = tk.Entry(janela, font=('Arial', 12))
    credor.pack(pady=5)

    tk.Label(janela, text='Tipo:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    tipo = ttk.Combobox(janela, values=['Fornecedor', 'Fixa'], state='readonly')
    tipo.set('Fornecedor')
    tipo.pack(pady=5)

    tk.Label(janela, text='Valor (R$):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    valor = tk.Entry(janela, font=('Arial', 12))
    valor.pack(pady=5)

    tk.Label(janela, text='Vencimento (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    vencimento = tk.Entry(janela, font=('Arial', 12))
    vencimento.pack(pady=5)

    def salvar():
        if not (credor.get() and tipo.get() and valor.get() and vencimento.get()):
            messagebox.showerror('Erro', 'Preencha todos os campos', parent=janela)
            return
        if not validar_numero(valor.get()):
            messagebox.showerror('Erro', 'Valor inválido', parent=janela)
            return
        if not validar_data(vencimento.get()):
            messagebox.showerror('Erro', 'Data inválida', parent=janela)
            return

        financeiro = receberFinanceiro()
        ids = [c['id'] for c in financeiro['contas_pagar']]
        novo_id = max(ids) + 1 if ids else 1

        conta = {
            'id': novo_id,
            'credor': credor.get(),
            'tipo': tipo.get(),
            'valor': float(valor.get()),
            'vencimento': vencimento.get(),
            'status': 'Pendente'
        }

        financeiro['contas_pagar'].append(conta)
        salvarFinanceiro(financeiro)
        atualizarPagar('Todos', '')
        messagebox.showinfo('Sucesso', 'Conta adicionada', parent=janela)
        janela.destroy()

    tk.Button(janela, text='Salvar', command=salvar, **button_style).pack(pady=10)

def editarPagar(tabela):
    try:
        selected = tabela.focus()
        if not selected:
            raise ValueError
        valores = tabela.item(selected, 'values')
        if not valores:
            raise ValueError
        conta_id = int(valores[0])
    except:
        messagebox.showerror('Erro', 'Selecione uma conta', parent=root)
        return

    financeiro = receberFinanceiro()
    conta = None
    for c in financeiro['contas_pagar']:
        if c['id'] == conta_id:
            conta = c
            break

    if not conta:
        messagebox.showerror('Erro', 'Conta não encontrada', parent=root)
        return

    janela = tk.Toplevel(root)
    janela.title('Editar Conta a Pagar')
    janela.geometry('400x350')
    janela.configure(bg='#1A3C34')
    janela.grab_set()

    tk.Label(janela, text='Credor:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    credor = tk.Entry(janela, font=('Arial', 12))
    credor.insert(0, conta.get('credor', ''))
    credor.pack(pady=5)

    tk.Label(janela, text='Tipo:', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    tipo = ttk.Combobox(janela, values=['Fornecedor', 'Fixa'], state='readonly')
    tipo.set(conta.get('tipo', 'Fornecedor'))
    tipo.pack(pady=5)

    tk.Label(janela, text='Valor (R$):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    valor = tk.Entry(janela, font=('Arial', 12))
    valor.insert(0, f"{conta.get('valor', 0):.2f}")
    valor.pack(pady=5)

    tk.Label(janela, text='Vencimento (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(pady=5)
    vencimento = tk.Entry(janela, font=('Arial', 12))
    vencimento.insert(0, conta.get('vencimento', ''))
    vencimento.pack(pady=5)

    def salvar():
        if not (credor.get() and tipo.get() and valor.get() and vencimento.get()):
            messagebox.showerror('Erro', 'Preencha todos os campos', parent=janela)
            return
        if not validar_numero(valor.get()):
            messagebox.showerror('Erro', 'Valor inválido', parent=janela)
            return
        if not validar_data(vencimento.get()):
            messagebox.showerror('Erro', 'Data inválida', parent=janela)
            return

        conta['credor'] = credor.get()
        conta['tipo'] = tipo.get()
        conta['valor'] = float(valor.get())
        conta['vencimento'] = vencimento.get()
        
        salvarFinanceiro(financeiro)
        atualizarPagar('Todos', '')
        messagebox.showinfo('Sucesso', 'Conta atualizada', parent=janela)
        janela.destroy()

    tk.Button(janela, text='Salvar', command=salvar, **button_style).pack(pady=10)

def marcarPagoPagar(tabela):
    try:
        selected = tabela.focus()
        if not selected:
            raise ValueError
        valores = tabela.item(selected, 'values')
        if not valores:
            raise ValueError
        conta_id = int(valores[0])
    except:
        messagebox.showerror('Erro', 'Selecione uma conta', parent=root)
        return

    financeiro = receberFinanceiro()
    for conta in financeiro['contas_pagar']:
        if conta['id'] == conta_id:
            if conta.get('status') == 'Pago':
                messagebox.showinfo('Info', 'Conta já está paga', parent=root)
                return
            conta['status'] = 'Pago'
            salvarFinanceiro(financeiro)
            atualizarPagar('Todos', '')
            messagebox.showinfo('Sucesso', 'Conta marcada como paga', parent=root)
            return

    messagebox.showerror('Erro', 'Conta não encontrada', parent=root)

def excluirPagar(tabela):
    try:
        selected = tabela.focus()
        if not selected:
            raise ValueError
        valores = tabela.item(selected, 'values')
        if not valores:
            raise ValueError
        conta_id = int(valores[0])
    except:
        messagebox.showerror('Erro', 'Selecione uma conta', parent=root)
        return

    confirm = messagebox.askyesno('Confirmar', 'Confirma a exclusão?', parent=root)
    if not confirm:
        return

    financeiro = receberFinanceiro()
    financeiro['contas_pagar'] = [c for c in financeiro['contas_pagar'] if c['id'] != conta_id]

    salvarFinanceiro(financeiro)
    atualizarPagar('Todos', '')
    messagebox.showinfo('Sucesso', 'Conta excluída', parent=root)
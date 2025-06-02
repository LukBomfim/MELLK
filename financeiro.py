import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.pdfgen import canvas
import json, os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

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

def validar_data(data_str):
    if not data_str:
        return True
    try:
        datetime.strptime(data_str, '%d/%m/%Y')
        return True
    except ValueError:
        return False

def inicio():
    global root, frameInicial, resumo_labels, tabela_pagamentos, canvas_grafico, grafico_frame

    root = tk.Toplevel()
    root.geometry('1000x700')
    root.title('FINANCEIRO')
    root.state('zoomed')
    root.configure(bg='#1A3C34')

    # Manipulador de fechamento
    def on_closing():
        global canvas_grafico
        if canvas_grafico:
            canvas_grafico.get_tk_widget().destroy()
            canvas_grafico = None
        plt.close('all')  # Fecha todas as figuras do Matplotlib
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    frameInicial = tk.Frame(root, bg='#1A3C34')
    frameInicial.pack(fill='both', expand=True)

    frameInicial.grid_rowconfigure(0, weight=0)
    frameInicial.grid_rowconfigure(1, weight=0)
    frameInicial.grid_rowconfigure(2, weight=0)
    frameInicial.grid_rowconfigure(3, weight=0)
    frameInicial.grid_rowconfigure(4, weight=1)
    frameInicial.grid_rowconfigure(5, weight=0)
    frameInicial.grid_columnconfigure(0, weight=1)

    # Cabeçalho
    header_frame = tk.Frame(frameInicial, bg='#1A3C34')
    header_frame.grid(row=0, column=0, pady=20, sticky='ew')
    tk.Label(header_frame, text="Sistema de Vendas - Módulo Financeiro", font=('Arial', 16, 'bold'), fg='white',
             bg='#1A3C34').pack()

    # Frame para filtros
    filter_frame = tk.Frame(frameInicial, bg='#1A3C34')
    filter_frame.grid(row=1, column=0, pady=10, padx=20, sticky='ew')
    tk.Label(filter_frame, text='Data Início (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    data_inicio = tk.Entry(filter_frame, font=('Arial', 12), width=12)
    data_inicio.pack(side=tk.LEFT, padx=5)
    tk.Label(filter_frame, text='Data Fim (DD/MM/AAAA):', font=('Arial', 12), fg='white', bg='#1A3C34').pack(side=tk.LEFT)
    data_fim = tk.Entry(filter_frame, font=('Arial', 12), width=12)
    data_fim.pack(side=tk.LEFT, padx=5)
    tk.Button(filter_frame, text='Filtrar', command=lambda: atualizarResumo(data_inicio.get(), data_fim.get()),
              **button_style).pack(side=tk.LEFT, padx=5)

    # Frame para resultados
    resumo_frame = tk.Frame(frameInicial, bg='#1A3C34')
    resumo_frame.grid(row=2, column=0, pady=10, padx=20, sticky='ew')
    resumo_labels = {}
    labels = ['Faturamento Bruto', 'Descontos aplicados', 'Total líquido', 'Lucro estimado']
    for texto in labels:
        label = tk.Label(resumo_frame, text=f'{texto}: R$ 0,00', font=('Arial', 12), fg='white', bg='#1A3C34')
        label.pack(anchor='w')
        resumo_labels[texto] = label

    # Frame para formas de pagamento
    pagamento_frame = tk.Frame(frameInicial, bg='#1A3C34')
    pagamento_frame.grid(row=3, column=0, pady=10, padx=20, sticky='ew')
    tk.Label(pagamento_frame, text='Formas de Pagamento', font=('Arial', 14, 'bold'), fg='white', bg='#1A3C34').pack(anchor='w')
    colunas = ['forma', 'valor', 'percentual']
    tabela_pagamentos = ttk.Treeview(pagamento_frame, columns=colunas, show='headings', height=5)
    tabela_pagamentos.heading('forma', text='Forma de Pagamento')
    tabela_pagamentos.heading('valor', text='Valor Total')
    tabela_pagamentos.heading('percentual', text='% do Total')
    tabela_pagamentos.column('forma', width=150)
    tabela_pagamentos.column('valor', width=100)
    tabela_pagamentos.column('percentual', width=100)
    tabela_pagamentos.pack(fill='x')
    scrollbar = ttk.Scrollbar(pagamento_frame, orient='vertical', command=tabela_pagamentos.yview)
    tabela_pagamentos.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill='y')

    # Frame para gráfico
    grafico_frame = tk.Frame(frameInicial, bg='#1A3C34')
    grafico_frame.grid(row=4, column=0, pady=10, padx=20, sticky='nsew')

    canvas_grafico = None

    # Botões
    button_frame = tk.Frame(frameInicial, bg='#1A3C34')
    button_frame.grid(row=5, column=0, pady=20, sticky='ew')
    tk.Button(button_frame, text='Atualizar', command=lambda: atualizarResumo(data_inicio.get(), data_fim.get()),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Gerar Relatório', command=lambda: gerarRelatorio(data_inicio.get(), data_fim.get()),
              **button_style).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text='Voltar', command=on_closing, **button_style).pack(side=tk.LEFT, padx=5)

    # Inicializa com dados totais
    try:
        atualizarResumo('', '')
    except Exception as e:
        print(f"Erro ao inicializar resumo: {e}")

def atualizarResumo(data_inicio, data_fim):
    # Corrige a validação das datas
    if not (validar_data(data_inicio) and validar_data(data_fim)):
        messagebox.showerror('Erro', 'Formato de data inválido. Use DD/MM/AAAA')
        return

    vendas = receberVendas()
    faturamento_bruto = 0.0
    descontos = 0.0
    total_liquido = 0.0
    pagamentos = {'Dinheiro': 0.0, 'Pix': 0.0, 'Credito': 0.0, 'Debito': 0.0}  # Consistente com float

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

        faturamento_bruto += venda['bruto']
        descontos += venda['desconto']
        total_liquido += venda['total']
        for forma, valor in venda['pagamento'].items():
            if forma == 'Credito':
                pagamentos[forma] += sum(p['valor'] for p in valor)
            elif forma in ['Pix', 'Debito']:
                pagamentos[forma] += sum(valor)
            else:
                pagamentos[forma] += valor

    custo_estimado = faturamento_bruto * 0.6
    lucro_estimado = total_liquido - custo_estimado

    resumo_labels['Faturamento Bruto'].configure(text=f'Faturamento Bruto: R$ {faturamento_bruto:.2f}')
    resumo_labels['Descontos aplicados'].configure(text=f'Descontos aplicados: R$ {descontos:.2f}')
    resumo_labels['Total líquido'].configure(text=f'Total líquido: R$ {total_liquido:.2f}')
    resumo_labels['Lucro estimado'].configure(text=f'Lucro estimado: R$ {lucro_estimado:.2f}')

    for item in tabela_pagamentos.get_children():
        tabela_pagamentos.delete(item)
    total_pagamentos = sum(pagamentos.values())
    for forma, valor in pagamentos.items():
        percentual = (valor / total_pagamentos * 100) if total_pagamentos > 0 else 0
        tabela_pagamentos.insert('', 'end', values=(forma, f'R$ {valor:.2f}', f'{percentual:.1f}%'))

    global canvas_grafico
    if canvas_grafico:
        canvas_grafico.get_tk_widget().destroy()
        canvas_grafico = None
    plt.close('all')  # Fecha todas as figuras do Matplotlib antes de criar uma nova
    
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    fig_width = screen_width / 100
    fig_height = screen_height / 400
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))
    
    
    formas = [f for f in pagamentos if pagamentos[f] > 0]
    valores = [pagamentos[f] for f in formas]
    
    ax.bar(formas, valores, color="#4FA893")
    ax.set_title('Faturamento por Forma de Pagamento')
    ax.set_ylabel('R$')
    
    canvas_grafico = FigureCanvasTkAgg(fig, master=grafico_frame)  # Corrigido: apenas fig e master
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

        faturamento_bruto += venda['bruto']
        descontos += venda['desconto']
        total_liquido += venda['total']
        for forma, valor in venda['pagamento'].items():
            if forma == 'Credito':
                pagamentos[forma] += sum(p['valor'] for p in valor)
            elif forma in ['Pix', 'Debito']:
                pagamentos[forma] += sum(valor)
            else:
                pagamentos[forma] += valor

    custo_estimado = faturamento_bruto * 0.6
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
    linha(f'Descontos aplicados: R$ {descontos:.2f}')
    linha(f'Total líquido: R$ {total_liquido:.2f}')
    linha(f'Lucro estimado: R$ {lucro_estimado:.2f}')
    linha('-' * 40, s=10)

    linha('FORMAS DE PAGAMENTO', centro=True)
    linha('-' * 40, s=8)
    linha(f'{"TIPO":<15}{"VALOR":>10}{"%":>15}')
    linha('-' * 40, s=8)
    total_pagamentos = sum(pagamentos.values())
    for forma, valor in pagamentos.items():
        percentual = (valor / total_pagamentos * 100) if total_pagamentos > 0 else 0
        linha(f'{forma[:15]:<15}{valor:>10.2f}{percentual:>15.1f}')
    linha('-' * 40, s=8)

    pdf.save()
    os.startfile(pdf)
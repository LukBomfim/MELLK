import tkinter as tk
from tkinter import ttk
import json

def inicio():
    global root
    root = tk.Toplevel()
    root.geometry('1000x1000')
    root.state('zoomed')

    tk.Label(root, text='MÓDULO DE COMPRAS').pack()

    tk.Button(root, text='Nova Compra', command=novaCompra).pack()

def novaCompra():
    janela = tk.Toplevel(root)
    janela.grab_set()
    janela.transient(root)
    janela.geometry('1050x1000')

    tk.Label(janela, text='Fornecedor:')
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
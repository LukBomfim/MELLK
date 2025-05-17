import json
import tkinter as tk
import clientes, estoque

# VERIFICAÇÃO SE OS ARQUIVOS EXISTEM
arq = ('clientes.json', 'estoque.json')
for a in arq:
    try:
        with open(a, 'r', encoding='utf-8') as arq:
            json.load(arq)
            print(f'{a}: OK')

    except:
        with open(a, 'w+', encoding='utf-8') as arq:
            json.dump([], arq, indent=4, ensure_ascii=False)
            print(f'Arquivo criado: {a}')

# CRIAÇÃO DO MENU
menuInicial = tk.Tk()
menuInicial.geometry('800x400')
menuInicial.title('MELLK')
# menuInicial.state('zoomed')

fonte = ('Arial', 14)
titulo = tk.Label(menuInicial, text='MENU INICIAL', font=fonte)
titulo2 = tk.Label(menuInicial, text='MELLK', font=('Arial', 16), fg='red')
titulo.pack()
titulo2.pack()

# BOTÕES
tk.Button(menuInicial, text='Clientes', command=clientes.inicio, font=fonte).pack()
tk.Button(menuInicial, text='Vendas', font=fonte).pack()
tk.Button(menuInicial, text='Estoque', command=estoque.inicio,font=fonte).pack()
tk.Button(menuInicial, text='Financeiro', font=fonte).pack()
tk.Button(menuInicial, text='Compras', font=fonte).pack()

menuInicial.mainloop()

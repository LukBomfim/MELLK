import json
import tkinter as tk
from PIL import Image, ImageTk
import os
import clientes, estoque, vendas

# VERIFICAÇÃO SE OS ARQUIVOS EXISTEM
arq = ('clientes.json', 'estoque.json', 'vendas.json')
for a in arq:
    try:
        with open(a, 'r', encoding='utf-8') as arq:
            json.load(arq)
            print(f'{a}: OK')
    except:
        with open(a, 'w+', encoding='utf-8') as arq:
            json.dump([], arq, indent=4, ensure_ascii=False)
            print(f'Arquivo criado: {a}')

# Capturando o diretório de um file específico
script_dir = os.path.dirname(os.path.abspath(__file__))

# CRIAÇÃO DA JANELA PRINCIPAL
menuInicial = tk.Tk()
menuInicial.title('MELLK - Sistema de Vendas')
menuInicial.configure(bg='#1A3C34')

# Mudando o icon padrão do Tk
icon_path = os.path.join(script_dir, "mellk-logo.png")
icon_image = ImageTk.PhotoImage(file=icon_path)
menuInicial.iconphoto(True, icon_image)

# === Centralização da janela ===

largura_tela = menuInicial.winfo_screenwidth()
altura_tela = menuInicial.winfo_screenheight()

largura_janela = largura_tela - 150
altura_janela = altura_tela - 150

pos_x = (largura_tela - largura_janela) // 2
pos_y = (altura_tela - altura_janela - 150) // 2

menuInicial.geometry(f'{largura_janela}x{altura_janela}+{pos_x}+{pos_y}')
# ================================

# FRAME PARA O CABEÇALHO
header_frame = tk.Frame(menuInicial, bg='#1A3C34')
header_frame.pack(pady=20)

# CAMINHO ABSOLUTO DA IMAGEM
img_path = os.path.join(script_dir, "mellk-logo.png")

# LOGO
try:
    logo_image = Image.open(img_path)
    logo_image = logo_image.resize((100, 100), Image.Resampling.LANCZOS)
    logo_photo = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(header_frame, image=logo_photo, bg='#1A3C34')
    logo_label.image = logo_photo
    logo_label.pack()
except Exception as e:
    import traceback

    print("Erro ao carregar a imagem:")
    traceback.print_exc()
    tk.Label(header_frame, text="MELLK", font=('Arial', 24, 'bold'), fg='white', bg='#1A3C34').pack()

# TÍTULO
titulo = tk.Label(header_frame, text="Sistema de Vendas", font=('Arial', 16, 'bold'), fg='white', bg='#1A3C34')
titulo.pack(pady=2.5)

# BOTÕES
button_frame = tk.Frame(menuInicial, bg='#1A3C34')
button_frame.pack(expand=True)

# estilos do botão
button_style = {
    'font': ('Arial', 14),
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

tk.Button(button_frame, text='Clientes', command=clientes.inicio, **button_style).pack(pady=10)
tk.Button(button_frame, text='Vendas', command=vendas.inicio, **button_style).pack(pady=10)
tk.Button(button_frame, text='Estoque', command=estoque.inicio, **button_style).pack(pady=10)
tk.Button(button_frame, text='Financeiro', **button_style).pack(pady=10)
tk.Button(button_frame, text='Compras', **button_style).pack(pady=10)

# RODAPÉ
footer = tk.Label(menuInicial, text="© 2025 MELLK - Todos os direitos reservados", font=('Arial', 10), fg='white',
                  bg='#1A3C34')
footer.pack(side=tk.BOTTOM, pady=10)

menuInicial.mainloop()

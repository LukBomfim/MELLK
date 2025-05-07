import tkinter as tk
import arquivos
import cadastro_cliente

arq = 'clientes.json'

# VERIFICAÇÃO SE OS ARQUIVOS EXISTEM
'''for a in arq:
    arquivos.arqExiste(a)'''

root = tk.Tk()
root.title('MELLK')
root.geometry('500x500')
root.configure(bg='lightblue')

tk.Label(root, text='Menu Principal')

botaoNovoCliente = tk.Button(root, text='Novo Cliente',
                             command=cadastro_cliente.cadastrocliente)
botaoNovoCliente.pack()
botaoVerClientes = tk.Button(root, text='Ver Clientes Cadastrados',
                             command=cadastro_cliente.ver_cadastros)
botaoVerClientes.pack()

root.mainloop()
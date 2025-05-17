<h1>MellK</h1>
<br>
<h2>Este é um sistema de gestão comercial, desenvolvido para controlar cadastros, vendas, estoque e finanças de forma integrada:</h2>
<ol>
    <li>
        <b>Cadastro de Clientes</b>
        <ol>
            <li>
                Permite inserir, editar, excluir e listar clientes cadastrados.
            </li>
            <br>
            <li>
                Os dados armazenados para cada cliente incluem:
                <ul>
                    <li><code>nome</code></li>
                    <li><code>CPF/CNPJ</code></li>
                    <li><code>telefone</code></li>
                    <li><code>e-mail</code></li>
                    <li><code>endereço</code></li>
                </ul>
            </li>
        </ol>
    </li>
    <br>
    <li>
        <b>Cadastro de Produtos / Estoque</b>
        <ol>
            <li>
                Permite a inserção, edição, exclusão e listagem de produtos disponíveis para venda.
            </li>
            <br>
            <li>
                Cada produto possui os seguintes atributos:
                <ul>
                    <li><code>nome</code></li>
                    <li><code>categoria</code></li>
                    <li><code>preço de custo</code></li>
                    <li><code>preço de venda</code></li>
                    <li><code>código de barras</code></li>
                    <li><code>validade</code> (se aplicável)</li>
                </ul>
            </li>
            <br>
            <li>
                O sistema controla automaticamente a quantidade em estoque, ajustando conforme as vendas realizadas.
            </li>
        </ol>
    </li>
    <br>
    <li>
        <b>Pedidos / Vendas</b>
        <ol>
            <li>
                O sistema permite realizar vendas do tipo balcão (rápida) ou entrega (com endereço e frete).
            </li>
            <br>
            <li>
                Os produtos são selecionados diretamente do estoque, com verificação da disponibilidade.
            </li>
            <br>
            <li>
                Para vendas de balcão, o cadastro do cliente é opcional.
            </li>
            <br>
            <li>
                Cada pedido recebe um número único e um status de acompanhamento:
                <ul>
                    <li><code>em preparação</code></li>
                    <li><code>entregue</code></li>
                    <li><code>cancelado</code></li>
                </ul>
            </li>
        </ol>
    </li>
    <br>
    <li>
        <b>Entrega (opcional dentro das vendas)</b>
        <ol>
            <li>
                Se a opção de entrega for ativada, é possível registrar o endereço do cliente e o prazo estimado de entrega.
            </li>
            <br>
            <li>
                O cálculo do frete pode ser:
                <ul>
                    <li><code>fixo</code></li>
                    <li><code>baseado na distância</code></li>
                </ul>
            </li>
        </ol>
    </li>
    <br>
    <li>
        <b>Caixa / Pagamento</b>
        <ol>
            <li>
                O sistema permite escolher a forma de pagamento:
                <ul>
                    <li><code>dinheiro</code></li>
                    <li><code>cartão</code></li>
                    <li><code>pix</code></li>
                </ul>
            </li>
            <br>
            <li>
                Calcula automaticamente o troco a ser devolvido ao cliente, caso o pagamento seja em dinheiro.
            </li>
            <br>
            <li>
                Possui funcionalidade para aplicar descontos na venda.
            </li>
            <br>
            <li>
                Ao final da compra, é gerado um comprovante:
                <ul>
                    <li>via print de tela</li>
                    <li>ou exportado em arquivo <code>.txt</code></li>
                </ul>
            </li>
        </ol>
    </li>
    <br>
    <li>
        <b>Controle Financeiro</b>
        <ol>
            <li>
                Geração de relatórios de vendas por período (diário ou mensal).
            </li>
            <br>
            <li>
                Registro de entradas e saídas financeiras:
                <ul>
                    <li><code>custos fixos</code></li>
                    <li><code>compras de estoque</code></li>
                    <li><code>outras despesas operacionais</code></li>
                </ul>
            </li>
        </ol>
    </li>
</ol>

<h2>Possível Estrutura modular:</h2>
<ul>
    <li><code>clientes.py</code> – lógica de CRUD para clientes.</li>
    <li><code>produtos.py</code> – cadastro e controle de estoque.</li>
    <li><code>vendas.py</code> – gerenciamento de pedidos e fluxo de compra.</li>
    <li><code>entregas.py</code> – módulo opcional de logística e frete.</li>
    <li><code>caixa.py</code> – controle de pagamentos e descontos.</li>
    <li><code>financeiro.py</code> – relatórios e fluxo de caixa.</li>
    <li><code>main.py</code> – ponto de entrada e orquestração geral.</li>
</ul>

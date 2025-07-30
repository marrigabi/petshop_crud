from app.forms import ProdutoForm, FornecedorForm, CompraForm, MovimentacaoForm
from flask import Flask
from werkzeug.datastructures import MultiDict

# Cria uma app Flask de teste
def criar_app_para_testes():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'test'
    app.config['WTF_CSRF_ENABLED'] = False
    return app

# Testa ProdutoForm com dados válidos
def test_produto_form_valido():
    app = criar_app_para_testes()
    with app.test_request_context():
        form = ProdutoForm(data={
            'nome': 'Ração',
            'lote': 'L01',
            'validade': '2025-12-31',
            'quantidade': 10,
            'estoque_minimo': 2,
            'estoque_maximo': 20
        })
        assert form.validate() is True  

# Testa ProdutoForm com dados ausentes (inválido)
def test_produto_form_invalido():
    app = criar_app_para_testes()
    with app.test_request_context():
        form = ProdutoForm(data={})
        assert form.validate() is False 

# Testa FornecedorForm com dados válidos
def test_fornecedor_form_valido():
    app = criar_app_para_testes()
    with app.test_request_context():
        form = FornecedorForm(data={
            'nome': 'Fornecedor X',
            'contato': '1234',
            'avaliacao': 5
        })
        assert form.validate() is True 

# Testa FornecedorForm sem dados (inválido)
def test_fornecedor_form_invalido():
    app = criar_app_para_testes()
    with app.test_request_context():
        form = FornecedorForm(data={})
        assert form.validate() is False 

# Testa MovimentacaoForm com dados válidos e choices definidos
def test_movimentacao_form_valido():
    app = criar_app_para_testes()
    with app.test_request_context():
        form = MovimentacaoForm(data={
            'produto_id': 1,
            'tipo': 'entrada',
            'quantidade': 5,
            'motivo': 'Reposição'
        })

        form.produto_id.choices = [(1, 'Ração')]
        assert form.validate() is True 

# Testa MovimentacaoForm com campos vazios (inválido)
def test_movimentacao_form_invalido():
    app = criar_app_para_testes()
    with app.test_request_context():
        form_data = MultiDict({
            'produto_id': '', 
            'tipo': '',
            'quantidade': '',
            'motivo': ''
        })

        form = MovimentacaoForm(formdata=form_data)
        form.produto_id.choices = [(1, 'Ração')] 
        form.tipo.choices = [('entrada', 'Entrada'), ('saida', 'Saída')]
        assert form.validate() is False

# Testa CompraForm com um item e fornecedor válidos
def test_compra_form_valido():
    app = criar_app_para_testes()
    with app.test_request_context():
        form_data = MultiDict({
            'fornecedor_id': '1',
            'observacao': 'Compra teste',
            'itens-0-produto_id': '1',
            'itens-0-quantidade': '5'
        })

        form = CompraForm(formdata=form_data)
        form.fornecedor_id.choices = [(1, 'Fornecedor X')]
        form.itens[0].form.produto_id.choices = [(1, 'Ração')]
        assert form.validate() is True 

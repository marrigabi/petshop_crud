from datetime import datetime
from app.models import Produto, Fornecedor, Compra, ItemCompra, Movimentacao

def test_criar_produto():
    produto = Produto(
        nome="Ração Premium",
        lote="L123",
        validade=datetime(2025, 12, 31),
        quantidade=10,
        estoque_minimo=5,
        estoque_maximo=50
    )
    assert produto.nome == "Ração Premium"
    assert produto.quantidade == 10

def test_criar_fornecedor():
    fornecedor = Fornecedor(
        nome="Fornecedor Exemplo",
        contato="contato@exemplo.com",
        avaliacao=4
    )
    assert fornecedor.nome == "Fornecedor Exemplo"
    assert fornecedor.avaliacao == 4

def test_criar_compra():
    fornecedor = Fornecedor(nome="Fornecedor A")
    data_fake = datetime(2025, 1, 1)
    compra = Compra(
        fornecedor=fornecedor,
        observacao="Pedido urgente",
        data=data_fake
    )
    assert compra.observacao == "Pedido urgente"
    assert compra.fornecedor.nome == "Fornecedor A"
    assert compra.data == data_fake


def test_criar_item_compra():
    produto = Produto(
        nome="Ração",
        lote="L001",
        validade=datetime(2025, 1, 1),
        quantidade=10,
        estoque_minimo=2,
    )
    fornecedor = Fornecedor(
        nome="Fornecedor B",
        contato="contato@b.com",
        avaliacao=4
    )
    compra = Compra(
        fornecedor=fornecedor,
        observacao="Compra teste"
    )
    item = ItemCompra(
        produto=produto,
        compra=compra,
        quantidade=3
    )
    assert item.quantidade == 3
    assert item.produto.nome == "Ração"

def test_criar_movimentacao():
    produto = Produto(nome="Ração", quantidade=20)
    data_fake = datetime(2025, 1, 1)
    movimentacao = Movimentacao(
        produto=produto,
        tipo="saida",
        quantidade=5,
        motivo="Venda",
        data=data_fake
    )
    assert movimentacao.tipo == "saida"
    assert movimentacao.motivo == "Venda"
    assert movimentacao.data == data_fake
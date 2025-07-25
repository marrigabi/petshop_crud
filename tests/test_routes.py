from app.models import Fornecedor, Compra, Produto, Movimentacao
from app import db
from datetime import datetime, timezone

def test_listar_compras(client):
    fornecedor = Fornecedor(nome="FornY", contato="Contato Y", avaliacao=5)
    db.session.add(fornecedor)
    db.session.commit()

    compra = Compra(fornecedor_id=fornecedor.id, observacao="Compra teste", data=datetime.now(timezone.utc))
    db.session.add(compra)
    db.session.commit()

    response = client.get("/compras")
    assert response.status_code == 200
    assert b"Compra teste" in response.data
    
def test_listar_fornecedores(client):
    fornecedor = Fornecedor(nome="Fornecedor Teste", contato="(00)0000-0000", avaliacao=5)
    db.session.add(fornecedor)
    db.session.commit()

    response = client.get("/fornecedores")
    assert response.status_code == 200
    assert b"Fornecedor Teste" in response.data


def test_listar_produtos(client):
    produto = Produto(nome="Ração", lote="ABC123", validade=None,
                      quantidade=15, estoque_minimo=5, estoque_maximo=30)
    db.session.add(produto)
    db.session.commit()

    response = client.get("/produtos")
    assert response.status_code == 200
    assert "Ração" in response.data.decode("utf-8")

def test_novo_produto_form(client):
    response = client.get("/produtos/novo")
    assert response.status_code == 200
    assert b"Novo Produto" in response.data

def test_listar_movimentacoes(client):
    produto = Produto(nome="Vacina", lote="LZ99", validade=None, quantidade=50,
                      estoque_minimo=10, estoque_maximo=100)
    db.session.add(produto)
    db.session.commit()

    mov = Movimentacao(produto_id=produto.id, tipo="entrada", quantidade=20,
                       motivo="Reabastecimento", data=datetime.now(timezone.utc))
    db.session.add(mov)
    db.session.commit()

    response = client.get("/movimentacoes")
    assert response.status_code == 200
    assert b"Reabastecimento" in response.data
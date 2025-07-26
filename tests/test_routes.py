from app import db
from app.models import Produto, Fornecedor, Compra, Movimentacao
from datetime import datetime, timezone
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

def test_index_dashboard(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Dashboard" in response.data or b"Estoque" in response.data

def test_listar_produtos(client):
    produto = Produto(nome="Ração", lote="ABC123", validade=None,
                      quantidade=15, estoque_minimo=5, estoque_maximo=30)
    db.session.add(produto)
    db.session.commit()

    response = client.get("/produtos")
    assert response.status_code == 200
    assert "Ração" in response.data.decode("utf-8")
def test_buscar_produtos(client):
    response = client.get("/produtos?q=ra")
    assert response.status_code == 200

def test_novo_produto_form(client):
    response = client.get("/produtos/novo")
    assert response.status_code == 200
    assert b"Produto" in response.data

def test_novo_produto_post(client):
    response = client.post("/produtos/novo", data={
        "nome": "Produto Teste",
        "lote": "L123",
        "validade": "",
        "quantidade": 10,
        "estoque_minimo": 5,
        "estoque_maximo": 20
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b"Produto Teste" in response.data

def test_editar_produto(client):
    produto = Produto(nome="Editar", lote="ED1", validade=None,
                      quantidade=10, estoque_minimo=5, estoque_maximo=20)
    db.session.add(produto)
    db.session.commit()

    response = client.post(f"/produtos/{produto.id}/editar", data={
        "nome": "Editado",
        "lote": "ED1",
        "quantidade": 20,
        "estoque_minimo": 5,
        "estoque_maximo": 30
    }, follow_redirects=True)
    assert b"Editado" in response.data

def test_excluir_produto(client):
    produto = Produto(nome="Excluir", lote="EX1", validade=None,
                      quantidade=5, estoque_minimo=2, estoque_maximo=10)
    db.session.add(produto)
    db.session.commit()

    response = client.post(f"/produtos/{produto.id}/excluir", follow_redirects=True)
    assert response.status_code == 200

def test_historico_produto(client):
    produto = Produto(nome="Hist", lote="H1", validade=None,
                      quantidade=5, estoque_minimo=1, estoque_maximo=10)
    db.session.add(produto)
    db.session.commit()

    response = client.get(f"/produtos/{produto.id}/historico")
    assert response.status_code == 200

def test_listar_fornecedores(client):
    fornecedor = Fornecedor(nome="Fornecedor Teste", contato="(00)0000-0000", avaliacao=5)
    db.session.add(fornecedor)
    db.session.commit()

    response = client.get("/fornecedores")
    assert response.status_code == 200
    assert b"Fornecedor Teste" in response.data

def test_novo_fornecedor(client):
    response = client.post("/fornecedores/novo", data={
        "nome": "Fornecedor Novo",
        "contato": "123",
        "avaliacao": 5
    }, follow_redirects=True)
    assert b"Fornecedor Novo" in response.data

def test_editar_fornecedor(client):
    fornecedor = Fornecedor(nome="Edita Forn", contato="C", avaliacao=2)
    db.session.add(fornecedor)
    db.session.commit()

    response = client.post(f"/fornecedores/{fornecedor.id}/editar", data={
        "nome": "Fornecedor Editado",
        "contato": "Contato",
        "avaliacao": 4
    }, follow_redirects=True)
    assert b"Fornecedor Editado" in response.data

def test_excluir_fornecedor(client):
    fornecedor = Fornecedor(nome="Excluir Forn", contato="Z", avaliacao=3)
    db.session.add(fornecedor)
    db.session.commit()

    response = client.post(f"/fornecedores/{fornecedor.id}/excluir", follow_redirects=True)
    assert response.status_code == 200

def test_listar_compras(client):
    fornecedor = Fornecedor(nome="Forn", contato="123", avaliacao=3)
    db.session.add(fornecedor)
    db.session.commit()

    compra = Compra(fornecedor_id=fornecedor.id, observacao="Compra teste", data=datetime.now(timezone.utc))
    db.session.add(compra)
    db.session.commit()

    response = client.get("/compras")
    assert response.status_code == 200
    assert b"Compra teste" in response.data

def test_nova_compra_form_get(client):
    response = client.get("/compras/nova")
    assert response.status_code == 200

def test_nova_compra_post(client):
    fornecedor = Fornecedor(nome="Forn Compra", contato="Z", avaliacao=5)
    db.session.add(fornecedor)
    db.session.commit()

    response = client.post("/compras/nova", data={
        "fornecedor": fornecedor.id,
        "observacao": "Compra nova"
    }, follow_redirects=True)
    assert b"Compra nova" in response.data

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

def test_nova_movimentacao_post(client):
    produto = Produto(nome="Nova Mov", lote="XYZ", validade=None, quantidade=10,
                      estoque_minimo=1, estoque_maximo=20)
    db.session.add(produto)
    db.session.commit()

    response = client.post("/movimentacoes/nova", data={
        "produto": produto.id,
        "tipo": "entrada",
        "quantidade": 5,
        "motivo": "Teste"
    }, follow_redirects=True)
    assert b"Teste" in response.data

def test_relatorios_get(client):
    urls = [
        "/relatorios/giro",
        "/relatorios/vencidos",
        "/relatorios/parados",
        "/relatorios/estoque-baixo",
        "/relatorios/previsoes",
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code == 200

def test_export_estoque_baixo_redirect(client):
    response = client.get("/relatorios/estoque-baixo/exportar")
    assert response.status_code == 302 

def test_export_other_excel(client):
    urls = [
        "/relatorios/previsoes/exportar",
        "/relatorios/giro/exportar",
        "/relatorios/parados/exportar"
    ]
    for url in urls:
        response = client.get(url)
        assert response.status_code in (200, 302)

import pytest
from app.models import Produto, Fornecedor

def test_editar_produto_inexistente(client):
    response = client.get("/produtos/999999/editar")
    assert response.status_code == 404

def test_excluir_produto_inexistente(client):
    response = client.post("/produtos/999999/excluir")
    assert response.status_code == 404

def test_excluir_produto_get_method_not_allowed(client):
    response = client.get("/produtos/1/excluir")
    assert response.status_code == 405

def test_sugestao_compra_sem_produtos_estoque_baixo(client):
    response = client.get("/compras/sugestao", follow_redirects=True)
    assert "Não há produtos abaixo do estoque mínimo" in response.data.decode("utf-8")

def test_sugestao_compra_sem_fornecedor(client):
    produto = Produto(nome="Teste Produto", lote="L1", validade=None,
                      quantidade=0, estoque_minimo=5, estoque_maximo=10)
    from app import db
    db.session.add(produto)
    db.session.commit()

    from app.models import Fornecedor
    Fornecedor.query.delete()
    db.session.commit()

    response = client.get("/compras/sugestao", follow_redirects=True)
    assert "É necessário ter pelo menos um fornecedor" in response.data.decode("utf-8")

def test_exportar_estoque_baixo_redirect_quando_vazio(client):
    from app.models import Produto
    Produto.query.update({Produto.quantidade: Produto.estoque_minimo + 10})
    from app import db
    db.session.commit()

    response = client.get("/relatorios/estoque-baixo/exportar", follow_redirects=True)
    assert "Nenhum produto abaixo do estoque mínimo" in response.data.decode("utf-8")

def test_exportar_parados_redirect_quando_vazio(client):
    from app.models import Movimentacao, Produto
    from datetime import datetime, timezone
    produto = Produto(nome="MovProduto", lote="LZ", validade=None,
                      quantidade=10, estoque_minimo=5, estoque_maximo=20)
    from app import db
    db.session.add(produto)
    db.session.commit()

    mov = Movimentacao(produto_id=produto.id, tipo="saida", quantidade=1, motivo="Teste",
                       data=datetime.now(timezone.utc))
    db.session.add(mov)
    db.session.commit()

    response = client.get("/relatorios/parados/exportar", follow_redirects=True)
    assert b"Nenhum produto parado" in response.data

def test_exportar_estoque_baixo_xlsx(client):
    produto = Produto(nome="Produto Export", lote="LoteX", validade=None,
                      quantidade=0, estoque_minimo=5, estoque_maximo=10)
    from app import db
    db.session.add(produto)
    db.session.commit()

    response = client.get("/relatorios/estoque-baixo/exportar")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def test_exportar_previsoes_xlsx(client):
    response = client.get("/relatorios/previsoes/exportar")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def test_exportar_giro_xlsx(client):
    response = client.get("/relatorios/giro/exportar")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

def test_exportar_parados_xlsx(client):
    produto = Produto(nome="Produto Parado", lote="LP", validade=None,
                      quantidade=10, estoque_minimo=5, estoque_maximo=20)
    from app import db
    db.session.add(produto)
    db.session.commit()

    response = client.get("/relatorios/parados/exportar")
    assert response.status_code in (200, 302)



from app import app, db
from app.models import Produto, Fornecedor, Movimentacao, Compra, ItemCompra
from datetime import date, timedelta
import random

with app.app_context():
    print("⚠️ Limpando o banco...")
    db.drop_all()
    db.create_all()

    print("📦 Criando fornecedores...")
    fornecedores = [
        Fornecedor(nome="PetMax", contato="petmax@exemplo.com", avaliacao=4),
        Fornecedor(nome="Rações Brasil", contato="racoes@exemplo.com", avaliacao=5),
        Fornecedor(nome="Animal Farma", contato="farmacia@exemplo.com", avaliacao=3),
    ]
    db.session.add_all(fornecedores)
    db.session.commit()

    print("🐶 Criando produtos fictícios...")
    produtos = [
        Produto(nome="Ração Premium", lote="R001", validade=date.today() + timedelta(days=90), quantidade=15, estoque_minimo=5, estoque_maximo=50),
        Produto(nome="Shampoo Canino", lote="S002", validade=date.today() + timedelta(days=15), quantidade=4, estoque_minimo=5, estoque_maximo=30),
        Produto(nome="Antipulgas", lote="A003", validade=date.today() - timedelta(days=5), quantidade=0, estoque_minimo=2, estoque_maximo=20),
        Produto(nome="Coleira LED", lote="C004", validade=None, quantidade=12, estoque_minimo=3, estoque_maximo=25),
        Produto(nome="Petisco Natural", lote="P005", validade=date.today() + timedelta(days=5), quantidade=2, estoque_minimo=5, estoque_maximo=40),
        Produto(nome="Ração Light", lote="R006", validade=date.today() + timedelta(days=180), quantidade=20, estoque_minimo=10, estoque_maximo=60),
        Produto(nome="Tapete Higiênico", lote="T007", validade=None, quantidade=8, estoque_minimo=5, estoque_maximo=30),
        Produto(nome="Brinquedo Mordedor", lote="B008", validade=None, quantidade=0, estoque_minimo=5, estoque_maximo=15),
        Produto(nome="Sabonete Antiácaro", lote="S009", validade=date.today() + timedelta(days=60), quantidade=6, estoque_minimo=4, estoque_maximo=20),
        Produto(nome="Suplemento Canino", lote="S010", validade=date.today() - timedelta(days=1), quantidade=1, estoque_minimo=2, estoque_maximo=10),
    ]
    db.session.add_all(produtos)
    db.session.commit()

    print("🔄 Criando movimentações aleatórias...")
    tipos = ['entrada', 'saida']
    motivos = ['Venda', 'Perda', 'Ajuste', 'Devolução', 'Reposição']

    for p in produtos:
        for _ in range(random.randint(1, 3)):
            tipo = random.choice(tipos)
            quantidade = random.randint(1, 5)

            if tipo == 'saida' and p.quantidade - quantidade >= 0:
                p.quantidade -= quantidade
            elif tipo == 'entrada':
                p.quantidade += quantidade
            else:
                continue  # Evita estoque negativo

            mov = Movimentacao(
                produto_id=p.id,
                tipo=tipo,
                quantidade=quantidade,
                motivo=random.choice(motivos)
            )
            db.session.add(mov)

    db.session.commit()

    print("🛒 Gerando compras fictícias...")
    for _ in range(3):  # 3 compras simuladas
        fornecedor = random.choice(fornecedores)
        compra = Compra(fornecedor_id=fornecedor.id, observacao="Compra automática para testes")
        db.session.add(compra)
        db.session.flush()  # garante compra.id

        produtos_selecionados = random.sample(produtos, k=3)

        for produto in produtos_selecionados:
            qtd = random.randint(2, 10)
            item = ItemCompra(compra_id=compra.id, produto_id=produto.id, quantidade=qtd)
            db.session.add(item)

            # Atualiza estoque do produto
            produto.quantidade += qtd

    db.session.commit()
    print("✅ Banco populado com dados fictícios com sucesso!")

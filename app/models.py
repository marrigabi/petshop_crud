from app import db
from datetime import datetime

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    lote = db.Column(db.String(50))
    validade = db.Column(db.Date)
    quantidade = db.Column(db.Integer, default=0)
    estoque_minimo = db.Column(db.Integer, default=10)
    estoque_maximo = db.Column(db.Integer, default=100)

class Fornecedor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    contato = db.Column(db.String(100))
    avaliacao = db.Column(db.Integer)

class Compra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fornecedor_id = db.Column(db.Integer, db.ForeignKey('fornecedor.id'))
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacao = db.Column(db.String(200))
    fornecedor = db.relationship('Fornecedor', backref='compras')

class ItemCompra(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('compra.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'))
    quantidade = db.Column(db.Integer)
    compra = db.relationship('Compra', backref='itens')
    produto = db.relationship('Produto')

class Movimentacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey('produto.id'), nullable=False)
    tipo = db.Column(db.String(10))  # entrada ou saida
    quantidade = db.Column(db.Integer, nullable=False)
    motivo = db.Column(db.String(100))
    data = db.Column(db.DateTime, default=datetime.utcnow)

    produto = db.relationship('Produto')


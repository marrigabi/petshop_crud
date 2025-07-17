from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SubmitField, SelectField, FieldList, FormField
from wtforms.validators import DataRequired
from app.models import Fornecedor, Produto

class ProdutoForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    lote = StringField('Lote')
    validade = DateField('Validade', format='%Y-%m-%d')
    quantidade = IntegerField('Quantidade')
    estoque_minimo = IntegerField('Estoque Mínimo')
    estoque_maximo = IntegerField('Estoque Máximo')
    submit = SubmitField('Salvar')

class FornecedorForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired()])
    contato = StringField('Contato')
    avaliacao = IntegerField('Avaliação')
    submit = SubmitField('Salvar')

class ItemCompraForm(FlaskForm):
    produto_id = SelectField('Produto', coerce=int)
    quantidade = IntegerField('Quantidade')

class CompraForm(FlaskForm):
    fornecedor_id = SelectField('Fornecedor', coerce=int)
    observacao = StringField('Observação')
    itens = FieldList(FormField(ItemCompraForm), min_entries=1)
    submit = SubmitField('Salvar')

class MovimentacaoForm(FlaskForm):
    produto_id = SelectField('Produto', coerce=int)
    tipo = SelectField('Tipo', choices=[('entrada', 'Entrada'), ('saida', 'Saída')])
    quantidade = IntegerField('Quantidade', validators=[DataRequired()])
    motivo = StringField('Motivo', validators=[DataRequired()])
    submit = SubmitField('Registrar')

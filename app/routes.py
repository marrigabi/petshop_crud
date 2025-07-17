from flask import render_template, redirect, request, url_for, flash
from app import app, db
from app.models import Produto, Movimentacao
from datetime import datetime, date, timedelta
from sqlalchemy import func


from app.models import Movimentacao, Produto, Fornecedor, Compra, ItemCompra
from app.forms import MovimentacaoForm, ProdutoForm, FornecedorForm, CompraForm, ItemCompraForm
@app.route("/")
def dashboard():
    produtos = Produto.query.all()
    estoque_baixo = Produto.query.filter(Produto.quantidade < Produto.estoque_minimo).count()

    from datetime import date, timedelta
    proximo_vencimento = Produto.query.filter(
        Produto.validade != None,
        Produto.validade < date.today() + timedelta(days=7)
    ).count()

    return render_template("dashboard.html", produtos=produtos,
                           estoque_baixo=estoque_baixo,
                           proximo_vencimento=proximo_vencimento)


# Produtos
@app.route("/produtos")
def listar_produtos():
    termo = request.args.get("busca", "")
    if termo:
        produtos = Produto.query.filter(Produto.nome.ilike(f"%{termo}%")).all()
    else:
        produtos = Produto.query.all()
    return render_template("produtos.html", produtos=produtos, termo=termo)


@app.route("/produtos/novo", methods=["GET", "POST"])
def novo_produto():
    form = ProdutoForm()
    if form.validate_on_submit():
        produto = Produto(
            nome=form.nome.data,
            lote=form.lote.data,
            validade=form.validade.data,
            quantidade=form.quantidade.data,
            estoque_minimo=form.estoque_minimo.data,
            estoque_maximo=form.estoque_maximo.data
        )
        db.session.add(produto)
        db.session.commit()
        flash("Produto cadastrado com sucesso!", "success")
        return redirect(url_for("listar_produtos"))
    return render_template("produto_form.html", form=form, titulo="Novo Produto")

@app.route("/produtos/<int:id>/editar", methods=["GET", "POST"])
def editar_produto(id):
    produto = Produto.query.get_or_404(id)
    form = ProdutoForm(obj=produto)
    if form.validate_on_submit():
        form.populate_obj(produto)
        db.session.commit()
        flash("Produto atualizado com sucesso!", "success")
        return redirect(url_for("listar_produtos"))
    return render_template("produto_form.html", form=form, titulo="Editar Produto")

@app.route("/produtos/<int:id>/excluir", methods=["POST"])
def excluir_produto(id):
    produto = Produto.query.get_or_404(id)
    db.session.delete(produto)
    db.session.commit()
    flash("Produto excluído com sucesso!", "success")
    return redirect(url_for("listar_produtos"))

# Fornecedores
@app.route("/fornecedores")
def listar_fornecedores():
    fornecedores = Fornecedor.query.all()
    return render_template("fornecedores.html", fornecedores=fornecedores)

@app.route("/fornecedores/novo", methods=["GET", "POST"])
def novo_fornecedor():
    form = FornecedorForm()
    if form.validate_on_submit():
        fornecedor = Fornecedor(
            nome=form.nome.data,
            contato=form.contato.data,
            avaliacao=form.avaliacao.data
        )
        db.session.add(fornecedor)
        db.session.commit()
        flash("Fornecedor cadastrado com sucesso!", "success")
        return redirect(url_for("listar_fornecedores"))
    return render_template("fornecedor_form.html", form=form, titulo="Novo Fornecedor")

@app.route("/fornecedores/<int:id>/editar", methods=["GET", "POST"])
def editar_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    form = FornecedorForm(obj=fornecedor)
    if form.validate_on_submit():
        form.populate_obj(fornecedor)
        db.session.commit()
        flash("Fornecedor atualizado com sucesso!", "success")
        return redirect(url_for("listar_fornecedores"))
    return render_template("fornecedor_form.html", form=form, titulo="Editar Fornecedor")

@app.route("/fornecedores/<int:id>/excluir", methods=["POST"])
def excluir_fornecedor(id):
    fornecedor = Fornecedor.query.get_or_404(id)
    db.session.delete(fornecedor)
    db.session.commit()
    flash("Fornecedor excluído com sucesso!", "success")
    return redirect(url_for("listar_fornecedores"))

# Compras
@app.route("/compras")
def listar_compras():
    compras = Compra.query.all()
    return render_template("compras.html", compras=compras)

@app.route("/compras/nova", methods=["GET", "POST"])
def nova_compra():
    form = CompraForm()
    form.fornecedor_id.choices = [(f.id, f.nome) for f in Fornecedor.query.all()]
    produtos = Produto.query.all()
    form.itens[0].produto_id.choices = [(p.id, p.nome) for p in produtos]

    if request.method == "POST" and form.validate():
        compra = Compra(
            fornecedor_id=form.fornecedor_id.data,
            observacao=form.observacao.data
        )
        db.session.add(compra)
        db.session.flush()

        for item_form in form.itens:
            item = ItemCompra(
                compra_id=compra.id,
                produto_id=item_form.produto_id.data,
                quantidade=item_form.quantidade.data
            )
            produto = Produto.query.get(item.produto_id)
            produto.quantidade += item.quantidade
            db.session.add(item)

        db.session.commit()
        flash("Compra registrada com sucesso!", "success")
        return redirect(url_for("listar_compras"))

    return render_template("compra_form.html", form=form, titulo="Nova Compra")

@app.route("/movimentacoes")
def listar_movimentacoes():
    movimentacoes = Movimentacao.query.order_by(Movimentacao.data.desc()).all()
    return render_template("movimentacoes.html", movimentacoes=movimentacoes)

@app.route("/movimentacoes/nova", methods=["GET", "POST"])
def nova_movimentacao():
    form = MovimentacaoForm()
    form.produto_id.choices = [(p.id, p.nome) for p in Produto.query.order_by(Produto.nome).all()]

    if form.validate_on_submit():
        movimento = Movimentacao(
            produto_id=form.produto_id.data,
            tipo=form.tipo.data,
            quantidade=form.quantidade.data,
            motivo=form.motivo.data
        )

        produto = Produto.query.get(form.produto_id.data)
        if form.tipo.data == "entrada":
            produto.quantidade += form.quantidade.data
        elif form.tipo.data == "saida":
            produto.quantidade -= form.quantidade.data

        db.session.add(movimento)
        db.session.commit()
        flash("Movimentação registrada com sucesso!", "success")
        return redirect(url_for("listar_movimentacoes"))

    return render_template("movimentacao_form.html", form=form, titulo="Nova Movimentação")

@app.route("/relatorios/giro")
def relatorio_giro_estoque():
    giro = db.session.query(
        Produto.nome,
        func.sum(Movimentacao.quantidade).label("total_mov")
    ).join(Movimentacao).group_by(Produto.id).order_by(func.sum(Movimentacao.quantidade).desc()).all()

    return render_template("relatorio_giro.html", giro=giro)

@app.route("/relatorios/vencidos")
def relatorio_vencidos():
    vencidos = Produto.query.filter(Produto.validade != None, Produto.validade < date.today()).all()
    return render_template("relatorio_vencidos.html", produtos=vencidos)

@app.route("/relatorios/parados")
def relatorio_parados():
    dias = 30
    limite = datetime.utcnow() - timedelta(days=dias)

    produtos_movimentados = db.session.query(Movimentacao.produto_id).filter(Movimentacao.data >= limite).distinct()
    produtos_parados = Produto.query.filter(~Produto.id.in_(produtos_movimentados)).all()

    return render_template("relatorio_parados.html", produtos=produtos_parados, dias=dias)

@app.route("/produtos/<int:id>/historico")
def historico_produto(id):
    produto = Produto.query.get_or_404(id)
    movimentacoes = Movimentacao.query.filter_by(produto_id=id).order_by(Movimentacao.data.desc()).all()
    return render_template("produto_historico.html", produto=produto, movimentacoes=movimentacoes)

@app.route("/relatorios/estoque-baixo")
def relatorio_estoque_baixo():
    produtos = Produto.query.filter(Produto.quantidade < Produto.estoque_minimo).all()
    return render_template("relatorio_estoque_baixo.html", produtos=produtos)

@app.route("/compras/sugestao", methods=["GET", "POST"])
def sugestao_compra():
    produtos = Produto.query.filter(Produto.quantidade < Produto.estoque_minimo).all()
    
    if not produtos:
        flash("Não há produtos abaixo do estoque mínimo para sugerir uma compra.", "info")
        return redirect(url_for("relatorio_estoque_baixo"))
    
    # Para simplificar, vamos usar o primeiro fornecedor existente
    fornecedor = Fornecedor.query.first()
    if not fornecedor:
        flash("É necessário ter pelo menos um fornecedor cadastrado para gerar a sugestão.", "danger")
        return redirect(url_for("listar_fornecedores"))

    # Criar a compra
    compra = Compra(fornecedor_id=fornecedor.id, observacao="Compra gerada automaticamente por sugestão de estoque")
    db.session.add(compra)
    db.session.flush()  # Garante que compra.id já exista

    for p in produtos:
        quantidade_sugerida = max(p.estoque_maximo - p.quantidade, 1)
        item = ItemCompra(compra_id=compra.id, produto_id=p.id, quantidade=quantidade_sugerida)
        db.session.add(item)

    db.session.commit()
    flash("Sugestão de compra gerada com sucesso!", "success")
    return redirect(url_for("listar_compras"))

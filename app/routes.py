from flask import render_template, redirect, request, url_for, flash
from app import app, db
from app.models import Produto, Movimentacao
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.models import Movimentacao, Produto, Fornecedor, Compra, ItemCompra
from app.forms import MovimentacaoForm, ProdutoForm, FornecedorForm, CompraForm, ItemCompraForm
import pandas as pd
from flask import send_file
import io
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



@app.route("/")
def index():
    # Produtos mais movimentados (contagem de movimentações por produto)
    movimentacoes_por_produto = (
        db.session.query(Produto.nome, func.count(Movimentacao.id))
        .join(Movimentacao)
        .group_by(Produto.id)
        .order_by(func.count(Movimentacao.id).desc())
        .limit(5)
        .all()
    )

    nomes_produtos = [nome for nome, _ in movimentacoes_por_produto]
    qtd_movs = [qtd for _, qtd in movimentacoes_por_produto]

    # Tipo de movimentações
    tipos_mov = (
        db.session.query(Movimentacao.tipo, func.count(Movimentacao.id))
        .group_by(Movimentacao.tipo)
        .all()
    )
    tipos = [t[0] for t in tipos_mov]
    contagens = [t[1] for t in tipos_mov]

    # Compras por mês (últimos 6 meses)
    hoje = datetime.today()
    data_inicio = datetime(hoje.year, hoje.month - 5, 1) if hoje.month > 5 else datetime(hoje.year - 1, hoje.month + 7, 1)

    compras_por_mes = (
        db.session.query(func.strftime('%Y-%m', Compra.data), func.count(Compra.id))
        .filter(Compra.data >= data_inicio)
        .group_by(func.strftime('%Y-%m', Compra.data))
        .order_by(func.strftime('%Y-%m', Compra.data))
        .all()
    )

    meses = [m[0] for m in compras_por_mes]
    qtd_compras = [m[1] for m in compras_por_mes]

    return render_template("dashboard.html",
        nomes_produtos=nomes_produtos,
        qtd_movs=qtd_movs,
        tipos=tipos,
        contagens=contagens,
        meses=meses,
        qtd_compras=qtd_compras
    )


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


@app.route("/relatorios/previsoes")
def relatorio_previsoes():
    hoje = date.today()
    limite_validade = hoje + timedelta(days=30)

    # Produtos vencendo nos próximos 30 dias
    produtos_vencendo = Produto.query.filter(
        Produto.validade != None,
        Produto.validade <= limite_validade,
        Produto.validade >= hoje
    ).all()

    # Produtos com estoque crítico + giro recente (simples previsão)
    # Supondo que movimentações nas últimas 30 dias indicam consumo
    limite_data = hoje - timedelta(days=30)
    produtos_movimentados = (
        db.session.query(Produto.id, db.func.sum(Movimentacao.quantidade).label('total'))
        .join(Movimentacao)
        .filter(Movimentacao.data >= limite_data, Movimentacao.tipo == 'saida')
        .group_by(Produto.id)
        .having(db.func.sum(Movimentacao.quantidade) > 0)
        .all()
    )

    # Produtos com giro alto e estoque já próximo do mínimo
    ids_previsao_ruptura = [pid for pid, total in produtos_movimentados]
    produtos_em_alerta = Produto.query.filter(
        Produto.id.in_(ids_previsao_ruptura),
        Produto.quantidade <= Produto.estoque_minimo + 3  # margem
    ).all()

    return render_template(
        "relatorio_previsoes.html",
        produtos_vencendo=produtos_vencendo,
        produtos_em_alerta=produtos_em_alerta
    )


@app.route("/relatorios/estoque-baixo/exportar")
def exportar_estoque_baixo():
    produtos = Produto.query.filter(Produto.quantidade < Produto.estoque_minimo).all()

    if not produtos:
        flash("Nenhum produto abaixo do estoque mínimo para exportar.", "info")
        return redirect(url_for("relatorio_estoque_baixo"))

    data = [{
        "Nome": p.nome,
        "Lote": p.lote,
        "Quantidade Atual": p.quantidade,
        "Estoque Mínimo": p.estoque_minimo,
        "Estoque Máximo": p.estoque_maximo,
        "Sugestão de Compra": max(p.estoque_maximo - p.quantidade, 0)
    } for p in produtos]

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Estoque Baixo')

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="estoque_baixo.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/relatorios/previsoes/exportar")
def exportar_previsoes():
    from datetime import date, timedelta
    hoje = date.today()
    limite_validade = hoje + timedelta(days=30)
    limite_data = hoje - timedelta(days=30)

    # Produtos vencendo
    produtos_vencendo = Produto.query.filter(
        Produto.validade != None,
        Produto.validade <= limite_validade,
        Produto.validade >= hoje
    ).all()

    # Produtos com previsão de ruptura
    produtos_movimentados = (
        db.session.query(Produto.id, db.func.sum(Movimentacao.quantidade).label('total'))
        .join(Movimentacao)
        .filter(Movimentacao.data >= limite_data, Movimentacao.tipo == 'saida')
        .group_by(Produto.id)
        .having(db.func.sum(Movimentacao.quantidade) > 0)
        .all()
    )
    ids_alerta = [pid for pid, _ in produtos_movimentados]
    produtos_em_alerta = Produto.query.filter(
        Produto.id.in_(ids_alerta),
        Produto.quantidade <= Produto.estoque_minimo + 3
    ).all()

    # Montar planilhas separadas
    df1 = pd.DataFrame([{
        "Nome": p.nome,
        "Validade": p.validade.strftime('%d/%m/%Y'),
        "Quantidade": p.quantidade
    } for p in produtos_vencendo])

    df2 = pd.DataFrame([{
        "Nome": p.nome,
        "Qtd Atual": p.quantidade,
        "Estoque Mínimo": p.estoque_minimo
    } for p in produtos_em_alerta])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df1.to_excel(writer, index=False, sheet_name="Vencimento Próximo")
        df2.to_excel(writer, index=False, sheet_name="Ruptura Estoque")

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="relatorio_previsoes.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/relatorios/giro/exportar")
def exportar_giro():
    giro = (
        db.session.query(
            Produto.nome,
            db.func.count(Movimentacao.id).label('movimentacoes'),
            db.func.sum(Movimentacao.quantidade).label('quantidade')
        )
        .join(Movimentacao)
        .filter(Movimentacao.tipo == 'saida')
        .group_by(Produto.id)
        .order_by(db.func.sum(Movimentacao.quantidade).desc())
        .all()
    )

    df = pd.DataFrame([{
        "Produto": nome,
        "Movimentações": movs,
        "Qtd Total Saída": qtd
    } for nome, movs, qtd in giro])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Giro de Estoque")

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="giro_estoque.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@app.route("/relatorios/parados/exportar")
def exportar_parados():
    from datetime import date, timedelta
    hoje = date.today()
    dias = 30
    limite_data = hoje - timedelta(days=dias)

    # Produtos com movimentações de saída nos últimos 30 dias
    ativos = (
        db.session.query(Movimentacao.produto_id)
        .filter(Movimentacao.data >= limite_data, Movimentacao.tipo == 'saida')
        .distinct()
    )

    # Produtos que não estão na lista de ativos
    produtos_parados = Produto.query.filter(~Produto.id.in_(ativos)).all()

    if not produtos_parados:
        flash("Nenhum produto parado nos últimos 30 dias para exportar.", "info")
        return redirect(url_for("relatorio_parados"))

    # Gerar DataFrame
    df = pd.DataFrame([{
        "Nome": p.nome,
        "Lote": p.lote,
        "Quantidade": p.quantidade,
        "Validade": p.validade.strftime('%d/%m/%Y') if p.validade else "—"
    } for p in produtos_parados])

    # Gerar Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Produtos Parados")

    output.seek(0)
    return send_file(
        output,
        as_attachment=True,
        download_name="produtos_parados.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

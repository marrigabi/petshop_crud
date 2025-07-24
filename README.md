# 🐾 PetShop - Sistema de Gestão

Este é um sistema de gestão completo para Pet Shop, desenvolvido com **Flask + SQLAlchemy**, focado no controle de produtos, fornecedores, compras e movimentações de estoque.

---

##  Como rodar o projeto

### 1. Clone o repositório

```bash
git clone https://github.com/marrigabi/petshop_crud.git
cd petshop_crud
```

### 2. Crie e ative um ambiente virtual 

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\\Scripts\\activate   # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados (SQLite)
```bash
flask db init
flask db migrate -m "Criação inicial"
flask db upgrade
```
### 5. Execute o arquivo seed.py 

```bash
python seed.py
```
### 6. Execute o servidor
```bash
flask run
```

### Funcionalidades

📋 Produtos: Cadastro, controle de validade, estoque mínimo/máximo

👨‍💼 Fornecedores: Cadastro e avaliação

🛒 Compras: Ordem de compra, recebimento e atualização de estoque

🔄 Movimentações: Entradas, saídas, perdas, devoluções

📈 Relatórios:

- Giro de estoque

- Produtos vencidos

- Produtos parados

⚠️ Alertas:

- Estoque baixo

- Produtos com validade próxima

🔍 Busca de produtos

🎨 Layout responsivo com sidebar e Bootstrap 5

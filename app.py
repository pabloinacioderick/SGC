from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configurações
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///clientes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "chave-secreta"

db = SQLAlchemy(app)


# =========================
# MODELO CLIENTE
# =========================

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)


# Criar banco de dados
with app.app_context():
    db.create_all()


# =========================
# LISTAR CLIENTES
# =========================

@app.route("/")
def index():
    clientes = Cliente.query.all()

    return render_template(
        "index.html",
        clientes=clientes
    )


# =========================
# ADICIONAR CLIENTE
# =========================

@app.route("/adicionar", methods=["GET", "POST"])
def adicionar():

    if request.method == "POST":

        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        cpf = request.form["cpf"].strip()

        # Verificar campos
        if not nome or not email or not cpf:
            flash("Todos os campos são obrigatórios!", "erro")

            return render_template("adicionar.html")

        # Verificar CPF
        cliente_existente = Cliente.query.filter_by(
            cpf=cpf
        ).first()

        if cliente_existente:
            flash(
                "Já existe um cliente com este CPF!",
                "erro"
            )

            return render_template("adicionar.html")

        try:

            novo_cliente = Cliente(
                nome=nome,
                email=email,
                cpf=cpf
            )

            db.session.add(novo_cliente)
            db.session.commit()

            flash(
                "Cliente cadastrado com sucesso!",
                "sucesso"
            )

            return redirect(url_for("index"))

        except Exception as erro:

            db.session.rollback()

            flash(
                "Erro ao cadastrar cliente: " + str(erro),
                "erro"
            )

            return render_template("adicionar.html")

    return render_template("adicionar.html")


# =========================
# EDITAR CLIENTE
# =========================

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):

    cliente = Cliente.query.get_or_404(id)

    if request.method == "POST":

        nome = request.form["nome"].strip()
        email = request.form["email"].strip()
        cpf = request.form["cpf"].strip()

        # Verificar campos
        if not nome or not email or not cpf:

            flash(
                "Todos os campos são obrigatórios!",
                "erro"
            )

            return render_template(
                "editar.html",
                cliente=cliente
            )

        # Verificar CPF duplicado
        cliente_existente = Cliente.query.filter(
            Cliente.cpf == cpf,
            Cliente.id != id
        ).first()

        if cliente_existente:

            flash(
                "Outro cliente já possui este CPF!",
                "erro"
            )

            return render_template(
                "editar.html",
                cliente=cliente
            )

        try:

            cliente.nome = nome
            cliente.email = email
            cliente.cpf = cpf

            db.session.commit()

            flash(
                "Cliente atualizado com sucesso!",
                "sucesso"
            )

            return redirect(url_for("index"))

        except Exception as erro:

            db.session.rollback()

            flash(
                "Erro ao editar cliente: " + str(erro),
                "erro"
            )

            return render_template(
                "editar.html",
                cliente=cliente
            )

    return render_template(
        "editar.html",
        cliente=cliente
    )


# =========================
# DELETAR CLIENTE
# =========================

@app.route("/deletar/<int:id>")
def deletar(id):

    cliente = Cliente.query.get_or_404(id)

    try:

        db.session.delete(cliente)
        db.session.commit()

        flash(
            "Cliente excluído com sucesso!",
            "sucesso"
        )

    except Exception as erro:

        db.session.rollback()

        flash(
            "Erro ao excluir cliente: " + str(erro),
            "erro"
        )

    return redirect(url_for("index"))


# =========================
# INICIAR SERVIDOR
# =========================

if __name__ == "__main__":
    app.run(debug=True)
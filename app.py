from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Tarefa
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/tarefas.db'
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'
db.init_app(app)

with app.app_context():
    db.create_all()

# Função para buscar tarefa pelo ID
def get_task_by_id(task_id):
    return Tarefa.query.get(task_id)

# Página principal
@app.route('/')
def index():
    tarefas = Tarefa.query.order_by(Tarefa.ordem).all()
    return render_template('index.html', tarefas=tarefas)

# Inclusão de tarefa
@app.route('/new', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        nome = request.form['nome']
        custo = float(request.form['custo'])
        data_limite = datetime.strptime(request.form['data_limite'], '%Y-%m-%d')
        
        # Validação e criação da tarefa
        if Tarefa.query.filter_by(nome=nome).first():
            flash('Erro: Nome da tarefa já existe.')
            return redirect(url_for('new_task'))
        
        # Buscar a maior ordem atual
        nova_ordem = db.session.query(db.func.max(Tarefa.ordem)).scalar() or 0
        nova_tarefa = Tarefa(nome=nome, custo=custo, data_limite=data_limite, ordem=nova_ordem + 1)
        
        db.session.add(nova_tarefa)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('new_task.html')

# Exclusão de tarefa
@app.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    tarefa = Tarefa.query.get(id)
    if tarefa:
        db.session.delete(tarefa)
        db.session.commit()
        flash('Tarefa excluída com sucesso.')
    return redirect(url_for('index'))

# Edição de tarefa
@app.route('/edit_task/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    tarefa = get_task_by_id(id)  # Função que busca a tarefa pelo ID
    if not tarefa:
        flash("Tarefa não encontrada.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        novo_nome = request.form['nome']
        novo_custo = float(request.form['custo'])  # Certifique-se de converter para float
        nova_data_limite = datetime.strptime(request.form['data_limite'], '%Y-%m-%d')

        # Verifica se já existe uma tarefa com o mesmo nome, ignorando a tarefa atual
        if Tarefa.query.filter(Tarefa.nome == novo_nome, Tarefa.id != tarefa.id).first():
            flash("Erro: já existe uma tarefa com esse nome.")
            return redirect(url_for('edit_task', id=id))

        # Atualiza a tarefa se a validação passar
        tarefa.nome = novo_nome
        tarefa.custo = novo_custo
        tarefa.data_limite = nova_data_limite
        db.session.commit()  # Salva as alterações
        flash("Tarefa atualizada com sucesso!")
        return redirect(url_for('index'))

    return render_template('edit_task.html', tarefa=tarefa)

@app.route('/move_task/<int:id>/<direction>', methods=['POST'])
def move_task(id, direction):
    tarefa = Tarefa.query.get(id)
    if not tarefa:
        flash("Tarefa não encontrada.")
        return redirect(url_for('index'))
    
    # Obtém a tarefa imediatamente anterior ou posterior à tarefa atual
    if direction == 'up':
        # Se mover para cima, encontramos a tarefa anterior
        tarefa_anterior = Tarefa.query.filter(Tarefa.ordem < tarefa.ordem).order_by(Tarefa.ordem.desc()).first()
        if tarefa_anterior:
            # Troca as ordens
            tarefa.ordem, tarefa_anterior.ordem = tarefa_anterior.ordem, tarefa.ordem
            db.session.commit()
    elif direction == 'down':
        # Se mover para baixo, encontramos a tarefa posterior
        tarefa_posterior = Tarefa.query.filter(Tarefa.ordem > tarefa.ordem).order_by(Tarefa.ordem.asc()).first()
        if tarefa_posterior:
            # Troca as ordens
            tarefa.ordem, tarefa_posterior.ordem = tarefa_posterior.ordem, tarefa.ordem
            db.session.commit()
    
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()

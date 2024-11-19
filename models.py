# models.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Numeric

db = SQLAlchemy()

class Tarefa(db.Model):
    __tablename__ = 'tarefas'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), unique=True, nullable=False)
    custo = db.Column(Numeric(precision=50, scale=2), nullable=False)
    data_limite = db.Column(db.Date, nullable=False)
    ordem = db.Column(db.Integer, nullable=False)
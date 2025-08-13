from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager

class Usuario(UserMixin, db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    posts = db.relationship("Post", backref="autor", lazy=True)
    comentarios = db.relationship("Comentario", backref="autor", lazy=True)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id: str):
    return Usuario.query.get(int(user_id))

class Categoria(db.Model):
    __tablename__ = "categoria"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    posts = db.relationship("Post", backref="categoria", lazy=True)

class Post(db.Model):
    __tablename__ = "post"
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categoria.id"))

    comentarios = db.relationship("Comentario", backref="post", cascade="all, delete-orphan", lazy=True)

class Comentario(db.Model):
    __tablename__ = "comentario"
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.Text, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

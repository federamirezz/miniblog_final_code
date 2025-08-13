from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm, PostForm, CommentForm
from models import db, Usuario, Post, Comentario, Categoria
from datetime import datetime

# Inicializar la app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_super_secreta'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tu_contraseña@localhost/miniblog'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))

# Context processor → categorías disponibles en todo template
@app.context_processor
def inject_categorias():
    return dict(categorias=Categoria.query.all())

# Rutas principales
@app.route('/')
def index():
    posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
    return render_template('index.html', posts=posts)

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistrationForm()
    if form.validate_on_submit():
        usuario = Usuario(
            username=form.username.data,
            email=form.email.data
        )
        usuario.set_password(form.password.data)
        db.session.add(usuario)
        db.session.commit()
        flash('Cuenta creada con éxito. Ahora podés iniciar sesión.', 'success')
        return redirect(url_for('login'))
    return render_template('registro.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_password(form.password.data):
            login_user(usuario)
            flash('Sesión iniciada correctamente.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Credenciales inválidas', 'danger')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('index'))

@app.route('/post/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            titulo=form.titulo.data,
            contenido=form.contenido.data,
            autor=current_user,
            fecha_creacion=datetime.utcnow(),
            categoria_id=form.categoria.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Post creado con éxito.', 'success')
        return redirect(url_for('index'))
    return render_template('nuevo_post.html', form=form)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
def ver_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    if form.validate_on_submit() and current_user.is_authenticated:
        comentario = Comentario(
            texto=form.texto.data,
            autor=current_user,
            post=post,
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(comentario)
        db.session.commit()
        flash('Comentario agregado.', 'success')
        return redirect(url_for('ver_post', post_id=post.id))
    comentarios = Comentario.query.filter_by(post_id=post.id).order_by(Comentario.fecha_creacion.desc()).all()
    return render_template('ver_post.html', post=post, form=form, comentarios=comentarios)

if __name__ == '__main__':
    app.run(debug=True)

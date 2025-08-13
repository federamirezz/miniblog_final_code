from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from . import db
from .models import Usuario, Post, Comentario, Categoria
from .forms import RegistrationForm, LoginForm, PostForm, CommentForm

def init_routes(app):

    @app.route("/")
    def index():
        posts = Post.query.order_by(Post.fecha_creacion.desc()).all()
        return render_template("index.html", posts=posts)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = RegistrationForm()
        if form.validate_on_submit():
            exists = Usuario.query.filter(
                (Usuario.username == form.username.data) | (Usuario.email == form.email.data)
            ).first()
            if exists:
                flash("Usuario o correo ya existe.", "warning")
                return render_template("register.html", form=form)
            user = Usuario(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Cuenta creada con éxito.", "success")
            return redirect(url_for("login"))
        return render_template("register.html", form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))
        form = LoginForm()
        if form.validate_on_submit():
            user = Usuario.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                flash("Sesión iniciada.", "success")
                return redirect(url_for("index"))
            flash("Credenciales inválidas.", "danger")
        return render_template("login.html", form=form)

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("Sesión cerrada.", "info")
        return redirect(url_for("index"))

    @app.route("/post/new", methods=["GET", "POST"])
    @login_required
    def create_post():
        form = PostForm()
        form.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
        if form.validate_on_submit():
            post = Post(
                titulo=form.titulo.data,
                contenido=form.contenido.data,
                autor=current_user,
                fecha_creacion=datetime.utcnow(),
                categoria_id=form.categoria.data or None
            )
            db.session.add(post)
            db.session.commit()
            flash("Post creado con éxito.", "success")
            return redirect(url_for("index"))
        return render_template("create_post.html", form=form)

    @app.route("/post/<int:post_id>", methods=["GET", "POST"])
    def post_detail(post_id):
        post = Post.query.get_or_404(post_id)
        form = CommentForm()
        if form.validate_on_submit():
            if not current_user.is_authenticated:
                flash("Iniciá sesión para comentar.", "info")
                return redirect(url_for("login"))
            comentario = Comentario(
                texto=form.texto.data,
                autor=current_user,
                post=post
            )
            db.session.add(comentario)
            db.session.commit()
            flash("Comentario agregado.", "success")
            return redirect(url_for("post_detail", post_id=post.id))
        comentarios = Comentario.query.filter_by(post_id=post.id).order_by(Comentario.fecha_creacion.desc()).all()
        return render_template("post_detail.html", post=post, comentarios=comentarios, form=form)

    @app.route("/post/<int:post_id>/edit", methods=["GET", "POST"])
    @login_required
    def edit_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.autor.id != current_user.id:
            abort(403)
        form = PostForm()
        form.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
        if request.method == "GET":
            form.titulo.data = post.titulo
            form.contenido.data = post.contenido
            form.categoria.data = post.categoria_id
        if form.validate_on_submit():
            post.titulo = form.titulo.data
            post.contenido = form.contenido.data
            post.categoria_id = form.categoria.data
            db.session.commit()
            flash("Post actualizado.", "success")
            return redirect(url_for("post_detail", post_id=post.id))
        return render_template("edit_post.html", form=form)

    @app.route("/post/<int:post_id>/delete", methods=["POST"])
    @login_required
    def delete_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.autor.id != current_user.id:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash("Post eliminado.", "info")
        return redirect(url_for("index"))

    @app.route("/categories")
    def categories():
        cats = Categoria.query.all()
        return render_template("categories.html", categorias=cats)

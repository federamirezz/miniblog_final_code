from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime
from . import db
from .models import Usuario, Post, Comentario, Categoria
from .forms import RegistrationForm, LoginForm, PostForm, CommentForm

def init_routes(app):

    @app.route("/")
    def index():
        q = request.args.get("q", "").strip()
        categoria_id = request.args.get("categoria_id", type=int)

        query = Post.query
        if categoria_id:
            query = query.filter(Post.categoria_id == categoria_id)
        if q:
            like = f"%{q}%"
            query = query.filter((Post.titulo.ilike(like)) | (Post.contenido.ilike(like)))

        posts = query.order_by(Post.fecha_creacion.desc()).all()
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
                flash("Nombre de usuario o correo ya existe.", "warning")
                return render_template("register.html", form=form)

            user = Usuario(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Cuenta creada con éxito. Iniciá sesión.", "success")
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
                flash("Sesión iniciada correctamente.", "success")
                next_url = request.args.get("next")
                return redirect(next_url or url_for("index"))
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
        form.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre.asc()).all()]
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
            flash("Publicación creada.", "success")
            return redirect(url_for("index"))
        return render_template("create_post.html", form=form)

    @app.route("/post/<int:post_id>", methods=["GET", "POST"])
    def post_detail(post_id):
        post = Post.query.get_or_404(post_id)
        form = CommentForm()
        if form.validate_on_submit():
            if not current_user.is_authenticated:
                flash("Debés iniciar sesión para comentar.", "info")
                return redirect(url_for("login"))
            comentario = Comentario(
                texto=form.texto.data,
                autor=current_user,
                post=post,
                fecha_creacion=datetime.utcnow(),
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
        form.categoria.choices = [(c.id, c.nombre) for c in Categoria.query.order_by(Categoria.nombre.asc()).all()]
        if request.method == "GET":
            form.titulo.data = post.titulo
            form.contenido.data = post.contenido
            form.categoria.data = post.categoria_id
        if form.validate_on_submit():
            post.titulo = form.titulo.data
            post.contenido = form.contenido.data
            post.categoria_id = form.categoria.data
            db.session.commit()
            flash("Publicación actualizada.", "success")
            return redirect(url_for("post_detail", post_id=post.id))
        return render_template("edit_post.html", form=form, post=post)

    @app.route("/post/<int:post_id>/delete", methods=["POST"])
    @login_required
    def delete_post(post_id):
        post = Post.query.get_or_404(post_id)
        if post.autor.id != current_user.id:
            abort(403)
        db.session.delete(post)
        db.session.commit()
        flash("Publicación eliminada.", "info")
        return redirect(url_for("index"))

    @app.route("/categories")
    def categories():
        cats = Categoria.query.order_by(Categoria.nombre.asc()).all()
        return render_template("categories.html", categorias=cats)

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from markupsafe import Markup, escape
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "login"

    @app.template_filter("nl2br")
    def nl2br(s):
        if s is None:
            return ""
            return Markup("<br>".join(escape(s).splitlines()))

    from .models import Categoria
    @app.context_processor
    def inject_categories():
        try:
            return dict(categorias=Categoria.query.all())
        except Exception:
            return dict(categorias=[])

    from .routes import init_routes
    init_routes(app)

    return app

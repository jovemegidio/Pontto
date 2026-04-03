from flask import Flask
from config import Config
from extensions import db, login_manager


def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    from routes.auth import auth_bp
    from routes.ponto import ponto_bp
    from routes.admin import admin_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(ponto_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(api_bp, url_prefix='/api')

    with app.app_context():
        db.create_all()
        _criar_admin_padrao()
        _criar_conquistas()

    return app


def _criar_admin_padrao():
    from models import Usuario
    if not Usuario.query.filter_by(is_admin=True).first():
        admin = Usuario(
            nome='Administrador',
            email='admin@empresa.com',
            is_admin=True,
            cargo='Administrador',
            departamento='TI',
            avatar_cor='#8b5cf6',
        )
        admin.set_senha('admin123')
        db.session.add(admin)
        db.session.commit()


def _criar_conquistas():
    from models import Conquista
    for codigo, nome, descricao, icone, xp, cor in Conquista.DEFINICOES:
        if not Conquista.query.filter_by(codigo=codigo).first():
            c = Conquista(codigo=codigo, nome=nome, descricao=descricao,
                          icone=icone, xp_bonus=xp, cor=cor)
            db.session.add(c)
    db.session.commit()

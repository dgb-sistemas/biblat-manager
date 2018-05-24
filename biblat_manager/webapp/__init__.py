# -*- coding: utf-8 -*-
from flask import Flask
from flask_babelex import Babel

babel = Babel()


def create_app():
    app = Flask(__name__)

    # Configuraciones
    app.config.from_object('biblat_manager.webapp.config.default')

    # i18n
    babel.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

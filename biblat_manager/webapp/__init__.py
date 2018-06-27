# -*- coding: utf-8 -*-
from flask import Flask
from flask_babelex import Babel
from biblat_manager.config import settings
from flask_breadcrumbs import Breadcrumbs

babel = Babel()
breadcrumbs = Breadcrumbs()


def create_app(config_name):
    app = Flask(__name__)

    # Configuraciones
    app.config.from_object(settings.config[config_name])
    settings.config[config_name].init_app(app)

    # i18n
    babel.init_app(app)

    # Breadcrumbs
    breadcrumbs.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app

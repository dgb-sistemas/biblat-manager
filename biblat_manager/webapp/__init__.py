# -*- coding: utf-8 -*-
from flask import Flask
from flask_babelex import Babel
from biblat_manager.config import settings
from flask_breadcrumbs import Breadcrumbs
from flask_mongoengine import MongoEngine
from flask_mail import Mail

babel = Babel()
breadcrumbs = Breadcrumbs()
dbmongo = MongoEngine()
mail = Mail()


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
    # mongoDB
    dbmongo.init_app(app)

    # Mail
    mail.init_app(app)

    app.register_blueprint(main_blueprint)

    return app

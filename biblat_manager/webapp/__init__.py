# -*- coding: utf-8 -*-
from flask import Flask
from flask.json import JSONEncoder
from flask_babelex import Babel
from flask_babelex import lazy_gettext as __
from flask_breadcrumbs import Breadcrumbs
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_mail import Mail

from biblat_manager.config import settings

babel = Babel()
breadcrumbs = Breadcrumbs()
login_manager = LoginManager()
dbmongo = MongoEngine()
mail = Mail()


class CustomJSONEncoder(JSONEncoder):
    """This class adds support for lazy translation texts to Flask's
    JSON encoder. This is necessary when flashing translated texts."""
    def default(self, obj):
        from speaklater import is_lazy_string
        if is_lazy_string(obj):
            try:
                return unicode(obj)  # python 2
            except NameError:
                return str(obj)  # python 3
        return super(CustomJSONEncoder, self).default(obj)


def create_app(config_name):
    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    # Configuraciones
    app.config.from_object(settings.config[config_name])
    settings.config[config_name].init_app(app)

    # i18n
    babel.init_app(app)

    # Breadcrumbs
    breadcrumbs.init_app(app)

    from .main import main as main_blueprint
    # Login
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'main.login'
    login_manager.login_message_category = 'info'
    login_manager.login_message = __(u'Por favor inicie sesión para acceder a esta página.')
    login_manager.init_app(app)

    # mongoDB
    dbmongo.init_app(app)

    # Mail
    mail.init_app(app)

    app.register_blueprint(main_blueprint)

    return app

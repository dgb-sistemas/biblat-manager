# -*- coding: utf-8 -*-
from flask import Flask, url_for
from flask.json import JSONEncoder
from flask_babelex import Babel
from flask_babelex import lazy_gettext as __
from flask_breadcrumbs import Breadcrumbs
from flask_login import LoginManager
from flask_mongoengine import MongoEngine
from flask_mail import Mail
from flask_security import Security, MongoEngineUserDatastore

from flask_admin import Admin
from flask_admin import helpers as admin_helpers

from biblat_manager.config import settings

babel = Babel()
breadcrumbs = Breadcrumbs()
login_manager = LoginManager()
dbmongo = MongoEngine()
mail = Mail()
security = Security()
admin_obj = Admin(
    name='Biblat-Manager',
    base_template='admin/base.html',
    template_mode='bootstrap4'
)

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


def is_bool(value):
    return isinstance(value, bool)


def create_app(config_name):
    app = Flask(__name__)

    app.json_encoder = CustomJSONEncoder

    # Remove strict slash from Werkzeug
    app.url_map.strict_slashes = False

    # Jinja filters

    app.jinja_env.filters.update({
        'is_bool': is_bool,
    })

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

    # Setup Flask-Security
    from .models import User, Role
    app.user_datastore = MongoEngineUserDatastore(dbmongo, User, Role)
    security_ctx = security.init_app(app, app.user_datastore)

    # Mail
    mail.init_app(app)

    # Admin
    from .models import User, Revista, Disciplina
    from .admin.views import(
        AdminIndexView,
        UserModelView,
        RevistaModelView,
        DisciplinaModelView
    )
    admin_obj.init_app(app, index_view=AdminIndexView())
    admin_obj.add_view(UserModelView(User, name='Usuarios', endpoint='user'))
    admin_obj.add_view(RevistaModelView(Revista, name='Revistas', endpoint='revista'))
    admin_obj.add_view(DisciplinaModelView(Disciplina, name='Disciplina', endpoint='disciplina'))

    # flask-security views.
    @security_ctx.context_processor
    def security_context_processor():
        return dict(
            admin_base_template=admin_obj.base_template,
            admin_view=admin_obj.index_view,
            h=admin_helpers,
            get_url=url_for
        )

    app.register_blueprint(main_blueprint)

    return app


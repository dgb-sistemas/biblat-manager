# -*- coding: utf-8 -*-
from flask import (request,
                   session,
                   current_app,
                   redirect,
                   url_for,
                   abort,
                   render_template,
                   flash)
from flask_babelex import gettext as _, lazy_gettext as __
from flask_breadcrumbs import register_breadcrumb

from . import main
from biblat_manager.webapp import babel


@main.route('/', methods=['GET', 'POST'])
@register_breadcrumb(main, '.', __('Inicio'))
def index():
    data = {
        'html_title': 'Biblat Manager - Index'
    }
    flash('You successfully read this important success message.', 'success')
    flash('You successfully read this important error message.', 'error')
    flash('You successfully read this important warning message.', 'warning')
    flash('You successfully read this important info message.', 'info')
    return render_template('main/index.html', **data)


@main.route('/revistas', methods=['GET', 'POST'])
@register_breadcrumb(main, '.revistas', __('Revistas'))
def revistas():
    data = {
        'html_title': 'Biblat Manager - Revistas'
    }
    return render_template('main/index.html', **data)


# i18n
@babel.localeselector
def get_locale():
    langs = current_app.config.get('LANGUAGES')
    lang_from_headers = request.accept_languages.best_match(list(langs.keys()))

    if 'lang' not in list(session.keys()):
        session['lang'] = lang_from_headers

    if not lang_from_headers and not session['lang']:
        # Si no se puede detectar el idioma se asigna el predeterminado
        session['lang'] = current_app.config.get('BABEL_DEFAULT_LOCALE')

    return session['lang']


@main.route('/set_locale/<string:lang_code>/')
def set_locale(lang_code):
    langs = current_app.config.get('LANGUAGES')

    if lang_code not in list(langs.keys()):
        abort(400, _(u'Código de idioma inválido'))

    # Guardar lang_code en sesión
    session['lang'] = lang_code

    if request.referrer is None:
        return redirect(url_for('main.index'))
    return redirect(request.referrer)


@main.route('/menutoggle/')
def set_menutoggle():
    session['menutoggle'] = 'open' \
        if session.get('menutoggle', '') == '' else ''
    return session['menutoggle']

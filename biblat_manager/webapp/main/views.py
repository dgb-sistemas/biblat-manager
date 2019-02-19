# -*- coding: utf-8 -*-
import socket
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
from flask_login import current_user, login_user, logout_user, login_required
from biblat_schema.models import Revista
from flask_mongoengine import Pagination

from . import main
from biblat_manager.webapp import babel, controllers
from biblat_manager.webapp.forms import (
    RegistrationForm, LoginForm, EmailForm, PasswordForm, RevistaForm
)
from biblat_manager.webapp.models import User
from biblat_manager.webapp.utils import get_timed_serializer


@main.route('/', methods=['GET', 'POST'])
@register_breadcrumb(main, '.', __('Inicio'))
@login_required
def index():
    data = {
        'html_title': 'Biblat Manager - Index'
    }
    flash('You successfully read this important success message.', 'success')
    flash('You successfully read this important error message.', 'error')
    flash('You successfully read this important warning message.', 'warning')
    flash('You successfully read this important info message.', 'info')
    return render_template('main/index.html', **data)



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


@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('.login'))


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('.index'))
    form = LoginForm()
    if request.method == 'POST' and form.validate():
        user = User.objects(email=form.email.data).first()
        if user and user.check_password_hash(form.password.data) \
                and user.email_confirmed:
            login_user(user, remember=form.remember.data)
            flash(_('Sesión iniciada como %s' % user.email), 'success')
            return redirect(session.get('next') or url_for('.index'))
        if not user:
            flash(_('Usuario no registrado'), 'error')
        if user and not user.check_password_hash(form.password.data):
            flash(_('Contraseña incorrecta'), 'error')
        if user and not user.email_confirmed:
            flash(_('Correo electrónico no verificado'), 'error')
    return render_template('auth/login.html', form=form)


# USER
@main.route('/usuarios', methods=['GET', 'POST'])
@main.route('/usuarios/<int:page>', methods=['GET', 'POST'])
@register_breadcrumb(main, '.users', __('Usuarios'))
@login_required
def list_users(page=1):
    # TODO: implementación de borrado de usuarios
    # TODO: implementación de reenvío de correo de confirmación
    order_by = request.args.get('order_by', None)
    column_list = {
        'username': _('Nombre de usuario'),
        'email': _('Correo electrónico'),
        'email_confirmed': _('Correo verificado?'),
    }
    users = User.objects.order_by(order_by).paginate(page=page, per_page=10)
    data = {
        'html_title': 'Biblat Manager - %s' % _('Usuarios'),
        'users': users,
        'order_by': order_by,
        'column_list': column_list
    }
    return render_template('main/users.html', **data)


@main.route('/usuarios/detalle/<user_id>', methods=['GET', 'POST'])
@register_breadcrumb(main, '.users.detail', __('Detalle'),
                     endpoint_arguments_constructor=lambda: {
                         'user_id': request.view_args['user_id']
                     })
@login_required
def user_detail(user_id):
    user = User.get_by_id(user_id)
    data = {
        'user': user
    }
    return render_template('main/user.html', **data)


@main.route('/usuarios/editar/<user_id>', methods=['GET', 'POST'])
@register_breadcrumb(main, '.users.edit', __('Editar'),
                     endpoint_arguments_constructor=lambda: {
                         'user_id': request.view_args['user_id']
                     })
@login_required
def user_edit(user_id):
    # TODO: permitir la actualización de usuarios sin actualizar contraseña
    user = User.get_by_id(user_id)
    form = RegistrationForm(obj=user)
    if request.method == 'POST' and form.validate():
        existing_user = User.get_by_email(form.email.data)
        if existing_user is None or user.id == existing_user.id:
            update_user = User.get_by_id(user_id)
            update_user.username = form.username.data
            update_user.email = form.email.data
            update_user.password = form.password.data
            update_user.save()
            flash(_('Usuario actualizado correctamente!'), 'info')
            if user.email != update_user.email:
                user.email_confirmed = False
                user.save()
                try:
                    # TODO: enviar email de actualización
                    was_sent, error_msg = update_user.send_confirmation_email()
                except (ValueError, socket.error) as e:
                    was_sent = False
                    error_msg = str(e)
                # Enviamos el email de confirmación al usuario.
                if was_sent:
                    flash(_('Se envío un correo de confirmación a: %(email)s',
                            email=update_user.email), 'info')
                else:
                    flash(_('Ocurrió un error en el envío del correo de '
                            'confirmación  a: %(email)s %(error_msg)s',
                            email=update_user.email, error_msg=error_msg),
                          'error')
        else:
            flash(_('El correo electrónico ya esta registrado'), 'error')
    return render_template('forms/register.html', form=form)


@main.route('/usuarios/agregar', methods=['GET', 'POST'])
@register_breadcrumb(main, '.users.add', __('Agregar'))
@login_required
def user_add():
    form = RegistrationForm()
    if request.method == 'POST' and form.validate():
        existing_user = User.get_by_email(form.email.data)
        if existing_user is None:
            user_data = {
                'username': form.username.data,
                'email': form.email.data,
                'password': form.password.data
            }
            user = User(**user_data).save()
            try:
                was_sent, error_msg = user.send_confirmation_email()
            except (ValueError, socket.error) as e:
                was_sent = False
                error_msg = str(e)
            # Enviamos el email de confirmación al usuario.
            if was_sent:
                flash(_('Se envío un correo de confirmación a: %(email)s',
                        email=user.email), 'info')
            else:
                flash(_('Ocurrió un error en el envío del correo de '
                        'confirmación  a: %(email)s %(error_msg)s',
                        email=user.email, error_msg=error_msg),
                      'error')
            return redirect(url_for('main.user_add'))
        else:
            flash(_('El correo electrónico ya esta registrado'), 'error')
    return render_template('forms/register.html', form=form)


@main.route('/user/confirm/<token>')
def confirm_email(token):
    try:
        ts = get_timed_serializer()
        email = ts.loads(token,
                         salt=current_app.config.get('TOKEN_EMAIL_SALT'),
                         max_age=current_app.config.get('TOKEN_MAX_AGE'))
    except Exception:  # posibles exepciones: https://pythonhosted.org/itsdangerous/#exceptions
        abort(404)

    user = User.get_by_email(email)
    if not user:
        abort(404, _('Usuario no encontrado'))

    controllers.set_user_email_confirmed(user)
    flash(_('Email: %(email)s confirmado com éxito!', email=user.email), 'success')
    return redirect(url_for('.index'))


@main.route('/reset/password', methods=['GET', 'POST'])
def reset():
    form = EmailForm()

    if request.method == 'POST' and form.validate():
        user = User.get_by_email(form.email.data)
        if not user:
            flash(_('Usuario no registrado'), 'error')
            return render_template('auth/reset.html', form=form)
        if not user.email_confirmed:
            user.send_confirmation_email()
            return render_template('auth/unconfirmed_email.html')

        was_sent, error_msg = user.send_reset_password_email()
        if was_sent:
            flash(_('Se enviaron instrucciones para recuperar su contraseña '
                    'al correo: %(email)s', email=user.email), 'info')
        else:
            flash(_('Ocurrió un problema al enviar el correo con las '
                    'instrucciones de recuperación de contraseña a la '
                    'dirección: %(email)s. Erro: %(error)s',
                    email=user.email,
                    error=error_msg),
                  'error')

        return redirect(url_for('.index'))

    return render_template('auth/reset.html', form=form)


@main.route('/reset/password/<token>', methods=['GET', 'POST'])
def reset_with_token(token):
    try:
        ts = get_timed_serializer()
        email = ts.loads(token,
                         salt=current_app.config.get('TOKEN_EMAIL_SALT'),
                         max_age=current_app.config.get('TOKEN_MAX_AGE'))
    except Exception:
        abort(404, _('Token inválido'))

    form = PasswordForm()
    if request.method == 'POST' and form.validate():
        user = User.get_by_email(email)
        if not user.email_confirmed:
            user.send_confirmation_email()
            return render_template('auth/unconfirmed_email.html')

        controllers.set_user_password(user, form.password.data)
        flash(_('Nueva contraseña guardada con éxito!'), 'success')
        return redirect(url_for('.index'))

    data = {
        'form': form,
        'token': token
    }
    return render_template('auth/reset_with_token.html', **data)


@main.route('/revistas')
@main.route('/revistas/<int:page>', methods=['GET', 'POST'])
@register_breadcrumb(main, '.revistas', __('Revistas'))
@login_required
def revista_list(page=1):
    # Listado de documentos de la revista
    order_by = request.args.get('order_by', None)
    column_list = {
        'issn': _('ISSN'),
        'titulo_revista': _('Título de la revista'),
        'fecha_creacion': _('Fecha de creación'),
        'fecha_actualizacion': _('Fecha de actualización'),
    }
    journals = Pagination(Revista.objects.order_by(order_by), page=page, per_page=10)
    data = {
        'html_title': 'Biblat Manager - %s' % _('Revistas'),
        'journals': journals,
        'order_by': order_by,
        'column_list': column_list
    }
    return render_template('forms/listar_revistas.html', **data)


@main.route('/revistas/agregar', methods=['GET', 'POST'])
@register_breadcrumb(main, '.revistas.add', __('Agregar revista'))
@login_required
def revista_add():
    # TODO: Registro de información de nueva revista.
    form = RevistaForm()
    if form.validate_on_submit():
        flash(_('Datos correctos'), 'success')
        return render_template('forms/revistas_add.html', form=form)
    else:
        flash(_('La revista ya existe'), 'error')
    for field in form:
        if field.type == 'FieldList' and field.min_entries == 0 and len(field) == 0:
            field.append_entry()
    return render_template('forms/revistas_add.html', form=form)


@main.route('/revistas/editar')
@register_breadcrumb(main, '.revistas.edit', __('Editar'))
# @login_required
def revista_edit():
    # Edición de documentos de la revista
    form = RevistaForm()
    if form.validate_on_submit():
        flash(_('Datos correctos'), 'success')
        return render_template('forms/revistas_add.html', form=form)
    for field in form:
        if field.type == 'FieldList' and field.min_entries == 0 and len(field) == 0:
            field.append_entry()
    return render_template('forms/revistas_add.html', form=form)

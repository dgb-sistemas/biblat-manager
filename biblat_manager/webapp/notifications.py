# -*- coding: utf-8 -*-
import six
from flask import url_for, render_template, current_app
from . import utils


def send_confirmation_email(recipient_email):
    """
    Envía un email de confirmación a ``recipient_email``
    Regresa:
     - (True, '') em caso de éxito.
     - (False, 'MENSAJE DE ERROR/EXCEPCIÓN') en caso de error/excepción
    """
    if not isinstance(recipient_email, six.string_types) \
            or not utils.REGEX_EMAIL.match(recipient_email):
        raise ValueError('recipient_email é inválido!')
    try:
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email,
                         salt=current_app.config.get('TOKEN_EMAIL_SALT'))
    except Exception as e:
        return False, 'Token inválido: %s' % str(e)
    else:
        confirm_url = url_for('main.confirm_email', token=token, _external=True)
        sent_results = utils.send_email(
            recipient_email,
            "Confirmación de correo electrónico",
            render_template('email/activate.html', confirm_url=confirm_url))
        return sent_results


def send_reset_password_email(recipient_email):
    """
    Envía un corre con las instrucciones para recuperar la contraseña de ``recipient_email``
    Regresa:
     - (True, '') em caso de éxito.
     - (False, 'MENSAJE DE ERROR/EXCEPCIÓN') en caso de error/excepción
    """
    if not isinstance(recipient_email, six.string_types) \
            or not utils.REGEX_EMAIL.match(recipient_email):
        raise ValueError('recipient_email es inválido!')
    try:
        ts = utils.get_timed_serializer()
        token = ts.dumps(recipient_email,
                         salt=current_app.config.get('TOKEN_EMAIL_SALT'))
    except Exception as e:
        return False, 'Token inválido: %s' % str(e)
    else:
        recover_url = url_for('main.reset_with_token', token=token,_external=True)
        sent_results = utils.send_email(
            recipient_email,
            "Instrucciones para recuperar su contraseña",
            render_template('email/recover.html', recover_url=recover_url))

        return sent_results

# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __
from .models import User


# -------- USER --------
def set_user_email_confirmed(user):
    """
    Actualiza un usuario (user) asignando el email como confirmado
    (atributo email_confirmed = True).
    """

    if not isinstance(user, User):
        raise ValueError(__('Usuario debe ser de tipo %s' % User))

    user.email_confirmed = True
    user.save()


def set_user_password(user, password):
    """
     Actualiza un usuario (user) con la contraseña (password) del parámetro
    """

    if not isinstance(user, User):
        raise ValueError(__('Usuario debe ser de tipo %s' % User))

    user.password = password
    user.save()


def create_user(user_email, user_password, user_email_confirmed):
    """
    Crea un nuevo usuario
    Parámetros:
    ``user_email`` correo electrónico,
    ``user_password`` contraseña en texto plano,
    ``user_email_confirmed`` bool para confirmar el correo electrónico
    """
    user_data = {
        'username': user_email.split("@")[0],
        'email': user_email,
        'password': user_password,
        'email_confirmed': user_email_confirmed
    }
    new_user = User(**user_data).save()

    return new_user

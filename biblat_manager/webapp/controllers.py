# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __
from .models import User


# -------- USER --------
def get_user_by_email(email):
    """
    Regresa un usuario cuando el atributo email sea igual al parámetro email,
    en caso de que email no sea un string regresa un ValueError.
    """
    if not isinstance(email, str):
        raise ValueError(__('El parámetro email debe ser un string'))
    return User.objects(email=email).first()


def set_user_email_confirmed(user):
    """
    Actualiza un usuario (user) asignando el email como confirmado
    (atributo email_confirmed = True).
    """

    if not isinstance(user, User):
        raise ValueError(__('Usuario debe ser de tipo %s' % User))

    user.email_confirmed = True
    user.save()

# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, validators


class RegistrationForm(FlaskForm):
    username = StringField(__('Nombre de usuario'), [
        validators.Length(min=4, max=25),
        validators.DataRequired()
    ])
    email = StringField(__('Correo electrónico'), [
        validators.Length(min=6, max=35),
        validators.Email(),
        validators.DataRequired()
    ])
    password = PasswordField(__('Contraseña'), [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='La contraseñas deben coincidir')
    ])
    confirm = PasswordField(__('Confirmar contraseña'))


class EmailForm(FlaskForm):
    email = StringField(__('Email'), validators=[
        validators.required(),
        validators.email()])


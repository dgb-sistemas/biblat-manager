# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, validators, IntegerField, DateTimeField


class RegistrationForm(FlaskForm):
    username = StringField(__('Nombre de usuario'), [
        validators.Length(min=4, max=25),
        validators.DataRequired()
    ])
    email = StringField(__('Correo electrónico'), [
        validators.Length(min=6, max=35),
        validators.Email(__('Correo electrónico inválido!')),
        validators.DataRequired()
    ])
    password = PasswordField(__('Contraseña'), [
        validators.DataRequired(),
        validators.EqualTo('confirm',
                           message=__('Las contraseñas deben coincidir'))
    ])
    confirm = PasswordField(__('Confirmar contraseña'))


class LoginForm(FlaskForm):
    email = StringField(__('Correo electrónico'), [
        validators.Length(min=6, max=35),
        validators.Email(__('Correo electrónico inválido!')),
        validators.DataRequired()
    ])
    password = PasswordField(__('Contraseña'), [
        validators.DataRequired(),
    ])

    remember = BooleanField(__('Recordarme'))


class EmailForm(FlaskForm):
    email = StringField(__('Email'), validators=[
        validators.required(),
        validators.email(__('Correo electrónico inválido!'))])


class PasswordForm(FlaskForm):
    password = PasswordField(__('Nueva contraseña'), [
        validators.DataRequired(),
        validators.EqualTo(
            'confirm',
            message=__('Las contraseñas deben coincidir')
        )
    ])
    confirm = PasswordField(__('Confirmar contraseña'))

class FasciculoForm(FlaskForm):
    revista = StringField(__('Revista'),[
        validators.Length(max=150),
        validators.DataRequired()
    ])
    volumen = IntegerField(__('Volumen'),[
        validators.Length(max=15),
    ])
    numero = IntegerField(__('Numero'),[
        validators.Length(max=15),
    ])
    anio = IntegerField(__('Año'),[
        validators.Length(max=4),
        validators.DataRequired()
    ])
    "**** Tengo duda de como manejar el mes en el formato, con nombre o con numero *****"
    mes_inicial = IntegerField(__('Mes inicial'),[
        validators.DataRequired()
    ])
    mes_final = IntegerField(__('Mes final'),[
        validators.DataRequired()
    ])
    parte = StringField(__('Parte'),[
        validators.Length(max=100),
        validators.DataRequired()
    ])
    fecha_creacion = DateTimeField(__('Fecha de creacion'),[
        validators.DataRequired()
    ])
    fecha_actualizacion = StringField(__('Fecha de actualizacion'),[
        validators.Length(max=15),
        validators.DataRequired()
    ])

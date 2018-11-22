# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __
from flask_wtf import FlaskForm
import safe
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    validators,
    ValidationError,
    IntegerField,
    SelectField,
    DateTimeField)


def check_secure_password(form, field):
    strength = safe.check(field.data)
    messages = {
        'password is too short': __('La contraseña es muy corta, la longitud '
                                    'mínima es de 8 caracteres'),
        'password has a pattern': __('La contraseña es un patrón'),
        'password is too common': __('La contraseña es muy común'),
        'password is too simple': __('La contraseña es muy simple'),
        'password is good enough, but not strong':
            __('La contraseña es buena, pero no lo suficiente, utilice '
               'números, letras y símbolos'),
    }
    if not strength.valid:
        raise ValidationError(messages[strength.message])


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
                           message=__('Las contraseñas deben coincidir')),
        check_secure_password
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
        ),
        check_secure_password
    ])
    confirm = PasswordField(__('Confirmar contraseña'))


class FasciculoForm(FlaskForm):
    revista = StringField(__('Revista'), [
        validators.Length(max=150),
        validators.DataRequired()
    ])
    volumen = IntegerField(__('Volumen'), [
        validators.Length(max=15),
        validators.Optional(),
    ])
    numero = IntegerField(__('Numero'), [
        validators.Length(max=15),
        validators.Optional(),
    ])
    anio = IntegerField(__('Año'), [
        validators.Length(max=4),
        validators.DataRequired()
    ])
    mes_inicial = SelectField(__('Mes inicial'), choices=[
         ('0', __('Elige una opción')),
         ('1', __('Enero')),
         ('2', __('Febrero')),
         ('3', __('Marzo')),
         ('4', __('Abril')),
         ('5', __('Mayo')),
         ('6', __('Junio')),
         ('7', __('Julio')),
         ('8', __('Agosto')),
         ('9', __('Septiembre')),
         ('10', __('Octubre')),
         ('11', __('Noviembre')),
         ('12', __('Diciembre'))],
        validators = [validators.DataRequired()]
    )
    mes_final = SelectField(__('Mes final'), choices=[
        ('0', __('Elige una opción')),
         ('1', __('Enero')),
         ('2', __('Febrero')),
         ('3', __('Marzo')),
         ('4', __('Abril')),
         ('5', __('Mayo')),
         ('6', __('Junio')),
         ('7', __('Julio')),
         ('8', __('Agosto')),
         ('9', __('Septiembre')),
         ('10', __('Octubre')),
         ('11', __('Noviembre')),
         ('12', __('Diciembre'))],
        validators = [validators.DataRequired()]
    )
    parte = StringField(__('Parte'), [
        validators.Length(max=100),
        validators.DataRequired()
    ])

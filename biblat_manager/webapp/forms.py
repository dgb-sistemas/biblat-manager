# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __
from flask_wtf import FlaskForm
import safe
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SelectField,
    TextAreaField,
    validators,
    ValidationError)


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


class RevistaRegistrationForm(FlaskForm):
    bd = SelectField(__('Base de Datos'), [
        validators.DataRequired()
    ], choices=[('CLA', 'CLASE'),
                ('PER', 'PERIÓDICA')]
                     )

    titulo = StringField(__('Título de la revista (222a)*'), [
        validators.Length(min=1, max=256),
        validators.DataRequired()
    ])

    titulo_abreviado = StringField(__('Título abreviado de la revista (210a)*'), [
        validators.Length(min=1, max=256),
        validators.DataRequired()
    ])

    issn = StringField(__('ISSN (022a)*'), [
        validators.Length(min=9, max=9),
        validators.DataRequired()
    ])

    eissn = StringField(__('e-ISSN'), [
        validators.Length(min=9, max=9),
        validators.DataRequired()
    ])

    pais = SelectField(__('País de la revista (008)*'), [
        validators.DataRequired()
    ], choices=[('MX', 'México'),
                ('AR', 'Argentina'),
                ('BR', 'Brasil')]
                       )

    disciplina = SelectField(__('Disciplina de la revista (698a)*'), [
        validators.DataRequired()
    ], choices=[('1', 'Física y astronomía'),
                ('2', 'Matemáticas'),
                ('3', 'Literatura')]
                             )

    licencia = SelectField(__('Licencia CC'), [
        validators.DataRequired()
    ], choices=[('1', 'BY-NC/4.0'),
                ('2', 'L1'),
                ('3', 'L2')]
                           )

    politica = SelectField(__('Sherpa Romeo'), [
        validators.DataRequired()
    ], choices=[('1', 'Verde'),
                ('2', 'Azul'),
                ('3', 'Amarillo')]
                           )

    acerca = TextAreaField(__('Sobre la revista'), [
        validators.optional(), validators.length(max=200)
    ], default="Misión, visión, etc...")

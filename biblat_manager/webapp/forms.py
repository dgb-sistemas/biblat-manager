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
    SelectField,
    FileField)


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


class RevistaForm(FlaskForm):
    base_datos = SelectField(__('Base de datos'), choices=[
        ('N', ''),
        ('CLA01', 'CLASE'),
        ('PER01', 'PERIÓDICA')
    ])
    titulo = StringField(__('Titulo'), [
        validators.length(max=256),
        validators.DataRequired()
    ])
    titulo_abreviado = StringField(__('Titulo abreviado'), [
        validators.length(max=256),
        validators.Optional(),
    ])
    issn = StringField(__('ISSN'), [
        validators.length(max=9),
        validators.Regexp('^[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9xX]', message=__("Los datos no corresponden a un ISSN")),
        validators.DataRequired()
    ])
    issn_electronico = StringField(__('ISSN electrónico'), [
        validators.length(max=9),
        validators.Regexp('^[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9xX]', message=__("Los datos no corresponden a un ISSN")),
        validators.Optional(),
    ])
    pais = SelectField(__('Pais'), [validators.DataRequired()], choices=[
        ('N',''),
        ('MX','México'),
        ('ARG', 'Argentina'),
        ('CO', 'Colombia'),
        ('PE', 'Peru'),
        ('BR', 'Brasil')
    ])
    disciplina = SelectField(__('Disciplina'), [validators.DataRequired()], choices=[
        ('N', ''),
        ('1' , 'Administracion'),
        ('2', 'Agrociencias'),
        ('3', 'Antropologia'),
        ('4', 'Derecho'),
        ('5', 'Ingenieria'),
    ])
    """¿Como se va a hacer para jalar los referencedFields?"""
    licencia_cc = SelectField(__('Licencia CC (Creative Commons)'), [validators.Optional()], choices=[
        ('N', ''),
        ('CC0','Zero Public Domain, "No Rights Reserved"'),
        ('CC-BY', 'Attribution'),
        ('CC-BY-SA', 'Attribution-ShareAlike'),
        ('CC-BY-NC', 'Attribution-NonCommercial'),
        ('CC-BY-NC-ND', 'Attribution-NonCommercial-NoDerivs'),
        ('CC-BY-NC-SA', 'Attribution-NonCommercial-ShareAlike'),
        ('CC-BY-ND', 'Attribution-NoDerivs'),
        ('CC-BY-ND-NC', 'Attribution-NoDerivs-NonCommercial'),
    ])
    sherpa_romeo = SelectField(__('Sherpa Romeo'), [validators.Optional()], choices=[
        ('N', ''),
        ('V','Verde'),
        ('A', 'Azul'),
        ('Y', 'Amarillo'),
        ('B', 'Blanco'),
    ])
    idioma = SelectField(__('Idioma'), [validators.Optional()], choices=[
        ('N', ''),
        ('ESP','Español'),
        ('US', 'Ingles'),
        ('PG', 'Portugues'),
        ('FR','Frances')
    ])
    periodicidad = SelectField(__('Periodicidad'), [validators.DataRequired()], choices=[
        ('N', ''),
        ('M' ,'Mensual'),
        ('B', 'Bimestral'),
        ('T', 'Trimestral'),
    ])
    logo = FileField(__('Logo'), [
        validators.Regexp('\w+(\.jpg)$', message=__("El archivo no es una imagen")),
        validators.Optional(),
    ])
    portada = FileField(__('Portada'), [
        validators.Regexp('\w+(\.jpg)$', message=__("El archivo no es una imagen")),
        validators.Optional(),
    ])

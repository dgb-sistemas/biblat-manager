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
    FileField,
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


class DocumentoRegistrationForm(FlaskForm):
    titulo = StringField(__('Título del documento (245a)*'), [
        validators.Length(min=1, max=100),
        validators.DataRequired()
    ])

    doi = StringField(__('DOI (036a)'), [
        validators.Length(min=1, max=100),
        validators.optional()
    ])

    publicacion = StringField(__('Publicación (036a)*'), [
        validators.Length(min=1, max=100),
        validators.DataRequired()
    ])

    idioma = SelectField(__('Idioma*'), [
        validators.DataRequired()
    ], choices=[('1', 'Inglés'),
                ('2', 'Español')]
                              )

    paginacion = StringField(__('Paginación (300e)*'), [
        validators.Length(min=1, max=50),
        validators.DataRequired()
    ])

    nombre = StringField(__('Nombre (100a)'), [
        validators.Length(min=1, max=100),
        validators.optional()
    ])

    correo = StringField(__('Correo (1006)'), [
        validators.Length(min=1, max=100),
        validators.optional()
    ])

    orcid = StringField(__('ORCID'), [
        validators.Length(min=1, max=100),
        validators.optional()
    ])

    afiliacion = SelectField(__('Afiliación (100z)'), [
        validators.DataRequired()
    ], choices=[('1', '1. Univerdidad de la Habana'),
                ('2', '2. UNAM')]
                             )

    pais = SelectField(__('País (120x)'), [
        validators.DataRequired()
    ], choices=[('1', 'Cuba'),
                ('2', 'Argentina'),
                ('3', 'Brasil'),
                ('4', 'México')]
                             )

    ciudad = SelectField(__('Ciudad (120w)'), [
        validators.DataRequired()
    ], choices=[('1', 'La Habana'),
                ('2', 'Cienfuegos'),
                ('3', 'Trinidad')]
                       )

    institucion = SelectField(__('Institución (120u)'), [
        validators.DataRequired()
    ], choices=[('1', 'Universidad de la Habana'),
                ('2', 'Universidad de las Ciencias Informáticas'),
                ('3', 'Universidad de Matanzas')]
                         )

    dependencia = SelectField(__('Dependencia (120v)'), [
        validators.DataRequired()
    ], choices=[('1', 'Facultad de Física'),
                ('2', 'Facultad de Ingeniería'),
                ('3', 'Facultad de Medicina')]
                              )

    idioma_resumen = SelectField('', [
        validators.DataRequired()
    ], choices=[('1', 'Inglés'),
                ('2', 'Español')]
                         )

    resumen = TextAreaField('', [
        validators.optional(), validators.length(max=200)
    ], default="Texto del resumen")

    idioma_palabra = SelectField('', [
        validators.DataRequired()
    ], choices=[('1', 'Inglés'),
                ('2', 'Español')]
                                 )

    palabra = StringField('', [
        validators.optional(), validators.length(max=100)
    ])

    idioma_palabras = SelectField('', [
        validators.DataRequired()
    ], choices=[('1', 'Inglés'),
                ('2', 'Español')]
                                 )

    palabras = StringField('', [
        validators.optional(), validators.length(max=100)
    ])

    tipo_documento = SelectField(__('Tipo de documento (590)'), [
        validators.DataRequired()
    ], choices=[('1', 'Artículo'),
                ('2', 'Reseña del libro')]
                              )

    tipo_documentob = SelectField('&nbsp;', [
        validators.DataRequired()
    ], choices=[('1', 'Analítico, teórico'),
                ('2', 'Analítico, crítico'),
                ('3', 'Divulgación')]
                                  )

    disciplina = StringField(__('Disciplina (650a)*'), [
        validators.DataRequired(), validators.length(max=100)
    ])

    texto_completo_select = SelectField(__('Texto completo (856u)*'), [
        validators.DataRequired()
    ], choices=[('1', 'URL')]
                                        )

    texto_completo_text = StringField('', [
        validators.DataRequired(), validators.length(max=100)
    ])

    archivo_select = SelectField(__('Texto completo (856u)*'), [
        validators.DataRequired()
    ], choices=[('1', 'Archivo')]
                                 )

    archivo = FileField(__(''), [
        validators.DataRequired()
    ])

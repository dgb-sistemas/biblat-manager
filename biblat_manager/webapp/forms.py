# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __
from flask_wtf import FlaskForm
import safe
from wtforms import Form as NoCsrfForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    validators,
    ValidationError,
    FieldList,
    SelectField,
    IntegerField,
    FormField,
    TextAreaField,
)


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


# Documento
class AutorForm(NoCsrfForm):
    nombre = StringField(__('Nombre'), validators=[
        validators.DataRequired(),
        validators.Length(max=100)
    ])
    correo_electronico = StringField(__('Email'), [
        validators.Length(min=6, max=100),
        validators.Email(__('Correo electrónico inválido!'))
    ])
    referencia = IntegerField(__('Referencia'))


class AutorCorporativoForm(NoCsrfForm):
    institucion = StringField(__('Institución'), validators=[
        validators.DataRequired(),
        validators.Length(max=100)
    ])
    dependencia = StringField(__('Dependencia'), validators=[
        validators.Length(max=100)
    ])
    pais = SelectField('Pais', choices=[('MX', 'México'), ('CO', 'Colombia'), ('BR', 'Brasil'), ('AR', 'Argentina')])


class ResumenForm(NoCsrfForm):
    idioma = SelectField('Idioma', choices=[('spa', 'Español'), ('eng', 'Inglés'), ('por', 'Portugués'), ('deu', 'Alemán')])
    resumen = TextAreaField(__('Resumen'), validators=[
        validators.Length(max=900),
        validators.DataRequired()
    ])


class DisciplinaForm(NoCsrfForm):
    disciplina = SelectField(__('Disciplina'), validators=[
        validators.DataRequired()
    ],
        choices=[('',''), ('1', 'Administración y contaduría'), ('2', 'Agrociencias'), ('3', 'Bibliotecología y ciencia de la información'), ('4','Biología'), ('5','Economía')
    ])


class SubdisciplinaForm(NoCsrfForm):
    subdisciplinas = SelectField('Subdisciplina',
        choices=[('', ''), ('1', 'Administración de instituciones'), ('2', 'Administración de la producción'), ('3', 'Fertilización'), ('4','Fitotecnia'), ('5','Análisis y sistematización de la información')
    ])


class NombreGeograficoForm(NoCsrfForm):
    nombres_geograficos = SelectField('Nombres geográficos',
        choices=[('', ''), ('1', 'América'), ('2', 'Asia Central'), ('3', 'Corea del Norte'), ('4','Mesoamérica'), ('5','Vietnam')
    ])


class DocumentEditForm(FlaskForm):
    numero_sistema = StringField(__('Número de sistema'), [
        validators.Length(min=9, max=9),
        validators.DataRequired()
    ], render_kw={'disabled': True})
    titulo_documento = StringField(__('Título de documento'), [
        validators.Length(max=256),
        validators.DataRequired()
    ])
    doi = StringField(__('DOI'), [
        validators.Length(max=256)
    ])
    paginacion = StringField(__('Paginación'), [
        validators.Length(max=100),
        validators.DataRequired()
    ])
    referencias = BooleanField(__('Referencias'))
    idioma = FieldList(SelectField(__('Idioma'), [
        validators.DataRequired()
        ], choices=[('es', 'Español'), ('en', 'Inglés')]),
        label=__('Agregar idiomas'), min_entries=1)
    autores = FieldList(FormField(AutorForm),
        label=__('Agregar autores'),
        min_entries=1)
    autor_corporativo = FieldList(FormField(AutorCorporativoForm),
        label=__('Agregar autores corporativos'),
        min_entries=1)
    resumen = FieldList(FormField(ResumenForm),
        label=__('Agregar resumen'),
        min_entries=1)
    tipo_documento = SelectField('Tipo de documento', validators=[
        validators.DataRequired()
    ], choices=[('', ''), ('1', 'Artículo'), ('2', 'Conferencia o discurso'), ('3', 'Entrevista')])
    enfoque_documento = SelectField('Enfoque', validators=[
        validators.DataRequired()
    ], choices=[('',''), ('1', 'Analítico'), ('2', 'Descriptivo'), ('3', 'Experimental')])
    disciplina = FieldList(FormField(DisciplinaForm),
        label=__('Agregar disciplina'),
        min_entries=1)
    subdisciplinas = FieldList(FormField(SubdisciplinaForm),
        label=__('Agregar subdisciplina'),
        min_entries=1)
    nombres_geograficos = FieldList(FormField(NombreGeograficoForm),
        label=__('Agregar nombre geográfico'),
        min_entries=1)
    texto_completo = StringField(__('Texto Completo'), [
        validators.Length(max=256),
        validators.URL(message='URL inválido'),
        validators.optional()
    ])


class DocumentRegistrationForm(DocumentEditForm):
    numero_sistema = None

# -*- coding: utf-8 -*-
import flask_admin
import flask_login as login
from flask_admin.contrib.mongoengine import ModelView, ajax
from flask_admin.helpers import get_form_data
from wtforms import validators, widgets, fields, ValidationError
import flask_security.utils as security_utils
from flask_babelex import gettext as _, lazy_gettext as __

from flask import url_for, current_app, redirect, request, json, flash
from flask_security import url_for_security
import flask_security.utils as security_utils
from .. import dbmongo as db
from flask_admin.form.fields import Select2Field, Select2TagsField
from ..main import choices
from .widgets import CKEditorField
from .upload import DropImageUploadField, MultipleImageUploadFieldPortada, ImageUploadFieldAppLogo
from ..models import (
    Pais,
    Disciplina,
    Idioma,
    SherpaRomeo,
    LicenciaCC
    )
from .fields import (
    GroupSelect2Widget
)

class AdminIndexView(flask_admin.AdminIndexView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for_security('login', next=request.url))


class BaseModelView(ModelView):
    def is_accessible(self):
        return login.current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for_security('login', next=request.url))

# User
class BaseUserModelView(BaseModelView):
    create_modal = False
    column_labels = dict(
        username=__('Nombre'),
        email=__('Correo electrónico'),
        email_confirmed=__('Correo verificado?')
    )
    column_exclude_list = ('_password', 'email_confirmed')
    form_excluded_columns = ('_password', 'email_confirmed')

    def scaffold_form(self):
        form_class = super(BaseUserModelView, self).scaffold_form()
        form_class.password2 = fields.PasswordField(__('Contraseña'))
        return form_class

    def on_model_change(self, form, model, is_created):
        if len(model.password2):
            model.password = security_utils.hash_password(model.password2)

    def after_model_change(self, form, model, is_created):
        if is_created:
            model.active = True
            model.send_confirmation_email()


class UserModelView(BaseUserModelView):
    column_exclude_list = (
        '_password', 'email_confirmed', 'confirmed_at'
    )
    form_excluded_columns = (
        '_password', 'email_confirmed',
    )
    column_labels = dict(
        active='Activo',
        roles='Permiso',
        username=__('Nombre'))

    form_columns = (
         'username',
         'email',
         'roles'
     )


#Revista
class RevistaModelView(BaseModelView):
    can_view_details = True

    def checkPais(form, field):
        if not field.data:
            flash(_('Seleccione un país'), 'error')
            raise ValidationError(None)

    def checkDisciplina(form, field):
        if not field.data:
            flash(_('Seleccione una disciplina'), 'error')
            raise ValidationError(None)

    column_details_exclude_list = {
        '_id'
    }

    column_labels = {
        'base_datos': __('Base de datos'),
        'titulo': __('Título'),
        'titulo_abreviado': __('Título abreviado'),
        'issn': __('ISSN'),
        'issn_electronico': __('ISSN Electrónico'),
        'pais.nombre.es': __('País'),
        'disciplina.nombre.es': __('Disciplina'),
        'licencia_cc.tipo': __('Licencia'),
        'sherpa_romeo.color.es': __('Sherpa romeo'),
        'idioma.nombre.es': __('Idioma'),
        'periodicidad': __('Periodicidad')
    }

    column_list = (
        'base_datos',
        'titulo',
        'titulo_abreviado',
        'issn',
        'issn_electronico',
        'pais.nombre.es',
        'disciplina.nombre.es',
        'licencia_cc.tipo',
        'sherpa_romeo.color.es',
        'idioma.nombre.es',
        'periodicidad'
    )

    form_overrides = dict(
        base_datos=Select2Field,
        periodicidad=Select2Field,
        pais=Select2Field,
        disciplina=Select2Field,
        licencia_cc=Select2Field,
        sherpa_romeo=Select2Field,
        idioma=Select2Field,
        acerca=CKEditorField,
        portada=MultipleImageUploadFieldPortada,
        logo=ImageUploadFieldAppLogo
    )

    form_args = dict(
        base_datos=dict(
            choices=[
                ('CLA01', 'CLA01'),
                ('PER01', 'PER01')
            ]
        ),
        periodicidad=dict(
            choices=choices.FREQUENCY
        ),
        pais=dict(
            allow_blank=True,
            blank_text=__('Seleccione un país...'),
            choices=Pais.get_all(),
            validators=[validators.InputRequired(), checkPais]
        ),
        disciplina=dict(
            allow_blank=True,
            blank_text=__('Seleccione una disciplina...'),
            choices=Disciplina.get_all(),
            validators=[validators.InputRequired(), checkDisciplina]
        ),
        licencia_cc=dict(
            allow_blank=True,
            blank_text=__('Seleccione una licencia...'),
            choices=LicenciaCC.get_all()
        ),
        sherpa_romeo=dict(
            allow_blank=True,
            blank_text=__('Seleccione uno...'),
            choices=SherpaRomeo.get_all()
        ),
        idioma=dict(
            allow_blank=True,
            blank_text=__('Seleccione un idioma...'),
            choices=Idioma.get_all()
        )
    )


# Disciplina
class DisciplinaModelView(BaseModelView):
    @flask_admin.expose('/ajax_options')
    @flask_admin.expose('/ajax_options/<base>')
    def ajax_options(self, base='CLA01', selected=None):
        data = {
            'results': [{'id': '_None', 'text': str(__('Seleccione una disciplina'))}] + [
                {'id': d._id, 'text': d.nombre} for d in Disciplina.get_by_base(base)]
        }
        response = current_app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response

# -*- coding: utf-8 -*-
import flask_admin
import flask_login as login
from flask_admin.contrib.mongoengine import ModelView, ajax
from flask_admin.helpers import get_form_data
from wtforms import validators, widgets, fields, ValidationError
import flask_security.utils as security_utils
from flask_babelex import gettext as _, lazy_gettext as __
from flask_admin.contrib.mongoengine import filters
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
    LicenciaCC,
    Revista,
    Fasciculo,
    Documento,
    TipoDocumento,
    EnfoqueDocumento
    )
from ..main.choices import MES
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
    list_template = 'admin/model/list_revista.html'
    details_template = 'admin/model/details_revista.html'
    edit_template = 'admin/model/edit_revista.html'
    create_template = 'admin/model/create_revista.html'

    def checkPais(form, field):
        if not field.data:
            flash(__('Seleccione un país'), 'error')
            raise ValidationError(None)

    def checkDisciplina(form, field):
        if not field.data:
            flash(__('Seleccione una disciplina'), 'error')
            raise ValidationError(None)


    column_labels = {
        'base_datos': __('Base de datos'),
        'titulo': __('Título'),
        'titulo_abreviado': __('Título abreviado'),
        'issn': __('ISSN'),
        'issn_electronico': __('ISSN Electrónico'),
        'pais.nombre.es': __('País'),
        'disciplina.nombre.es': __('Disciplina'),
        'licencia_cc.tipo': __('Licencia CC'),
        'sherpa_romeo.color.es': __('Sherpa romeo'),
        'idioma.nombre.es': __('Idioma'),
        'logo': __('Logo'),
        'portada': __('Portada'),
        'periodicidad': __('Periodicidad'),
        'acerca': __('Acerca'),
        'fecha_creacion': __('Fecha de creación'),
        'fecha_actualizacion': __('Fecha de actualización')
    }

    column_list = (
        'base_datos',
        'titulo',
        'issn',
        'issn_electronico',
        'pais.nombre.es'
    )

    column_details_list = (
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
        'logo',
        'portada',
        'periodicidad',
        'acerca',
        'fecha_creacion',
        'fecha_actualizacion'
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
            label=__('Base de datos'),
            choices=[
                ('CLA01', 'CLA01'),
                ('PER01', 'PER01')
            ]
        ),
        periodicidad=dict(
            choices=choices.FREQUENCY
        ),
        pais=dict(
            label=__('País'),
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
            label=__('Licencia CC'),
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
        ),
        titulo=dict(
            label=__('Título')
        ),
        titulo_abreviado=dict(
            label=__('Título abreviado')
        ),
        issn=dict(
            label=__('ISSN')
        ),
        issn_electronico=dict(
            label=__('ISSN electrónico')
        ),
        fecha_creacion=dict(
            label=__('Fecha de creación')
        ),
        fecha_actualizacion=dict(
            label=__('Fecha de actualización')
        )
    )


def checkRevista(form, field):
    if not field.data:
        flash(__('Seleccione una revista'), 'error')
        raise ValidationError(None)


#Fasciculo
class FasciculoModelView(BaseModelView):
    can_view_details = True
    list_template='admin/model/list_fasciculo.html'
    details_template = 'admin/model/details_fasciculo.html'
    edit_template = 'admin/model/edit_fasciculo.html'
    create_template = 'admin/model/create_fasciculo.html'

    column_default_sort = [
                                ('anio', True),
                                ('numero', False),
                                ('volumen', False),
                                ('parte', False)
                            ]

    column_exclude_list = {
        '_id',
        'revista'
    }

    column_details_exclude_list = {
        '_id',
        'revista'
    }

    column_labels = {
        'revista': __('Revista'),
        'volumen': __('Volúmen'),
        'numero': __('Número'),
        'anio': __('Año'),
        'mes_inicial': __('Mes inicial'),
        'mes_final': __('Mes final'),
        'parte': __('Parte'),
        'fecha_creacion': __('Fecha de creación'),
        'fecha_actualizacion': __('Fecha de actualización')
    }

    column_list = (
        'volumen',
        'numero',
        'anio',
        'mes_inicial',
        'mes_final',
        'parte'
    )

    form_overrides = dict(
        revista=Select2Field,
        mes_inicial=Select2Field,
        mes_final=Select2Field
    )

    form_args = dict(
        revista=dict(
            allow_blank=True,
            blank_text=__('Seleccione una revista...'),
            choices=Revista.get_all(),
            validators=[checkRevista]
        ),
        volumen=dict(
            label=__('Volúmen')
        ),
        numero=dict(
            label=__('Número')
        ),
        anio=dict(
            label=__('Año')
        ),
        mes_inicial=dict(
            choices=choices.MES
        ),
        mes_final=dict(
            choices=choices.MES
        ),
        fecha_creacion=dict(
            label=__('Fecha de creación')
        ),
        fecha_actualizacion=dict(
            label=__('Fecha de actualización')
        )
    )

    column_filters = (filters.FilterLike(column=Fasciculo.revista, name='Revista'),)

    def create_form(self, obj=None):
        form = super(BaseModelView, self).create_form(obj=obj)
        if form.revista:
            form.revista.choices = Revista.get_all()
        if request.args.get('id_rev'):
            form.revista.data = request.args.get('id_rev')
        return form

    def edit_form(self, obj=None):
        form = super(BaseModelView, self).create_form(obj=obj)
        if form.revista:
            form.revista.choices = Revista.get_all()
        return form

    @flask_admin.expose('/ajax_options')
    @flask_admin.expose('/ajax_options/<revista>')
    def ajax_options(self, revista, selected=None):
        data = {
            'results': [{'id': '_None', 'text': str(__('Seleccione un fascículo...'))}] + [
                #{'id': d._id, 'text': str(d.anio) + (' vol.'+str(d.volumen) if d.volumen else '') + (' num.'+str(d.numero) if d.numero else '')} for d in Fasciculo.get_by_revista(revista)]
                {'id': i, 'text': val} for i, val in Fasciculo.get_by_revista(revista)]
        }
        response = current_app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response


#Documento
class DocumentoModelView(BaseModelView):
    can_view_details = True

    list_template = 'admin/model/list_documento.html'
    details_template = 'admin/model/details_documento.html'
    create_template = 'admin/model/create_documento.html'
    edit_template = 'admin/model/edit_documento.html'

    form_excluded_columns = ('marc21')

    column_details_exclude_list = (
        '_id',
        'revista',
        'fasciculo'
    )

    column_labels = {
        'numero_sistema': __('Número de sistema'),
        'titulo_documento': __('Título del documento'),
        'doi': __('DOI'),
        'idioma': __('Idioma'),
        'paginacion': __('Paginación'),
        'autor': __('Autor'),
        'autor_corporativo': __('Autor corporativo'),
        'institucion': __('Institución'),
        'resumen': __('Resumen'),
        'palabra_clave': __('Palabra clave'),
        'tipo_documento.nombre.es': __('Tipo de documento'),
        'enfoque_documento.nombre.es': __('Enfoque del documento'),
        'disciplina': __('Disciplinas'),
        'subdisciplinas': __('Subisciplinas'),
        'nombres_geograficos': __('Nombres geográficos'),
        'referencias': __('Referencias'),
        'texto_completo': __('Texto completo'),
        'fecha_creacion': __('Fecha de creación'),
        'fecha_actualizacion': __('Fecha de actualización'),
        'fecha_recepcion': __('Fecha de recepción'),
        'fecha_aceptacion': __('Fecha de aceptación')
    }

    column_list = {
        'numero_sistema',
        'titulo_documento',
    }

    column_details_list = {
        'numero_sistema',
        'titulo_documento',
        'doi',
        'idioma',
        'paginacion',
        'autor',
        'autor_corporativo',
        'institucion',
        'resumen',
        'palabra_clave',
        'tipo_documento.nombre.es',
        'enfoque_documento.nombre.es',
        'disciplina',
        'subdisciplinas',
        'nombres_geograficos',
        'referencias',
        'texto_completo',
        'fecha_creacion',
        'fecha_actualizacion',
        'fecha_recepcion',
        'fecha_aceptacion'
    }

    form_overrides = dict(
        revista=Select2Field,
        fasciculo=Select2Field,
        #idioma=ListField,
        referencias=fields.BooleanField,
        tipo_documento=Select2Field,
        enfoque_documento=Select2Field,
        #disciplina=Select2Field
    )

    form_subdocuments = {
        'autor': {
            'form_subdocuments': {
                None: {
                    'form_args': {
                        'nombre': {
                            'label': __('Nombre')
                        },
                        'correo_electronico': {
                            'label': __('Correo electrónico')
                        },
                        'referencia': {
                            'label': __('Referencia')
                        }
                    }
                }
            }
        },
        'autor_corporativo': {
            'form_subdocuments': {
                None: {
                    'form_overrides': {
                        'pais': Select2Field
                    },
                    'form_args': {
                        'institucion': {
                            'label': __('Institución')
                        },
                        'dependencia': {
                            'label': __('Dependencia')
                        },
                        'pais': {
                            'label': __('País'),
                            'allow_blank': True,
                            'blank_text': __('Seleccione un país...'),
                            'choices': Pais.get_all(),
                            #validators=[validators.InputRequired(), checkPais]
                        }
                    }
                }
            }
        },
        'institucion': {
            'form_subdocuments': {
                None: {
                    'form_overrides': {
                        'pais': Select2Field
                    },
                    'form_args': {
                        'dependencia': {
                            'label': __('Dependencia')
                        },
                        'ciudad_estado': {
                            'label': __('Ciudad o Estado')
                        },
                        'pais': {
                            'label': __('País')
                        },
                        'referencia': {
                            'label': __('Referencia')
                        },
                        'pais': {
                            'label': __('País'),
                            'allow_blank': True,
                            'blank_text': __('Seleccione un país...'),
                            'choices': Pais.get_all(),
                            # validators=[validators.InputRequired(), checkPais]
                        }
                    }
                }
            }
        },
        'resumen': {
            'form_subdocuments': {
                None: {
                    'form_overrides': {
                        'idioma': Select2Field
                    },
                    'form_args': {
                        'resumen': {
                            'label': __('Resumen')
                        },
                        'idioma': {
                            'label': __('Idioma'),
                            'allow_blank': True,
                            'blank_text': __('Seleccione un idioma...'),
                            'choices': Idioma.get_all(),
                            # validators=[validators.InputRequired(), checkPais]
                        }
                    }
                }
            }
        },
        'palabra_clave': {
            'form_subdocuments': {
                None: {
                    'form_overrides': {
                        'idioma': Select2Field
                    },
                    'form_args': {
                        'palabra_clave': {
                            'label': __('Palabra clave')
                        },
                        'idioma': {
                            'label': __('Idioma'),
                            'allow_blank': True,
                            'blank_text': __('Seleccione un idioma...'),
                            'choices': Idioma.get_all(),
                            # validators=[validators.InputRequired(), checkPais]
                        }
                    }
                }
            }
        }
    }

    form_args = dict(
        idioma=dict(
            label=__('Idioma'),
            allow_blank=True,
            blank_text=__('Seleccione uno o varios idiomas...'),
            label_attr='nombre'
        ),#option_widget=[]),  queryset, choices=Idioma.get_all()
        revista=dict(
            label=__('Revista'),
            allow_blank=True,
            blank_text=__('Seleccione una revista...'),
            choices=Revista.get_all(),
            validators=[checkRevista]
        ),
        fasciculo=dict(
            label=__('Fascículo'),
            allow_blank=True,
            blank_text=__('Seleccione un fascículo...'),
            choices=[]#Fasciculo.get_all(),
        ),
        pais=dict(
            label=__('País'),
            allow_blank=True,
            blank_text=__('Seleccione un país...'),
            choices=Pais.get_all(),
            #validators=[validators.InputRequired(), checkPais]
        ),
        tipo_documento=dict(
            label=__('Tipo de documento'),
            allow_blank=True,
            blank_text=__('Seleccione un tipo de documento...'),
            choices=TipoDocumento.get_all(),
            # validators=[validators.InputRequired(), checkPais]
        ),
        enfoque_documento=dict(
            label=__('Enfoque del documento'),
            allow_blank=True,
            blank_text=__('Seleccione un tipo de enfoque...'),
            choices=EnfoqueDocumento.get_all(),
            # validators=[validators.InputRequired(), checkPais]
        ),
        disciplina=dict(
            label=__('Disciplina'),
            allow_blank=True,
            blank_text=__('Seleccione una o varias disciplinas...'),
            label_attr='nombre',
            validators=[validators.InputRequired()]
        ),
        subdisciplina=dict(
            label=__('Subdisciplina'),
            allow_blank=True,
            blank_text=__('Seleccione una o varias subdisciplinas...'),
            label_attr='nombre',
            #validators=[validators.InputRequired()]
        ),
        nombres_geograficos=dict(
            label=__('Nombres geográficos'),
            allow_blank=True,
            blank_text=__('Seleccione uno o varios nombres...'),
            label_attr='nombre',
            # validators=[validators.InputRequired()]
        ),
        numero_sistema=dict(
            label=__('Número de sistema'),
        ),
        titulo_documento=dict(
            label=__('Título del documento'),
        ),
        doi=dict(
            label=__('DOI'),
        ),
        paginacion=dict(
            label=__('Paginación'),
        ),
        autor=dict(
            label=__('Autor'),
        ),
        autor_corporativo=dict(
            label=__('Autor corporativo'),
        ),
        institucion=dict(
            label=__('Institución'),
        ),
        resumen=dict(
            label=__('Resumen'),
        ),
        palabra_clave=dict(
            label=__('Palabra clave'),
        ),
        texto_completo=dict(
            label=__('Texto completo'),
        ),
        fecha_creacion=dict(
            label=__('Fecha de creación'),
        ),
        fecha_actualizacion=dict(
            label=__('Fecha de actualización'),
        ),
        fecha_recepcion=dict(
            label=__('Fecha de recepción')
        ),
        fecha_aceptacion=dict(
            label=__('Fecha de aceptación'),
        )
    )

    column_filters = (filters.FilterLike(column=Documento.fasciculo, name='Fasciculo'),)

    def create_form(self, obj=None):
        form = super(BaseModelView, self).create_form(obj=obj)
        if form.revista:
            form.revista.choices = Revista.get_all()
        if form.fasciculo:
            if request.args.get('id_rev'):
                form.fasciculo.choices = Fasciculo.get_by_revista(request.args.get('id_rev'))
            else:
                form.fasciculo.choices = Fasciculo.get_all()
        if form.disciplina:
            if request.args.get('id_rev'):
                form.disciplina.queryset = Disciplina.get_by_rev(request.args.get('id_rev'))
            else:
                form.disciplina.queryset = Disciplina.get_all_qs()
        if request.args.get('id_fasc'):
            form.fasciculo.data = request.args.get('id_fasc')
        if request.args.get('id_rev'):
            form.revista.data = request.args.get('id_rev')

        return form

    def edit_form(self, obj=None):
        form = super(BaseModelView, self).create_form(obj=obj)
        if form.fasciculo:
            form.fasciculo.choices = Fasciculo.get_by_revista(request.args.get('id_rev'))
        if form.revista:
            form.revista.choices = Revista.get_all()
        if form.disciplina:
            form.disciplina.queryset = Disciplina.get_by_rev(request.args.get('id_rev'))

        return form

# Disciplina
class DisciplinaModelView(BaseModelView):
    @flask_admin.expose('/ajax_options')
    @flask_admin.expose('/ajax_options/<base>')
    def ajax_options_base(self, base='CLA01', selected=None):
        print('ajax')
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

    @flask_admin.expose('/ajax_options/rev/<id_rev>')
    def ajax_options_rev(self, id_rev):
        data = {
            'results': [{'id': '_None', 'text': str(__('Seleccione una disciplina'))}] + [
                {'id': d._id, 'text': d.nombre} for d in Disciplina.get_by_rev(id_rev)]
        }
        response = current_app.response_class(
            response=json.dumps(data),
            status=200,
            mimetype='application/json'
        )
        return response

# -*- coding: utf-8 -*-
import flask_admin
import flask_login as login
from flask_admin.contrib.mongoengine import ModelView
from wtforms import validators, widgets, fields
import flask_security.utils as security_utils
from flask_babelex import gettext as _, lazy_gettext as __

from flask import url_for, current_app, redirect, request
from flask_security import url_for_security
import flask_security.utils as security_utils


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

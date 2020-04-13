# -*- coding: utf-8 -*-
from flask_security import UserMixin, RoleMixin
from mongoengine import queryset_manager
import flask_security.utils as security_utils
from flask_security import confirmable, recoverable
from . import dbmongo as db, login_manager, notifications, utils, admin
from flask_admin.contrib.mongoengine import ModelView


class Role(db.Document, RoleMixin):
    name = db.StringField(max_length=80, unique=True)
    description = db.StringField(max_length=255)

    meta = {'collection': 'roles'}

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class User(db.Document, UserMixin):
    username = db.StringField(max_length=100, unique=True)
    email = db.StringField(max_length=100, required=True)
    _password = db.StringField(required=True, db_field='password')
    email_confirmed = db.BooleanField(default=False)
    confirmed_at = db.DateTimeField()
    active = db.BooleanField(default=True)
    roles = db.ListField(db.ReferenceField(Role), default=[])

    meta = {'collection': 'users'}

    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            kwargs['_password'] = kwargs.pop('password')
            db.Document.__init__(self, *args, **kwargs)
            self.password = kwargs['_password']
        else:
            db.Document.__init__(self, *args, **kwargs)


    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, plaintext):
        self._password = plaintext

    def check_password_hash(self, plaintext):
        """
        Compara el string ``plaintext`` con el hash de la contraseña almacenada
        """
        if not self._password:
            return False
        else:
            return security_utils.verify_password(plaintext, self._password)

    def send_confirmation_email(self):
        confirmable.send_confirmation_instructions(self)

    def send_reset_password_email(self):
        recoverable.send_reset_password_instructions(self)

    def _check_valid_email(self):
        """
        retorna True cuando la instancia (self) del usuario, tiene um email válido.
        retorna False en otro caso.
        """
        return utils.check_valid_email(self.email)

    @queryset_manager
    def get_by_email(doc_cls, queryset, user_email):
        """
        Regresa un usuario cuando el atributo email sea igual al parámetro email,
        en caso de que email no sea un string regresa un ValueError.
        """
        if not isinstance(user_email, str):
            raise ValueError('El parámetro email debe ser un string')
        return queryset.filter(email=user_email).first()

    def __unicode__(self):
        return self.email

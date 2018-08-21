# -*- coding: utf-8 -*-
from flask_login import UserMixin
from mongoengine import queryset_manager
from werkzeug.security import generate_password_hash, check_password_hash
from . import dbmongo as db, login_manager
from . import notifications, utils


class User(UserMixin, db.Document):
    _id = db.StringField(max_length=32, primary_key=True,
                         default=utils.generate_uuid_32_string())
    username = db.StringField(max_length=100, unique=True)
    email = db.StringField(max_length=100, required=True)
    _password = db.StringField(required=True, db_field='password')
    email_confirmed = db.BooleanField(default=False)

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
        self._password = generate_password_hash(plaintext, method='sha256')

    def check_password_hash(self, plaintext):
        """
        Compara el string ``plaintext`` con el hash de la contraseña almacenada
        """
        if not self._password:
            return False
        else:
            return check_password_hash(self._password, plaintext)

    def send_confirmation_email(self):
        if not self._check_valid_email():
            raise ValueError(
                'El usuario debe tener un correo electrónico válido')
        else:
            return notifications.send_confirmation_email(self.email)

    def send_reset_password_email(self):
        if not self._check_valid_email():
            raise ValueError('El usuario debe tener un correo electrónico '
                             'válido para realizar el envío')
        else:
            return notifications.send_reset_password_email(self.email)

    def _check_valid_email(self):
        """
        retorna True cuando la instancia (self) del usuario, tiene um email válido.
        retorna False en otro caso.
        """
        return utils.check_valid_email(self.email)

    @queryset_manager
    def get_by_id(doc_cls, queryset, user_id):
        return queryset.filter(_id=user_id).first()

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


@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

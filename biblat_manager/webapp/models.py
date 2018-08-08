# -*- coding: utf-8 -*-
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import dbmongo as db
from . import notifications, utils


class User(UserMixin, db.Document):
    _id = db.StringField(max_length=32, primary_key=True,
                         default=utils.generate_uuid_32_string())
    username = db.StringField(max_length=100)
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

    def _check_valid_email(self):
        """
        retorna True cuando la instancia (self) del usuario, tiene um email válido.
        retorna False en otro caso.
        """
        from .forms import EmailForm
        if not self.email or self.email == '' or self.email == '':
            return False
        else:
            form = EmailForm(data={'email': self.email})
            return form.validate()

    def __unicode__(self):
        return self.email

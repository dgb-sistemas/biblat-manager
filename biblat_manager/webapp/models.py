# -*- coding: utf-8 -*-
from flask_security import UserMixin, RoleMixin
from mongoengine import queryset_manager
import flask_security.utils as security_utils
from flask_security import confirmable, recoverable
from . import dbmongo as db, login_manager, notifications, utils, admin
from flask_admin.contrib.mongoengine import ModelView
from biblat_manager.config import settings
import json

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


class I18NField(db.EmbeddedDocument):
    es = db.StringField()
    en = db.StringField()

    def __unicode__(self):
        #if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
        return self.es
        #else:
        #    return self.en


class Pais(db.Document):
    """Esquema de catálogo país
    _id: Código ISO 3166-2
    alpha2: código de país en dos letras designado para representar la
    mayoría de los lenguajes en el mundo
    alpha: código de país en tres caracteres
    codigo_pais: Código numérico de país
    iso_3166-2: Descripción del ISO 3166-2
    """
    _id = db.StringField(max_length=2, primary_key=True, required=True)
    nombre = db.EmbeddedDocumentField(I18NField)
    alpha2 = db.StringField(max_length=2, required=True)
    alpha3 = db.StringField(max_length=3, required=True)
    codigo_pais = db.StringField(max_length=3, required=True)
    iso_3166_2 = db.StringField(max_length=14)
    region = db.EmbeddedDocumentField(I18NField)
    sub_region = db.EmbeddedDocumentField(I18NField)
    region_intermedia = db.EmbeddedDocumentField(I18NField)
    codigo_region = db.StringField(max_length=3)
    codigo_sub_region = db.StringField(max_length=3)
    codigo_region_intermedia = db.StringField(max_length=3)

    meta = {
        'collection': 'paises',
        'indexes': [
            'nombre.es',
            'alpha2'
        ]
    }

    @classmethod
    def get_all(cls):
        output = []
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in cls.objects:
                output.append((p._id, p.nombre.es))
        else:
            for p in cls.objects:
                output.append((p._id, p.nombre.en))
        return output


    def save(self, *args, **kwargs):
        """Override save in Pais"""
        if not self._id:
            self._id = self.alpha2

        return super(Pais, self).save(*args, **kwargs)

    def __str__(self):
        return self._id

    def __unicode__(self):
        return self._id



class Disciplina(db.Document):
    """Esquema de catálogo disciplina"""
    _id = db.StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    base = db.ListField(db.StringField(max_length=10, required=True))
    nombre = db.EmbeddedDocumentField(I18NField)

    meta = {
        'collection': 'disciplinas_revista',
        'indexes': [
            'nombre.es',
            'base'
        ]
    }

    def __str__(self):
        return self._id

    def __unicode__(self):
        return self._id

    @classmethod
    def get_all(cls):
        print('Get all disc')
        output = []
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in cls.objects:
                output.append((p._id, p.nombre.es))
        else:
            for p in cls.objects:
                output.append((p._id, p.nombre.en))
        print(output)
        print(Disciplina.objects)
        return output

    @classmethod
    def get_by_base(cls, base):
        output = []
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in cls.objects(base=base).all():
                p.nombre = p.nombre.es
                output.append(p)
        else:
            for p in cls.objects(base=base):
                output.append((p._id, p.base, p.nombre.en))
        return output


class LicenciaCC(db.Document):
    """Esquema de catálogo licencia
    tipo: tipo de licencia creative commons
    url: url del legal code de la licencia
    """
    _id = db.StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    tipo = db.StringField(max_length=16, required=True)
    url = db.URLField(required=True)

    meta = {
        'collection': 'licencias_cc',
        'indexes': [
            'tipo'
        ]
    }

    def __str__(self):
        return self._id

    def __unicode__(self):
        return self._id

    @classmethod
    def get_all(cls):
        output = []
        for p in cls.objects:
            output.append((p._id, p.tipo))
        return output

class SherpaRomeo(db.Document):
    """Esquema de catálogo sherpa romeo
    politica: especificacion de la politica utilizada
    codigo: codigo hexagecimal utilizado por el color
    """
    _id = db.StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    color = db.EmbeddedDocumentField(I18NField)
    politica = db.EmbeddedDocumentField(I18NField)
    codigo = db.StringField(required=True)

    meta = {
        'collection': 'sherparomeo',
        'indexes': [
            'color.es'
        ]
    }

    def __str__(self):
        return self._id

    def __unicode__(self):
        return self._id

    @classmethod
    def get_all(cls):
        output = []
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in cls.objects:
                output.append((p._id, p.color.es))
        else:
            for p in cls.objects:
                output.append((p._id, p.color.en))
        return output


class Idioma(db.Document):
    """Esquema de catálogo idioma
    _id : Código ISO 639-3
    iso_639_1: Identificador 639-1 para identificar los idiomas principales
    iso_639_3: Identificador 639-3 para identificar todos los lenguajes humanos
               conocidos, incluyendo vivos, extintos, antiguos, históricos,
               artificiales o de señas
    iso_639_2b: Identificador 639-2 para aplicaciones bibliográficas
    iso_639_2t: Identificador 639-2 para aplicaciones de terminología
    type: Tipo de idioma A(ncient), C(onstructed),
          E(xtinct), H(istorical), L(iving), S(pecial)
    scope: Cobertura del idioma I(ndividual), M(acrolanguage), S(pecial)
    """
    _id = db.StringField(max_length=3, primary_key=True, required=True)
    iso_639_1 = db.StringField(min_length=2, max_length=2)
    iso_639_3 = db.StringField(min_length=3, max_length=3, required=True)
    iso_639_2b = db.StringField(min_length=2, max_length=3)
    iso_639_2t = db.StringField(min_length=2, max_length=3)
    type = db.StringField(max_length=1)
    scope = db.StringField(max_length=1)
    nombre = db.EmbeddedDocumentField(I18NField)

    meta = {
        'collection': 'idiomas',
        'indexes': [
            'nombre.es',
            'iso_639_1',
            'iso_639_3',
        ]
    }

    def __str__(self):
        return self._id

    def __unicode__(self):
        return self._id

    def save(self, *args, **kwargs):
        """Override save Idioma"""
        if not self._id:
            self._id = self.iso_639_3

        return super(Idioma, self).save(*args, **kwargs)

    @classmethod
    def get_all(cls):
        output = []
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in cls.objects:
                output.append((p._id, p.nombre.es))
        else:
            for p in cls.objects:
                output.append((p._id, p.nombre.en))
        return output

class Revista(db.Document):
    """Esquema de Revista
    base_datos: Nombre de la base de datos(CLA01 o PER01)
    titulo: Título de la revista
    titulo_abreviado:
    issn: identificador de revista
    issn_electronico: identificador de revista electrónica
    pais: Identificador del país
    disciplina: Identificador de la disciplina
    licencia_cc: Licencia Creative Commons
    sherpa_romeo: Definicion Politicas open access
    idioma: Lista de idiomas de la revista
    logo:
    portada:
    fecha_creacion: fecha en que fue creada la revista
    fecha_actualizacion: fecha en que se actualizaron los datos
    """
    _id = db.StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    base_datos = db.StringField(max_length=5, required=True)
    titulo = db.StringField(max_length=256, required=True)
    titulo_abreviado = db.StringField(max_length=256)
    issn = db.StringField(max_length=9, required=True)
    issn_electronico = db.StringField(max_length=9)
    pais = db.ReferenceField(Pais, required=True)
    disciplina = db.ReferenceField(Disciplina, required=True)
    licencia_cc = db.ReferenceField(LicenciaCC)
    sherpa_romeo = db.ReferenceField(SherpaRomeo)
    idioma = db.ReferenceField(Idioma)
    logo = db.StringField(max_length=100)
    portada = db.StringField()
    fecha_creacion = db.DateTimeField(required=True)
    fecha_actualizacion = db.DateTimeField(required=True)
    periodicidad = db.StringField(max_length=1, required=True)
    acerca = db.StringField(max_length=256, required=True)


    meta = {
        'collection': 'revistas',
        'indexes': [
            'base_datos',
            'titulo',
            'issn',
            'issn_electronico',
            'pais',
            'disciplina',
            'idioma'
        ]
    }

    def save(self, *args, **kwargs):
        """Override save in Revista"""
        self.pais = Pais.objects(_id=self.pais).first()
        self.disciplina = Disciplina.objects(_id=self.disciplina).first()
        self.idioma = Idioma.objects(_id=self.idioma).first()
        self.sherpa_romeo = SherpaRomeo.objects(_id=self.sherpa_romeo).first()
        self.licencia_cc = LicenciaCC.objects(_id=self.licencia_cc).first()
        if not self._id:
            self._id = self.alpha2

        return super(Revista, self).save(*args, **kwargs)

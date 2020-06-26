# -*- coding: utf-8 -*-
from flask_security import UserMixin, RoleMixin
from mongoengine import queryset_manager, CASCADE
import flask_security.utils as security_utils
from flask_security import confirmable, recoverable
from . import dbmongo as db, login_manager, notifications, utils, admin
from flask_admin.contrib.mongoengine import ModelView
from biblat_manager.config import settings
# -*- coding: utf-8 -*-
from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    ListField,
    IntField,
    EmbeddedDocument,
    BooleanField,
    EmbeddedDocumentField,
    EmbeddedDocumentListField,
    ReferenceField,
    URLField
)
from .catalogs import (
    Pais,
    Idioma,
    TipoDocumento,
    EnfoqueDocumento,
    #Disciplina,
    #SubDisciplina,
    NombreGeografico,
    LicenciaCC,
    SherpaRomeo,
    I18NField
)
from .marc import MarcDocumentField
import json


class Role(Document, RoleMixin):
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)

    meta = {'collection': 'roles'}

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class User(Document, UserMixin):
    username = StringField(max_length=100, unique=True)
    email = StringField(max_length=100, required=True)
    _password = StringField(required=True, db_field='password')
    email_confirmed = BooleanField(default=False)
    confirmed_at = DateTimeField()
    active = BooleanField(default=True)
    roles = ListField(ReferenceField(Role), default=[])

    meta = {'collection': 'users'}

    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            kwargs['_password'] = kwargs.pop('password')
            Document.__init__(self, *args, **kwargs)
            self.password = kwargs['_password']
        else:
            Document.__init__(self, *args, **kwargs)


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


class Disciplina(Document):
    """Esquema de catálogo disciplina"""
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    base = ListField(StringField(max_length=10, required=True))
    nombre = EmbeddedDocumentField(I18NField)

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
        output = []
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in cls.objects:
                output.append((p._id, p.nombre.es))
        else:
            for p in cls.objects:
                output.append((p._id, p.nombre.en))
        return output

    @classmethod
    def get_all_qs(cls):
        queryset = cls.objects
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in queryset:
                p.nombre = p.nombre.es
        else:
            for p in queryset:
                p.nombre = p.nombre.en
        return queryset

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

    @classmethod
    def get_by_rev(cls, id_rev):
        queryset = cls.objects(base=Revista.objects(_id=id_rev).first().base_datos).all()
        if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
            for p in queryset:
                p.nombre = p.nombre.es
        else:
            for p in queryset:
                p.nombre = p.nombre.en
        return queryset


class SubDisciplina(Document):
    """Esquema de catálogo subdisciplina"""
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    disciplina = ReferenceField(Disciplina, required=True)
    nombre = EmbeddedDocumentField(I18NField)

    meta = {
        'collection': 'subdisciplinas',
        'indexes': [
            'nombre.es',
            'disciplina'
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
                output.append((p._id, p.nombre.es))
        else:
            for p in cls.objects:
                output.append((p._id, p.nombre.en))
        return output


class Revista(Document):
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
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    base_datos = StringField(max_length=5, required=True)
    titulo = StringField(max_length=256, required=True)
    titulo_abreviado = StringField(max_length=256)
    issn = StringField(max_length=9, required=True)
    issn_electronico = StringField(max_length=9)
    pais = ReferenceField(Pais, required=True)
    disciplina = ReferenceField(Disciplina, required=True)
    licencia_cc = ReferenceField(LicenciaCC)
    sherpa_romeo = ReferenceField(SherpaRomeo)
    idioma = ReferenceField(Idioma)
    logo = StringField(max_length=100)
    portada = StringField()
    fecha_creacion = DateTimeField(required=True)
    fecha_actualizacion = DateTimeField(required=True)
    periodicidad = StringField(max_length=1, required=True)
    acerca = StringField(max_length=256, required=True)

    def __str__(self):
        return self._id

    def __unicode__(self):
        return self._id

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

    @classmethod
    def get_all(cls):
        output = []
        for p in cls.objects:
            output.append((p._id, p.titulo))

        return output

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


class Fasciculo(Document):
    """Esquema de fascículo
    revista:Objeto referenciado de tipo revista
    volumen: volúmen del fascículo
    numero: numero del fascículo
    año: año del fascículo
    mes_inicial:
    mes_final:
    parte: parte del fascículo
    fecha_creacion:
    fecha_actualizacion:
    """
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    revista = ReferenceField(Revista, required=True, reverse_delete_rule=CASCADE)
    volumen = IntField()
    numero = IntField()
    anio = IntField(required=True)
    mes_inicial = IntField(required=True)
    mes_final = IntField(required=True)
    parte = StringField(max_length=100)
    fecha_creacion = DateTimeField(required=True)
    fecha_actualizacion = DateTimeField(required=True)

    meta = {
        'collection': 'fasciculos',
        'indexes': [
            'revista',
            'anio',
            'volumen',
            'numero'
        ]
    }

    def __str__(self):
        return self._id

    def __unicode__(self):
        return self._id

    def save(self, *args, **kwargs):
        """Override save in Fascículo"""
        self.revista = Revista.objects(_id=self.revista).first()

        return super(Fasciculo, self).save(*args, **kwargs)

    @classmethod
    def get_by_revista(cls, revista):
        output = []
        for p in cls.objects(revista=revista).all():
            output.append((p._id, str(p.anio) + (' vol.'+str(p.volumen) if p.volumen else '') + (' num.'+str(p.numero) if p.numero else '')))
        return output

    @classmethod
    def get_all(cls):
        output = []
        for p in cls.objects:
            output.append((p._id, str(p.anio) + (' vol.'+str(p.volumen) if p.volumen else '') + (' num.'+str(p.numero) if p.numero else '')))
        return output


class Autor(EmbeddedDocument):
    """Esquema de autor
    nombre: Nombre del autor
    correo_electronico: correo de contacto del autor
    referencia: valor entero que referencia a la institución
    a la que pertenece el autor
    """
    nombre = StringField(max_length=100, required=True)
    correo_electronico = StringField(max_length=100)
    referencia = IntField()

    def __str__(self):
        return self.nombre + ', ' + self.correo_electronico + ' (' + str(self.referencia) + ')'

    def __unicode__(self):
        return self.nombre + ', ' + self.correo_electronico + ' (' + str(self.referencia) + ')'


class AutorCorporativo(EmbeddedDocument):
    """Esquema de autor corporativo
    institucion: nombre de la institución a la que pertenece el autor
    dependencia: nombre de la dependencia a la que pertenece el autor
    pais: nombre del país de la institución a la que pertenece el autor"""
    institucion = StringField(max_length=100, required=True)
    dependencia = StringField(max_length=100)
    pais = ReferenceField(Pais)

    def __str__(self):
        return self.institucion + ', ' + self.dependencia

    def __unicode__(self):
        return self.institucion + ', ' + self.dependencia


class Institucion(EmbeddedDocument):
    """Esquema de institución
    institucion: Nombre de la institución
    dependencia: Nombre de la dependencia
    ciudad_estado: Nombre de la ciudad o estado
    pais: Referencia al identificador del país
    referencia: Número entero para ser referenciado por el autor
    """
    institucion = StringField(max_length=256, required=True)
    dependencia = StringField(max_length=256)
    ciudad_estado = StringField(max_length=256)
    pais = ReferenceField(Pais, required=True)
    referencia = IntField()

    def __str__(self):
        return self.institucion + ', ' + self.dependencia + ' (' + str(self.referencia) + ')'

    def __unicode__(self):
        return self.institucion + ', ' + self.dependencia + ' (' + str(self.referencia) + ')'


class UrlTextoCompleto(EmbeddedDocument):
    """Esquema de Url de texto completo
    url: URL del recurso para texto completo
    descripcion: Descripción del formato en Texto completo
    Texto completo (Ver PDF) o Texto completo (Ver HTML)
    """
    url = URLField(required=True)
    descripcion = StringField(max_length=100, required=True)

    def __str__(self):
        return self.url + ' (' + self.descripcion + ')'

    def __unicode__(self):
        return self.url + ' (' + self.descripcion + ')'


class Resumen(EmbeddedDocument):
    """Esquema de resúmen
    idioma: Objeto referenciado de idioma
    resumen:
    """
    idioma = ReferenceField(Idioma, required=True)
    resumen = StringField(required=True)

    def __str__(self):
        return self.idioma.nombre.es + ': ' + self.resumen

    def __unicode__(self):
        return self.idioma.nombre.es + ': ' + self.resumen


class PalabraClave(EmbeddedDocument):
    """Esquema de palabra clave
    idioma: Objeto referenciado de idioma
    palabra_clave: definición de la palabra clave
    """
    idioma = ReferenceField(Idioma, required=True)
    palabra_clave = StringField(max_length=100, required=True)

    def __str__(self):
        return self.idioma.nombre.es + ': ' + self.palabra_clave

    def __unicode__(self):
        return self.idioma.nombre.es + ': ' + self.palabra_clave


class Documento(Document):
    """Esquema de documento
    doi: identificador de objeto digital
    """
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    revista = ReferenceField(Revista, required=True, reverse_delete_rule=CASCADE)
    fasciculo = ReferenceField(Fasciculo, required=True, reverse_delete_rule=CASCADE)
    numero_sistema = StringField(max_length=14, required=True)
    titulo_documento = StringField(max_length=256, required=True)
    doi = StringField(max_length=256)
    idioma = ListField(ReferenceField(Idioma))
    paginacion = StringField(max_length=100)
    autor = ListField(EmbeddedDocumentField(Autor))
    autor_corporativo = ListField(EmbeddedDocumentField(AutorCorporativo))
    institucion = ListField(EmbeddedDocumentField(Institucion))
    resumen = ListField(EmbeddedDocumentField(Resumen))
    palabra_clave = ListField(EmbeddedDocumentField(PalabraClave, required=True))
    tipo_documento = ReferenceField(TipoDocumento, required=True)
    enfoque_documento = ReferenceField(EnfoqueDocumento, required=True)
    disciplina = ListField(ReferenceField(Disciplina), required=False)
    subdisciplinas = ListField(ReferenceField(SubDisciplina))
    nombres_geograficos = ListField(ReferenceField(NombreGeografico))
    referencias = BooleanField()
    texto_completo = ListField(EmbeddedDocumentField(UrlTextoCompleto))
    #marc21 = EmbeddedDocumentField(MarcDocumentField, required=True)
    fecha_creacion = DateTimeField(required=True)
    fecha_actualizacion = DateTimeField(required=True)
    fecha_recepcion = DateTimeField()
    fecha_aceptacion = DateTimeField()

    meta = {
        'collection': 'documentos',
        'indexes': [
            'revista',
            'autor',
            'institucion',
            'palabra_clave',
            'fasciculo',
            'numero_sistema',
            'titulo_documento',
            'doi',
            'idioma'
        ]
    }

    def save(self, *args, **kwargs):
        self.revista = Revista.objects(_id=self.revista).first()
        self.fasciculo = Fasciculo.objects(_id=self.fasciculo).first()
        self.enfoque_documento = EnfoqueDocumento.objects(_id=self.enfoque_documento).first()
        self.tipo_documento = TipoDocumento.objects(_id=self.tipo_documento).first()
        for a in self.autor_corporativo:
            a.pais = Pais.objects(_id=a.pais).first()
        for i in self.institucion:
            i.pais = Pais.objects(_id=i.pais).first()
        for r in self.resumen:
            r.idioma = Idioma.objects(_id=r.idioma).first()
        for pc in self.palabra_clave:
            pc.idioma = Idioma.objects(_id=pc.idioma).first()
        if not self._id:
            self._id = self.alpha2

        return super(Documento, self).save(*args, **kwargs)

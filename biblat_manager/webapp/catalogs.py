# -*- coding: utf-8 -*-
from mongoengine import (
    Document,
    StringField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    ReferenceField,
    URLField,
    ListField,
    BooleanField
)
from . import utils
from biblat_manager.config import settings

class I18NField(EmbeddedDocument):
    es = StringField()
    en = StringField()

    def __unicode__(self):
        #if settings.Config.BABEL_DEFAULT_LOCALE == 'es_MX':
        return self.es
        #else:
        #    return self.en


class Pais(Document):
    """Esquema de catálogo país
    _id: Código ISO 3166-2
    alpha2: código de país en dos letras designado para representar la
    mayoría de los lenguajes en el mundo
    alpha: código de país en tres caracteres
    codigo_pais: Código numérico de país
    iso_3166-2: Descripción del ISO 3166-2
    """
    _id = StringField(max_length=2, primary_key=True, required=True)
    nombre = EmbeddedDocumentField(I18NField)
    alpha2 = StringField(max_length=2, required=True)
    alpha3 = StringField(max_length=3, required=True)
    codigo_pais = StringField(max_length=3, required=True)
    iso_3166_2 = StringField(max_length=14)
    region = EmbeddedDocumentField(I18NField)
    sub_region = EmbeddedDocumentField(I18NField)
    region_intermedia = EmbeddedDocumentField(I18NField)
    codigo_region = StringField(max_length=3)
    codigo_sub_region = StringField(max_length=3)
    codigo_region_intermedia = StringField(max_length=3)

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


class Idioma(Document):
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
    _id = StringField(max_length=3, primary_key=True, required=True)
    iso_639_1 = StringField(min_length=2, max_length=2)
    iso_639_3 = StringField(min_length=3, max_length=3, required=True)
    iso_639_2b = StringField(min_length=2, max_length=3)
    iso_639_2t = StringField(min_length=2, max_length=3)
    type = StringField(max_length=1)
    scope = StringField(max_length=1)
    nombre = EmbeddedDocumentField(I18NField)

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


class TipoDocumento(Document):
    """Esquema de catálogo tipo documento"""
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    nombre = EmbeddedDocumentField(I18NField)
    descripcion = EmbeddedDocumentField(I18NField)

    meta = {
        'collection': 'tipo_documento',
        'indexes': [
            'nombre.es'
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


class EnfoqueDocumento(Document):
    """Esquema de catálogo enfoque documento"""
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    nombre = EmbeddedDocumentField(I18NField)
    descripcion = EmbeddedDocumentField(I18NField)

    meta = {
        'collection': 'enfoque_documento',
        'indexes': [
            'nombre.es'
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
                output.append((p._id, p.nombre.en))
        return output


class NombreGeografico(Document):
    """Esquema de catálogo nombre geográfico"""
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    nombre = EmbeddedDocumentField(I18NField)
    nota = EmbeddedDocumentField(I18NField)

    meta = {
        'collection': 'nombres_geograficos',
        'indexes': [
            'nombre.es'
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


class LicenciaCC(Document):
    """Esquema de catálogo licencia
    tipo: tipo de licencia creative commons
    url: url del legal code de la licencia
    """
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    tipo = StringField(max_length=16, required=True)
    url = URLField(required=True)

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


class SherpaRomeo(Document):
    """Esquema de catálogo sherpa romeo
    politica: especificacion de la politica utilizada
    codigo: codigo hexagecimal utilizado por el color
    """
    _id = StringField(max_length=32, primary_key=True, required=True,
                      default=lambda: utils.generate_uuid_32_string())
    color = EmbeddedDocumentField(I18NField)
    politica = EmbeddedDocumentField(I18NField)
    codigo = StringField(required=True)

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
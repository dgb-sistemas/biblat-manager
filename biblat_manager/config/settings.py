# -*- coding: utf-8 -*-
import os

"""
    Archivo de configuración de Biblat Manager

    Variables de entorno:

        * BIBLAT_SECRET_KEY: Clave necesaria para la seguridad de las sesiones
"""


class Config:
    SECRET_KEY = os.environ.get('BIBLAT_SECRET_KEY', 'secr3t-k3y')
    # Idioma predeterminado:
    BABEL_DEFAULT_LOCALE = 'es_MX'
    # Idiomas soportados
    LANGUAGES = {
        'en_US': 'English',
        'es_MX': 'Español',
    }

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}

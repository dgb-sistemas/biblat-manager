# -*- coding: utf-8 -*-
import os

"""
    Archivo de configuración de Biblat Manager

    Variables de entorno:

        - BIBLAT_SECRET_KEY: Clave necesaria para la seguridad de las sesiones

        - BIBLAT_MONGODB_NAME:    nombre de la base (default: 'biblat')
        - BIBLAT_MONGODB_HOST:    host del servicio (default: 'localhost')
        - BIBLAT_MONGODB_PORT:    puerto del servicio (default: 27017)
        - BIBLAT_MONGODB_USER:    [opcional] usuario de la base (default: None)
        - BIBLAT_MONGODB_PASS:    [opcional] password de la base (default: None)

        - BIBLAT_TOKEN_EMAIL_SALT: Clave para la seguridad de los tokens
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

    # mongoDB
    MONGODB_NAME = os.environ.get('BIBLAT_MONGODB_NAME', 'biblat')
    MONGODB_HOST = os.environ.get('BIBLAT_MONGODB_HOST', 'localhost')
    MONGODB_PORT = os.environ.get('BIBLAT_MONGODB_PORT', 27017)
    MONGODB_USER = os.environ.get('BIBLAT_MONGODB_USER', None)
    MONGODB_PASS = os.environ.get('BIBLAT_MONGODB_PASS', None)

    MONGODB_SETTINGS = {
        'db': MONGODB_NAME,
        'host': MONGODB_HOST,
        'port': int(MONGODB_PORT),
    }

    if MONGODB_USER and MONGODB_PASS:
        MONGODB_SETTINGS['username'] = MONGODB_USER
        MONGODB_SETTINGS['password'] = MONGODB_PASS

    # Login
    USE_SESSION_FOR_NEXT = True

    # Mail
    MAIL_DEFAULT_SENDER = 'info@biblat.unam.mx'

    # TIEMPO de EXPIRACIÓN para Los tokens
    TOKEN_MAX_AGE = 86400  # valor en segundos: 86400 = 60*60*24 = 1 día
    TOKEN_EMAIL_SALT = os.environ.get('BIBLAT_TOKEN_EMAIL_SALT',
                                      'email-secr3t-k3y')

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

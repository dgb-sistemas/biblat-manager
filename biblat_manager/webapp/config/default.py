# -*- coding: utf-8 -*-
import os

"""
    Archivo de configuración de Biblat Manager
    
    Variables de entorno
    
        * BIBLAT_SECRET_KEY: Clave necesaria para la seguridad de las sesiones
"""

SECRET_KEY = os.environ.get('BIBLAT_SECRET_KEY', 'secr3t-k3y')

# Idiomas soportados
LANGUAGES = {
    'en': 'English',
    'es': 'Español',
}

# Idioma predeterminado:
BABEL_DEFAULT_LOCALE = 'es'

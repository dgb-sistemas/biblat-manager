# -*- coding: utf-8 -*-
from flask_babelex import lazy_gettext as __


FREQUENCY = [
    ('M', 'Mensual (doce veces al año)'),
    ('B', 'Bimestral (seis veces al año)'),
    ('T', 'Trimestral (cuatro veces al año)'),
    ('C', 'Cuatrimestral (tres veces al año)'),
    ('S', 'Semestral (dos veces por año)'),
    ('A', 'Anual (una vez al año)'),
    ('K', 'Irregular'),
]

MES = [
    ('1', __('Enero')),
    ('2', __('Febrero')),
    ('3', __('Marzo')),
    ('4', __('Abril')),
    ('5', __('Mayo')),
    ('6', __('Junio')),
    ('7', __('Julio')),
    ('8', __('Agosto')),
    ('9', __('Septiembre')),
    ('10', __('Octubre')),
    ('11', __('Noviembre')),
    ('12', __('Diciembre'))
]
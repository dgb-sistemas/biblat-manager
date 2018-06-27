# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_breadcrumbs import default_breadcrumb_root

main = Blueprint('main', __name__)
default_breadcrumb_root(main, '.')

from . import views  # NOQA

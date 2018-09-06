# -*- coding: utf-8 -*-
import os
import sys

from babel.messages.frontend import CommandLineInterface
import click

from .config import settings

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='biblat_manager/webapp/*')
    COV.start()

from .webapp import create_app  # NOQA

app = create_app(os.getenv('BIBLAT_CONFIG', 'default'))


# Comandos para i18n
@app.cli.command()
def make_messages():
    """
    Escanea biblat_manager/webapp buscando strings traducible y el resultado
    lo almacena en: biblat_manager/webapp/translations/messages.pot
    """
    args = [
        'pybabel', 'extract',
        '-F', 'biblat_manager/config/babel.cfg',
        '-k', 'lazy_gettext',
        '-k', '__',
        '-o', 'biblat_manager/webapp/translations/messages.pot', '.'
    ]
    return CommandLineInterface().run(args)


@app.cli.command()
def create_catalog():
    """
    Crea los catálogos para los idiomas definidos en biblat_manager/config,
    a partir de las cadenas en: biblat_manager/webapp/translations/messages.pot
    """
    for lang in settings.Config.LANGUAGES:
        args = [
            'pybabel', 'init',
            '-i', 'biblat_manager/webapp/translations/messages.pot',
            '-d', 'biblat_manager/webapp/translations',
            '-l', '%s' % lang
        ]
        CommandLineInterface().run(args)


@app.cli.command()
def update_catalog():
    """
    Actualiza los catálogos a partir de las cadenas en:
    biblat_manager/webapp/translations/messages.pot
    """
    args = [
        'pybabel', 'update',
        '-i', 'biblat_manager/webapp/translations/messages.pot',
        '-d', 'biblat_manager/webapp/translations'
    ]
    return CommandLineInterface().run(args)


@app.cli.command()
def compile_messages():
    """Compila las traducciones de los archivos .po a .mo"""
    args = [
        'pybabel', 'compile',
        '-d', 'biblat_manager/webapp/translations'
    ]
    return CommandLineInterface().run(args)


# Comando de pruebas unitarias
@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Ejecutar tests con cobertura.')
def test(coverage):
    """Ejecutar pruebas unitarias."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import subprocess
        os.environ['FLASK_COVERAGE'] = '1'
        sys.exit(subprocess.call(sys.argv))

    import unittest
    tests = unittest.TestLoader().discover('biblat_manager/tests')
    ret = not unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()

    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        coverage_dir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=coverage_dir)
        print('HTML version: file://%s/index.html' % coverage_dir)
        COV.erase()

    sys.exit(ret)

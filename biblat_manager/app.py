# -*- coding: utf-8 -*-
import getpass
import os
import sys

from babel.messages.frontend import CommandLineInterface
import click

from biblat_manager.config import settings

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='biblat_manager/webapp/*')
    COV.start()

from biblat_manager.webapp import create_app, controllers, utils  # NOQA

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


# USER
@app.cli.command()
def create_superuser():
    """
    Crea un nuevo usuario a partir de los datos insertados en la terminal
    Para crear un nuevo usuario se necesita:
    - email (debe ser válido y único);
    - contraseña
    - si el usuario no es confirmado debe verificar su cuenta por correo
    """
    user_email = None
    user_password = None

    while user_email is None:
        user_email = input('Correo electrónico: ').strip()
        if user_email == '':
            user_email = None
            print('El correo electrónico no puede ser nulo')
        else:
            if not utils.check_valid_email(user_email):
                user_email = None
                print('Debe introducir un correo electrónico válido!')
            elif controllers.get_user_by_email(user_email):
                user_email = None
                print('El correo electrónico ya esta registrado!')

    while user_password is None:
        user_password = getpass.getpass('Contraseña: ').strip()
        if user_password == '':
            user_password = None
            print('La contraseña no puede ser nula')

    email_confirmed = input('\nCorreo electrónico confirmado? [y/n]: ').strip()
    if email_confirmed.upper() in ('Y', 'YES'):
        email_confirmed = True
    else:
        print('Debe enviar el correo de confirmación desde la interfaz web')
        email_confirmed = False

    user = controllers.create_user(user_email, user_password, email_confirmed)
    if user.id:
        print('Nuevo usuario creado con éxito!')


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
    unittest.TextTestRunner(verbosity=2).run(tests)

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

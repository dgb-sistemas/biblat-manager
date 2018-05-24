from babel.messages.frontend import CommandLineInterface
from .webapp import create_app
from .webapp.config import default as defaul_config

app = create_app()


# Comandos para i18n
@app.cli.command()
def make_messages():
    """
        Escanea biblat_manager/webapp buscando strings traducible y el resultado lo almacena en
        biblat_manager/webapp/translations/messages.pot
    """
    args = [
        'pybabel', 'extract',
        '-F', 'biblat_manager/webapp/config/babel.cfg',
        '-k', 'lazy_gettext',
        '-k', '__',
        '-o', 'biblat_manager/webapp/translations/messages.pot', '.'
    ]
    return CommandLineInterface().run(args)


@app.cli.command()
def create_catalog():
    """
    Crea los catálogos para los idiomas definidos en biblat_manager/webapp/config,
    a partir de las cadenas en: biblat_manager/webapp/translations/messages.pot
    """
    for lang in defaul_config.LANGUAGES:
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

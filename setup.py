#!/usr/bin/env python

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

setup(
    name='BiblatManager',
    version='0.0',
    packages=find_packages(),
    url='https://github.com/dgb-sistemas/biblat-manager',
    license='GPL-3.0',
    author='DGB Sistemas',
    author_email='sistemasintegralesdgb@dgb.unam.mx',
    description='Biblat Manager es un sistema para la gestión de registros bibliográficos de CLASE y PERIÓDICA',
    keywords='biblat manager clase periódica',
    maintainer_email='sistemasintegralesdgb@dgb.unam.mx',
    download_url='',
    classifiers=[],
    install_requires=[
        'click>=6.7',
        'coverage>=4.5.1',
        'Babel>=2.5.3',
        'Flask>=1.0.2',
        'Flask-BabelEx>=0.9.3',
        'Flask-Testing>=0.7.1',
        'Jinja2>=2.10',
        'Werkzeug>=0.14.1',
    ],
    tests_require=[],
    dependency_links=[],
    test_suite='',
)

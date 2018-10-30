# -*- coding: utf-8 -*-
import re

from datetime import datetime

from biblat_schema.models import (
    Documento
)
from itsdangerous import URLSafeTimedSerializer
from mock import patch
from flask import current_app, url_for
from flask_breadcrumbs import current_breadcrumbs

from biblat_manager.tests.base import BaseTestCase
from biblat_manager.webapp import forms
from biblat_manager.webapp.controllers import create_user
from biblat_manager.webapp.models import User

url_pattern = re.compile('href="(.+?)">')


class DocumentTestCase(BaseTestCase):
    def test_document_list_view(self):
        """Test de la vista del listado de documento"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        document_list_view = url_for('main.document_list')
        with current_app.app_context():
            with self.client as c:
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                response = c.get(document_list_view)
                self.assert200(response)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertTemplateUsed('documents/listar.html')

    def test_document_add_view(self):
        """Test de la vista para agregar documento"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        document_add_view = url_for('main.document_add')
        with current_app.app_context():
            with self.client as c:
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                response = c.get(document_add_view)
                self.assert200(response)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertTemplateUsed('documents/agregar.html')
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.DocumentRegistrationForm)

    def test_document_add_insert_one(self):
        """Test para registro de un documento"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_document_data = {
            'numero_sistema': '000468737',
            'titulo_documento': 'Sobre el inicio de los Grundrisse de Marx: '
                                'el "Bastiat y Carey" o la necesidad de pensar '
                                'la producción en general en Enrique Dussel.',
            'doi': '10.1145/1067268.1067287',
            'paginacion': '153-176',
            'referencias': True,
            'idioma-0': 'es',
            'autores-0-nombre': 'González Jiménez, Alejandro Fernando',
            'autores-0-correo_electronico': 'gonzalezja@hotmail.com',
            'autores-0-referencia': '1',
            'autor_corporativo-0-institucion': 'Universidad Nacional Autónoma de México, Ciudad de México. México',
            'autor_corporativo-0-dependencia': 'Facultad de Economía',
            'autor_corporativo-0-pais': 'MX',
            'resumen-0-idioma': 'spa',
            'resumen-0-resumen': 'En este trabajo se intenta proponer, desde los márgenes, elementos '
                       'que cuestionen la forma tradicional de iniciar la lectura de los '
                       'Grundrisse de Karl Marx y propone al mismo tiempo la restitución del '
                       'manuscrito llamado “Bastiat y Carey” como su verdadero comienzo argumental. '
                       'Ello a través de una revisión panorámica de su recepción en América Latina '
                       'y en particular en la recepción hecha de los manuscritos de 1857-58 de la '
                       'crítica de la economía política por Enrique Dussel. Partiendo de la importancia '
                       'que este autor latinoamericano pone sobre la necesidad en Marx de pensar el '
                       'concepto de producción en general.',
            'tipo_documento': '1',
            'enfoque_documento': '1',
            'disciplina-0-disciplina': '5',
            'subdisciplinas-0-subdisciplinas': '1',
            'nombres_geograficos-0-nombres_geograficos': '1',
            'palabra_clave-0-idioma': 'spa',
            'palabra_clave-0-palabra_clave': 'Marx, Karl',
            'palabra_clave-1-idioma': 'spa',
            'palabra_clave-1-palabra_clave': 'Grundrisse',
            'texto_completo': 'http://132.248.9.34/hevila/Deraizdiversa/2017/vol4/no8/6.pdf',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        document_add_view = url_for('main.document_add')
        expected_msg = 'Datos correctos'
        with current_app.app_context():
            with self.client as c:
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # registro de documento
                response = c.post(
                    document_add_view,
                    data=new_document_data,
                    follow_redirects=True
                )
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("documents/agregar.html")
                self.assertIn(expected_msg,
                          response.data.decode('utf-8'))
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.DocumentRegistrationForm)


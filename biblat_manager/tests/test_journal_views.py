# -*- coding: utf-8 -*-
import re

from biblat_schema.models import (
    Revista
)
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_breadcrumbs import current_breadcrumbs

from biblat_manager.tests.base import BaseTestCase
from biblat_manager.webapp import forms
from biblat_manager.webapp.controllers import create_user

url_pattern = re.compile('href="(.+?)">')


class JournalTestCase(BaseTestCase):
    def test_journal_list_view(self):
        """Test de la vista del listado de revistas"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        document_list_view = url_for('main.revista_list')
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
                self.assertTemplateUsed('forms/listar_revistas.html')

    def test_journal_add_view(self):
        """Test de la vista para agregar revista"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        revista_add_view = url_for('main.revista_add')
        with current_app.app_context():
            with self.client as c:
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                response = c.get(revista_add_view)
                self.assert200(response)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertTemplateUsed('forms/revistas_add.html')
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.RevistaForm)

    def test_journal_add_insert_one(self):
        """Test para nuevo registro de revista"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_journal_data = {
            'base_datos': 'CLA01',
            'titulo': 'Sobre el inicio de los Grundrisse de Marx: '
                      'el "Bastiat y Carey" o la necesidad de pensar '
                      'la producción en general en Enrique Dussel.',
            'titulo_abreviado': '',
            'issn': '1533-1764',
            'issn_electronico': '',
            'pais': 'MX',
            'disciplina': '5',
            'licencia_cc': 'CC-BY',
            'sherpa_romeo': 'B',
            'idioma': 'ESP',
            'periodicidad': 'B',
            'logo': '',
            'Portada': '',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        journal_add_view = url_for('main.revista_add')
        expected_msg = 'Datos correctos'
        with current_app.app_context():
            with self.client as c:
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # registro de documento
                response = c.post(
                    journal_add_view,
                    data=new_journal_data,
                    follow_redirects=True
                )
                context_form = self.get_context_variable('form')
                print(context_form.errors)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/revistas_add.html")
                self.assertIn(expected_msg, response.data.decode('utf-8'))
                self.assertIsInstance(context_form, forms.RevistaForm)

# -*- coding: utf-8 -*-
import re


from biblat_schema.models import (
    Fasciculo
)
from itsdangerous import URLSafeTimedSerializer
from flask import current_app, url_for
from flask_breadcrumbs import current_breadcrumbs

from biblat_manager.tests.base import BaseTestCase
from biblat_manager.webapp import forms
from biblat_manager.webapp.controllers import create_user

url_pattern = re.compile('href="(.+?)">')



class FasciculoTestCase(BaseTestCase):
    def test_fasciculo_list_view(self):
        """Test de la vista del listado de fasciculos"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        document_list_view = url_for('main.fasciculo_list')
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
                self.assertTemplateUsed('forms/listar_fasciculos.html')

    def test_fasciculo_add_view(self):
        """Test de la vista para agregar fasciculo"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        fasciculo_add_view = url_for('main.fasciculo_add')
        with current_app.app_context():
            with self.client as c:
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                response = c.get(fasciculo_add_view)
                self.assert200(response)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertTemplateUsed('forms/fasciculos_add.html')
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.FasciculoForm)

    def test_fasciculo_add_insert_one(self):
        """Test para nuevo registro de fasciculo"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_fasciculo_data = {
            'revista': 'Ciencia desde México',
            'volumen': '12',
            'numero': '8',
            'anio': '2018',
            'mes_inicial': '1',
            'mes_final': '12',
            'parte': 'Cuarta de doce'
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        fasciculo_add_view = url_for('main.fasciculo_add')
        expected_msg = 'Datos correctos'
        with current_app.app_context():
            with self.client as c:
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # registro de documento
                response = c.post(
                    fasciculo_add_view,
                    data=new_fasciculo_data,
                    follow_redirects=True)
                context_form = self.get_context_variable('form')
                print(context_form.errors)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/fasciculos_add.html")
                self.assertIn(expected_msg, response.data.decode('utf-8'))
                self.assertIsInstance(context_form, forms.FasciculoForm)

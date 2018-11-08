# -*- coding: utf-8 -*-
import flask
from flask import current_app, url_for
from flask_breadcrumbs import current_breadcrumbs

from biblat_manager.webapp.controllers import create_user
from biblat_manager.tests.base import BaseTestCase


class MainTestCase(BaseTestCase):

    def test_home_page(self):
        """Test de la página principal"""
        admin_user = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(admin_user['email'], admin_user['password'], True)
        login_url = url_for('main.login')
        with current_app.app_context():
            with self.client as c:
                # login de usuario admin
                login_response = c.post(
                    login_url,
                    data=admin_user,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                response = c.get(url_for('main.index'))
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertEqual([i.url for i in current_breadcrumbs],
                                 ['/'])
                self.assert_template_used("main/index.html")

    def test_change_set_locale(self):
        """
        Test para cambiar el idioma de la interfaz, con la URL:
        '/set_locale/<string:lang_code>', que debe crear una variable
        de sesión con el valor de lang_code.
        """

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='es_MX'))
            self.assertEqual(302, response.status_code)
            self.assertEqual(flask.session['lang'], 'es_MX')

    def test_change_set_locale_with_unknow_lang(self):
        """
        Test para cambiar el idioma de la interfaz, con la URL:
        '/set_locale/<string:lang_code>' y un código de idioma inválido
        que debe regresar un 'status_code:400'
        y mantener el idioma predeterminado 'es'.
        """
        expected_message = u'Código de idioma inválido'

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='jp'))
            self.assertEqual(400, response.status_code)
            self.assertIn(expected_message, response.data.decode('utf-8'))

    def test_redirect_when_change_set_locale(self):
        """
        Test para verificar la redirección de la función de vista 'set_locale'
        que debe regresar a la página de referencia.
        """

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='es_MX'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

    def test_set_menutoggle(self):
        """Test para verificar el cambio de menú en sesión"""
        with self.client as c:
            response = c.get(url_for('main.set_menutoggle'))
            self.assertStatus(response, 200)
            self.assertEqual(flask.session['menutoggle'], 'open')
            self.assertEqual(response.data.decode('utf-8'), 'open')
            response = c.get(url_for('main.set_menutoggle'))
            self.assertStatus(response, 200)
            self.assertEqual(flask.session['menutoggle'], '')
            self.assertEqual(response.data.decode('utf-8'), '')

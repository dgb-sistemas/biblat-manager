# -*- coding: utf-8 -*-
import flask
from flask import current_app, url_for
from flask_testing import TestCase

from biblat_manager.webapp import create_app


class MainTestCase(TestCase):

    def create_app(self):
        return create_app('testing')

    def test_home_page(self):
        """Test de la página principal"""
        with current_app.app_context():
            with self.client as c:
                response = c.get(url_for('main.index'))
                self.assertStatus(response, 200)

    def test_change_set_locale(self):
        """
        Test para cambiar el idioma de la interfaz, con la URL:
        '/set_locale/<string:lang_code>', que debe crear una variable
        de sesión con el valor de lang_code.
        """

        with self.client as c:
            response = c.get(url_for('main.set_locale', lang_code='es'))
            self.assertEqual(302, response.status_code)
            self.assertEqual(flask.session['lang'], 'es')

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
            response = c.get(url_for('main.set_locale', lang_code='es'),
                             headers={'Referer': '/'},
                             follow_redirects=True)
            self.assertStatus(response, 200)

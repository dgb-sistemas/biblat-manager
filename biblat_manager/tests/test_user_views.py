# -*- coding: utf-8 -*-
import re

from itsdangerous import URLSafeTimedSerializer
from mock import patch
from flask import current_app, url_for

from biblat_manager.tests.base import BaseTestCase
from biblat_manager.webapp import forms, mail
from biblat_manager.webapp.controllers import create_user
from biblat_manager.webapp.models import User

reset_pwd_url_pattern = re.compile('href="(.+?)">')


class UserTestCase(BaseTestCase):

    def test_login_view(self):
        """"Test de las vista de login"""
        login_url = url_for('main.login')
        with current_app.app_context():
            with self.client as c:
                response = c.get(login_url)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("auth/login.html")
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.LoginForm)

    def test_login_registered_user(self):
        """Test de login de usuario registrado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')

        with current_app.app_context():
            with self.client as c:
                # login de usuario
                response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("main/index.html")

    def test_login_unregistered_user(self):
        """Test de login de usuario no registrado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        login_url = url_for('main.login')

        with current_app.app_context():
            with self.client as c:
                # login de usuario
                response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                expected_errors_msg = 'Usuario no registrado'
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertIn(expected_errors_msg,
                              response.data.decode('utf-8'))
                self.assert_template_used("auth/login.html")

    def test_login_wrong_password(self):
        """Test de login de usuario con contraseña incorrecta"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_data['password'] = 'quxquuxcorge'

        with current_app.app_context():
            with self.client as c:
                # login de usuario
                response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                expected_errors_msg = 'Contraseña incorrecta'
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertIn(expected_errors_msg,
                              response.data.decode('utf-8'))
                self.assert_template_used("auth/login.html")

    def test_login_unverified_email(self):
        """Test de login de usuario con correo no verificado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], False)
        login_url = url_for('main.login')

        with current_app.app_context():
            with self.client as c:
                # login de usuario
                response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                expected_errors_msg = 'Correo electrónico no verificado'
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertIn(expected_errors_msg,
                              response.data.decode('utf-8'))
                self.assert_template_used("auth/login.html")

    def test_login_redirect(self):
        """"Test de redirección de usuario con sesión activa"""
        """Test de login de usuario registrado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')

        with current_app.app_context():
            with self.client as c:
                # login de usuario
                response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(response, 200)
                # llamada a login nuevamente
                response_login = c.get(login_url, follow_redirects=True)
                self.assertStatus(response_login, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("main/index.html")

    def test_logout(self):
        """Test de logout de usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        logout_url = url_for('main.logout')

        with current_app.app_context():
            with self.client as c:
                # login de usuario
                response_login = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(response_login, 200)
                # logout de usuario
                logout_response = c.get(logout_url, follow_redirects=True)
                self.assertEqual('text/html; charset=utf-8',
                                 logout_response.content_type)
                self.assert_template_used("auth/login.html")

    def test_reset_password(self):
        """Test de la vista de recuperación de contraseña"""
        reset_url = url_for('main.reset')
        with current_app.app_context():
            with self.client as c:
                response = c.get(reset_url)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("auth/reset.html")
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.EmailForm)

    def test_reset_invalid_email(self):
        """Test de recuperación con email no registrado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
        }
        reset_url = url_for('main.reset')
        expected_errors_msg = 'Usuario no registrado'
        with current_app.app_context():
            with self.client as c:
                response = c.post(
                    reset_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(response, 404)
                self.assertIn(expected_errors_msg,
                              response.data.decode('utf-8'))

    def test_reset_unverified_email(self):
        """Test de recuperación con email no registrado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], False)
        reset_url = url_for('main.reset')
        with current_app.app_context():
            with self.client as c:
                response = c.post(
                    reset_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("auth/unconfirmed_email.html")

    def test_reset_registered_user(self):
        """Test de recuperación con email no registrado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        reset_url = url_for('main.reset')
        expected_msg = 'Se enviaron instrucciones para recuperar su ' \
                       'contraseña al correo: %s' % user_data['email']
        expected_email = {
            'subject': 'Instrucciones para recuperar su contraseña',
            'recipients': [user_data['email']],
            'reset_link': url_for('main.reset')
        }
        with current_app.app_context():
            with self.client as c:
                with mail.record_messages() as outbox:
                    response = c.post(
                        reset_url,
                        data=user_data,
                        follow_redirects=True)
                    self.assertStatus(response, 200)
                    self.assertEqual('text/html; charset=utf-8',
                                     response.content_type)
                    self.assert_template_used("auth/login.html")
                    self.assertIn(expected_msg,
                                  response.data.decode('utf-8'))
                    # Verificar envío de correo
                    email_msg = outbox[0]
                    self.assertEqual(1, len(outbox))
                    self.assertEqual(expected_email['subject'],
                                     email_msg.subject)
                    self.assertEqual(expected_email['recipients'],
                                     email_msg.recipients)
                    self.assertIn(expected_email['reset_link'],
                                  email_msg.html)

    def test_reset_registered_user_send_error(self):
        """Test de error en recuperación de contraseña"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        reset_url = url_for('main.reset')
        expected_error_msg = 'Ocurrió un problema al enviar el correo con ' \
                             'las instrucciones de recuperación de ' \
                             'contraseña a la dirección: %s' % user_data['email']
        with current_app.app_context():
            with self.client as c:
                with patch('biblat_manager.webapp.utils'
                           '.get_timed_serializer') as mock:
                    mock.return_value = URLSafeTimedSerializer(None)
                    response = c.post(
                        reset_url,
                        data=user_data,
                        follow_redirects=True)
                    self.assertStatus(response, 200)
                    self.assertEqual('text/html; charset=utf-8',
                                     response.content_type)
                    self.assert_template_used("auth/login.html")
                    self.assertIn(expected_error_msg,
                                  response.data.decode('utf-8'))

    def test_reset_with_invalid_token(self):
        """Test de error en recuperación de contraseña con token invalido"""
        reset_with_token_url = url_for('main.reset_with_token', token='qwerty')
        expected_error_msg = 'Token inválido'
        with current_app.app_context():
            with self.client as c:
                response = c.get(reset_with_token_url)
                self.assertStatus(response, 404)
                self.assertEqual('text/html',
                                 response.content_type)
                self.assertIn(expected_error_msg,
                              response.data.decode('utf-8'))

    def test_reset_with_valid_token(self):
        """Test de las vista reset_with_token"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        reset_url = url_for('main.reset')

        with current_app.app_context():
            with self.client as c:
                with mail.record_messages() as outbox:
                    c.post(
                        reset_url,
                        data=user_data,
                        follow_redirects=True)
                    # Obtenemos url del correo
                    email_msg = outbox[0]
                    links_found = reset_pwd_url_pattern.findall(email_msg.html)
                    self.assertGreaterEqual(1, len(links_found))
                    reset_url_with_token = [url for url in links_found if
                                            reset_url in url]
                    self.assertEqual(1, len(reset_url_with_token))
                    reset_url_with_token = reset_url_with_token[0]
                    # Llamamos a la vista reset_with_token
                    response = c.get(reset_url_with_token)
                    self.assertStatus(response, 200)
                    self.assertTemplateUsed('auth/reset_with_token.html')
                    context_form = self.get_context_variable('form')
                    self.assertIsInstance(context_form, forms.PasswordForm)

    def test_reset_with_valid_token_update_ok(self):
        """Test de recuperación de contraseña"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        reset_url = url_for('main.reset')

        with current_app.app_context():
            with self.client as c:
                with mail.record_messages() as outbox:
                    c.post(
                        reset_url,
                        data=user_data,
                        follow_redirects=True)
                    # Obtenemos url del correo
                    email_msg = outbox[0]
                    links_found = reset_pwd_url_pattern.findall(email_msg.html)
                    self.assertGreaterEqual(1, len(links_found))
                    reset_url_with_token = [url for url in links_found if
                                            reset_url in url]
                    self.assertEqual(1, len(reset_url_with_token))
                    reset_url_with_token = reset_url_with_token[0]
                    # Llamamos a la vista reset_with_token con la contraseña
                    new_password = 'quxquuxcorge'
                    response = c.post(
                        reset_url_with_token,
                        data={'password': new_password,
                              'confirm': new_password},
                        follow_redirects=True
                    )
                    self.assertStatus(response, 200)
                    self.assertTemplateUsed('auth/login.html')
                    user = User.get_by_email(user_data['email'])
                    self.assertTrue(user.check_password_hash(new_password))

    def test_reset_with_valid_token_unverified_email(self):
        """Test de recuperación de contraseña"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'foobarbaz',
        }
        create_user(user_data['email'], user_data['password'], True)
        reset_url = url_for('main.reset')

        with current_app.app_context():
            with self.client as c:
                with mail.record_messages() as outbox:
                    c.post(
                        reset_url,
                        data=user_data,
                        follow_redirects=True)
                    # Obtenemos url del correo
                    email_msg = outbox[0]
                    links_found = reset_pwd_url_pattern.findall(email_msg.html)
                    self.assertGreaterEqual(1, len(links_found))
                    reset_url_with_token = [url for url in links_found if
                                            reset_url in url]
                    self.assertEqual(1, len(reset_url_with_token))
                    reset_url_with_token = reset_url_with_token[0]
                    # Actualizamos el estado del usuario
                    user = User.get_by_email(user_data['email'])
                    user.email_confirmed = False
                    user.save()
                    # Llamamos a la vista reset_with_token con la contraseña
                    new_password = 'quxquuxcorge'
                    response = c.post(
                        reset_url_with_token,
                        data={'password': new_password,
                              'confirm': new_password},
                        follow_redirects=True
                    )
                    self.assertStatus(response, 200)
                    self.assertTemplateUsed('auth/unconfirmed_email.html')
                    user = User.get_by_email(user_data['email'])
                    self.assertTrue(user.check_password_hash(
                        user_data['password'])
                    )

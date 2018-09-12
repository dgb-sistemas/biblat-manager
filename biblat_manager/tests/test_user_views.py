# -*- coding: utf-8 -*-
import re

from itsdangerous import URLSafeTimedSerializer
from mock import patch
from flask import current_app, url_for
from flask_breadcrumbs import current_breadcrumbs

from biblat_manager.tests.base import BaseTestCase
from biblat_manager.webapp import forms, mail, notifications
from biblat_manager.webapp.controllers import create_user
from biblat_manager.webapp.models import User

url_pattern = re.compile('href="(.+?)">')


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
            'password': 'F00barbaz$',
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
            'password': 'F00barbaz$',
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
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_data['password'] = 'Quxquuxc0rge$'

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
            'password': 'F00barbaz$',
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
            'password': 'F00barbaz$',
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
            'password': 'F00barbaz$',
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
                self.assertStatus(response, 200)
                self.assertIn(expected_errors_msg,
                              response.data.decode('utf-8'))

    def test_reset_unverified_email(self):
        """Test de recuperación con email no registrado"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
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
            'password': 'F00barbaz$',
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

    def test_reset_registered_user_send_email_error(self):
        """Test de error en envío de coreo de recuperación de contraseña"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
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
            'password': 'F00barbaz$',
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
                    links_found = url_pattern.findall(email_msg.html)
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
            'password': 'F00barbaz$',
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
                    links_found = url_pattern.findall(email_msg.html)
                    self.assertGreaterEqual(1, len(links_found))
                    reset_url_with_token = [url for url in links_found if
                                            reset_url in url]
                    self.assertEqual(1, len(reset_url_with_token))
                    reset_url_with_token = reset_url_with_token[0]
                    # Llamamos a la vista reset_with_token con la contraseña
                    new_password = 'Quxquuxc0rge$'
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
            'password': 'F00barbaz$',
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
                    links_found = url_pattern.findall(email_msg.html)
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
                    new_password = 'Quxquuxc0rge$'
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

    def test_list_users(self):
        """Test para la vista list_users"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        list_users_url = url_for('main.list_users')
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                response = c.get(list_users_url)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertEqual([i.url for i in current_breadcrumbs],
                                 ['/', '/usuarios'])
                self.assert_template_used("main/users.html")

    def test_user_detail(self):
        """Test para la vista user_detail"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                # vista user_detail
                user = User.get_by_email(user_data['email'])
                user_detail_url = url_for('main.user_detail', user_id=user.id)
                response = c.get(user_detail_url)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertEqual([i.url for i in current_breadcrumbs],
                                 ['/', '/usuarios', user_detail_url])
                self.assert_template_used("main/user.html")

    def test_user_edit(self):
        """Test para la vista user_edit"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                # vista user_edit
                user = User.get_by_email(user_data['email'])
                user_edit_url = url_for('main.user_edit', user_id=user.id)
                response = c.get(user_edit_url)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertEqual([i.url for i in current_breadcrumbs],
                                 ['/', '/usuarios', user_edit_url])
                self.assert_template_used("forms/register.html")
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.RegistrationForm)

    def test_user_edit_update_one(self):
        """Test para actualizar un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        user = User.get_by_email(user_data['email'])
        login_url = url_for('main.login')

        expected_msg = 'Usuario actualizado correctamente!'
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # edición de usuario
                user_data_update = {}
                user_data_update.update(user_data)
                user_data_update.update({
                    'username': 'administrador',
                    'password': 'Quxquuxc0rge$',
                    'confirm': 'Quxquuxc0rge$'
                })
                user_edit_url = url_for('main.user_edit', user_id=user.id)
                response = c.post(
                    user_edit_url,
                    data=user_data_update,
                    follow_redirects=True
                )
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/register.html")
                self.assertIn(expected_msg,
                              response.data.decode('utf-8'))
                updated_user = User.get_by_id(user.id)
                self.assertEqual(user_data_update['username'], updated_user.username)

    def test_user_edit_update_email(self):
        """Test para actualizar un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        user = User.get_by_email(user_data['email'])
        login_url = url_for('main.login')

        expected_msg = 'Usuario actualizado correctamente!'
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # edición de usuario
                user_data_update = {}
                user_data_update.update(user_data)
                user_data_update.update({
                    'email': 'user@biblat.unam.mx',
                    'username': 'administrador',
                    'password': 'Quxquuxc0rge$',
                    'confirm': 'Quxquuxc0rge$'
                })
                user_edit_url = url_for('main.user_edit', user_id=user.id)
                response = c.post(
                    user_edit_url,
                    data=user_data_update,
                    follow_redirects=True
                )
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/register.html")
                self.assertIn(expected_msg,
                              response.data.decode('utf-8'))
                updated_user = User.get_by_id(user.id)
                self.assertEqual(user_data_update['email'], updated_user.email)

    def test_user_edit_update_send_email_error(self):
        """Test para actualizar un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        user = User.get_by_email(user_data['email'])
        login_url = url_for('main.login')

        with current_app.app_context():
            with self.client as c:
                with patch('biblat_manager.webapp.utils'
                           '.get_timed_serializer') as mock:
                    mock.return_value = URLSafeTimedSerializer(None)
                    # login de usuario
                    c.post(
                        login_url,
                        data=user_data,
                        follow_redirects=True)

                    # edición de usuario
                    user_data_update = {}
                    user_data_update.update(user_data)
                    user_data_update.update({
                        'email': 'user@biblat.unam.mx',
                        'username': 'administrador',
                        'password': 'Quxquuxc0rge$',
                        'confirm': 'Quxquuxc0rge$'
                    })
                    user_edit_url = url_for('main.user_edit', user_id=user.id)
                    response = c.post(
                        user_edit_url,
                        data=user_data_update,
                        follow_redirects=True
                    )
                    self.assertStatus(response, 200)
                    self.assertEqual('text/html; charset=utf-8',
                                     response.content_type)
                    self.assert_template_used("forms/register.html")
                    expected_error_msg = 'Ocurrió un error en el envío del ' \
                                         'correo de confirmación  a: %s' % \
                                         user_data_update['email']
                    self.assertIn(expected_error_msg,
                                  response.data.decode('utf-8'))
                    updated_user = User.get_by_id(user.id)
                    self.assertEqual(user_data_update['email'], updated_user.email)

    def test_user_edit_update_raise_value_error(self):
        """Test para actualizar un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        user = User.get_by_email(user_data['email'])
        login_url = url_for('main.login')

        with current_app.app_context():
            with self.client as c:
                with patch('biblat_manager.webapp.models.User'
                           '.send_confirmation_email') as mock:
                    mock.side_effect = ValueError('recipient_email es inválido!')
                    # login de usuario
                    c.post(
                        login_url,
                        data=user_data,
                        follow_redirects=True)

                    # edición de usuario
                    user_data_update = {}
                    user_data_update.update(user_data)
                    user_data_update.update({
                        'email': 'user@biblat.unam.mx',
                        'username': 'administrador',
                        'password': 'Quxquuxc0rge$',
                        'confirm': 'Quxquuxc0rge$'
                    })
                    user_edit_url = url_for('main.user_edit', user_id=user.id)
                    response = c.post(
                        user_edit_url,
                        data=user_data_update,
                        follow_redirects=True
                    )
                    self.assertRaises(ValueError)
                    self.assertStatus(response, 200)
                    self.assertEqual('text/html; charset=utf-8',
                                     response.content_type)
                    self.assert_template_used("forms/register.html")
                    expected_error_msg = 'Ocurrió un error en el envío del ' \
                                         'correo de confirmación  a: %s' % \
                                         user_data_update['email']
                    self.assertIn(expected_error_msg,
                                  response.data.decode('utf-8'))
                    updated_user = User.get_by_id(user.id)
                    self.assertEqual(user_data_update['email'], updated_user.email)

    def test_user_edit_duplicated_email(self):
        """Test para registro de un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }

        create_user(user_data['email'], user_data['password'], True)
        create_user('user@biblat.unam.mx', 'F00barbaz$', True)
        user = User.get_by_email(user_data['email'])
        login_url = url_for('main.login')

        expected_error_msg = 'El correo electrónico ya esta registrado'
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # edición de usuario
                user_data_update = {}
                user_data_update.update(user_data)
                user_data_update.update({
                    'email': 'user@biblat.unam.mx',
                    'username': 'admin',
                    'password': 'Quxquuxc0rge$',
                    'confirm': 'Quxquuxc0rge$'
                })
                user_edit_url = url_for('main.user_edit', user_id=user.id)
                response = c.post(
                    user_edit_url,
                    data=user_data_update,
                    follow_redirects=True
                )
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/register.html")
                self.assertIn(expected_error_msg,
                              response.data.decode('utf-8'))
                updated_user = User.get_by_id(user.id)
                self.assertEqual(user_data['email'], updated_user.email)

    def test_user_add(self):
        """Test para la vista user_add"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_add_url = (url_for('main.user_add'))
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                login_response = c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)
                self.assertStatus(login_response, 200)
                # vista user_add
                response = c.get(user_add_url)
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assertEqual([i.url for i in current_breadcrumbs],
                                 ['/', '/usuarios', user_add_url])
                self.assert_template_used("forms/register.html")
                context_form = self.get_context_variable('form')
                self.assertIsInstance(context_form, forms.RegistrationForm)

    def test_user_add_insert_one(self):
        """Test para registro de un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@biblat.unam.mx',
            'password': 'F00barbaz$',
            'confirm': 'F00barbaz$'
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_add_url = (url_for('main.user_add'))
        expected_msg = 'Se envío un correo de confirmación a: %s' % new_user_data['email']
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # registro de usuario
                response = c.post(
                    user_add_url,
                    data=new_user_data,
                    follow_redirects=True
                )
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/register.html")
                self.assertIn(expected_msg,
                              response.data.decode('utf-8'))
                user = User.get_by_email(new_user_data['email'])
                self.assertIsInstance(user, User)

    def test_user_add_insert_one_week_password(self):
        """Test para registro de un usuario con contraseña debil"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@biblat.unam.mx',
            'password': 'qwerty',
            'confirm': 'qwerty'
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_add_url = (url_for('main.user_add'))
        expected_error_msg = 'La contraseña es muy corta, la longitud mínima ' \
                             'es de 8 caracteres'
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # registro de usuario
                response = c.post(
                    user_add_url,
                    data=new_user_data,
                    follow_redirects=True
                )
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/register.html")
                self.assertIn(expected_error_msg,
                              response.data.decode('utf-8'))

    def test_user_add_insert_email_duplicated(self):
        """Test para registro de un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_user_data = {
            'username': 'newuser',
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
            'confirm': 'F00barbaz$'
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_add_url = (url_for('main.user_add'))
        expected_error_msg = 'El correo electrónico ya esta registrado'
        with current_app.app_context():
            with self.client as c:
                # login de usuario
                c.post(
                    login_url,
                    data=user_data,
                    follow_redirects=True)

                # registro de usuario
                response = c.post(
                    user_add_url,
                    data=new_user_data,
                    follow_redirects=True
                )
                self.assertStatus(response, 200)
                self.assertEqual('text/html; charset=utf-8',
                                 response.content_type)
                self.assert_template_used("forms/register.html")
                self.assertIn(expected_error_msg,
                              response.data.decode('utf-8'))

    def test_user_add_insert_one_send_email_error(self):
        """Test para registro de un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@biblat.unam.mx',
            'password': 'F00barbaz$',
            'confirm': 'F00barbaz$'
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_add_url = (url_for('main.user_add'))
        expected_error_msg = 'Ocurrió un error en el envío del correo de ' \
                             'confirmación  a: %s' % new_user_data['email']
        with current_app.app_context():
            with self.client as c:
                with patch('biblat_manager.webapp.utils'
                           '.get_timed_serializer') as mock:
                    mock.return_value = URLSafeTimedSerializer(None)
                    # login de usuario
                    c.post(
                        login_url,
                        data=user_data,
                        follow_redirects=True)

                    # registro de usuario
                    response = c.post(
                        user_add_url,
                        data=new_user_data,
                        follow_redirects=True
                    )
                    self.assertStatus(response, 200)
                    self.assertEqual('text/html; charset=utf-8',
                                     response.content_type)
                    self.assert_template_used("forms/register.html")
                    self.assertIn(expected_error_msg,
                                  response.data.decode('utf-8'))
                    user = User.get_by_email(new_user_data['email'])
                    self.assertIsInstance(user, User)

    def test_user_add_insert_one_raise_value_error(self):
        """Test para registro de un usuario"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@biblat.unam.mx',
            'password': 'F00barbaz$',
            'confirm': 'F00barbaz$'
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        user_add_url = (url_for('main.user_add'))
        expected_error_msg = 'Ocurrió un error en el envío del correo de ' \
                             'confirmación  a: %s' % new_user_data['email']
        with current_app.app_context():
            with self.client as c:
                with patch('biblat_manager.webapp.models.User'
                           '.send_confirmation_email') as mock:
                    mock.side_effect = ValueError('recipient_email es inválido!')
                    # login de usuario
                    c.post(
                        login_url,
                        data=user_data,
                        follow_redirects=True)

                    # registro de usuario
                    response = c.post(
                        user_add_url,
                        data=new_user_data,
                        follow_redirects=True
                    )
                    self.assertRaises(ValueError)
                    self.assertStatus(response, 200)
                    self.assertEqual('text/html; charset=utf-8',
                                     response.content_type)
                    self.assert_template_used("forms/register.html")
                    self.assertIn(expected_error_msg,
                                  response.data.decode('utf-8'))
                    user = User.get_by_email(new_user_data['email'])
                    self.assertIsInstance(user, User)

    def test_user_add_insert_one_with_confirmation_email(self):
        """Test para registro de un usuario con confirmación de correo"""
        user_data = {
            'email': 'admin@biblat.unam.mx',
            'password': 'F00barbaz$',
        }
        new_user_data = {
            'username': 'newuser',
            'email': 'newuser@biblat.unam.mx',
            'password': 'F00barbaz$',
            'confirm': 'F00barbaz$'
        }
        create_user(user_data['email'], user_data['password'], True)
        login_url = url_for('main.login')
        logout_url = url_for('main.logout')
        user_add_url = (url_for('main.user_add'))
        expected_email = {
            'subject': 'Confirmación de correo electrónico',
            'recipients': [new_user_data['email']],
        }
        with current_app.app_context():
            with self.client as c:
                with mail.record_messages() as outbox:
                    # login de usuario
                    c.post(
                        login_url,
                        data=user_data,
                        follow_redirects=True)

                    # registro de usuario
                    c.post(
                        user_add_url,
                        data=new_user_data,
                        follow_redirects=True
                    )
                    # logout de usuario
                    c.get(logout_url)
                    # confirmación de correo electrónico
                    email_msg = outbox[0]
                    self.assertEqual(1, len(outbox))
                    self.assertEqual(expected_email['subject'],
                                     email_msg.subject)
                    self.assertEqual(expected_email['recipients'],
                                     email_msg.recipients)
                    links_found = url_pattern.findall(email_msg.html)
                    self.assertGreaterEqual(1, len(links_found))
                    confirm_url_with_token = [url for url in links_found if
                                              '/user/confirm/' in url]
                    self.assertEqual(1, len(confirm_url_with_token))
                    confirm_url_with_token = confirm_url_with_token[0]
                    # activamos correo electrónico
                    response = c.get(confirm_url_with_token,
                                     follow_redirects=True)
                    self.assertStatus(response, 200)
                    self.assertEqual('text/html; charset=utf-8',
                                     response.content_type)
                    self.assert_template_used("auth/login.html")
                    user = User.get_by_email(new_user_data['email'])
                    self.assertTrue(user.email_confirmed)

    def test_confirmation_email_invalid_user(self):
        """Test de error cuando se trata de activar un usuario no registrado"""
        fake_email = 'unregitered_user@biblat.unam.mx'
        expected_error_msg = 'Usuario no encontrado'
        with current_app.app_context():
            with self.client as c:
                with mail.record_messages() as outbox:
                    notifications.send_confirmation_email(fake_email)
                    email_msg = outbox[0]
                    links_found = url_pattern.findall(email_msg.html)
                    self.assertGreaterEqual(1, len(links_found))
                    confirm_url_with_token = [url for url in links_found if
                                              '/user/confirm/' in url]
                    self.assertEqual(1, len(confirm_url_with_token))
                    confirm_url_with_token = confirm_url_with_token[0]
                    # tratamos de activar con el enlace
                    response = c.get(confirm_url_with_token,
                                     follow_redirects=True)
                    self.assertStatus(response, 404)
                    self.assertEqual('text/html', response.content_type)
                    user = User.get_by_email(fake_email)
                    self.assertIsNone(user)
                    self.assertIn(expected_error_msg,
                                  response.data.decode('utf-8'))

    def test_confirmation_email_raise_exception(self):
        """Test de excepción al activar usuario"""
        fake_email = 'unregitered_user@biblat.unam.mx'
        ts = URLSafeTimedSerializer('email-secr3t-k3y')
        token = ts.dumps(fake_email, salt='email-secr3t-k3y')
        confirm_url_with_token = url_for('.confirm_email', token=token)
        with current_app.app_context():
            with self.client as c:
                with patch('biblat_manager.webapp.utils'
                           '.get_timed_serializer') as mock:
                    # tratamos de activar con el enlace
                    mock.return_value = URLSafeTimedSerializer(None)
                    response = c.get(confirm_url_with_token,
                                     follow_redirects=True)
                    self.assertStatus(response, 404)
                    self.assertEqual('text/html', response.content_type)

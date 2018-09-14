# -*- coding: utf-8 -*-
import re
import uuid
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from flask_mail import Message
from passlib.context import CryptContext
from biblat_manager.webapp import mail

REGEX_EMAIL = re.compile(
    r"[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:["
    r"a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?",
    re.IGNORECASE)  # RFC 2822 (simplified)

pwd_context = CryptContext(schemes=['bcrypt_sha256'])


def generate_uuid_32_string():
    return str(uuid.uuid4().hex)


def get_timed_serializer():
    """
    Regresa una instancia de URLSafeTimedSerializer para generar tokens
    """
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])


def check_valid_email(email):
    validation = True
    if not REGEX_EMAIL.match(email):
        validation = False
    return validation


def send_email(recipient, subject, html):
    """
    Método para el envío de emails
    - recipient: destinatario
    - subject: asunto
    - html: cuerpo del mensaje (formato html)
    Quien envía el mensaje debe definirse en la configuración 'MAIL_DEFAULT_SENDER'
    Regresa:
     - (True, '') em caso de éxito.
     - (False, 'MENSAJE DE ERROR/EXCEPCIÓN') en caso de error/excepción
    """
    recipients = [recipient, ]
    if isinstance(recipient, list):
        recipients = recipient
    try:
        msg = Message(subject=subject,
                      sender=current_app.config['MAIL_DEFAULT_SENDER'],
                      recipients=recipients,
                      html=html)
        mail.send(msg)
        return True, ''
    except Exception as e:
        return False, e

# coding:utf-8

from flask import current_app
from flask_testing import TestCase

from biblat_manager.webapp import create_app, dbmongo


class BaseTestCase(TestCase):

    def create_app(self):
        return create_app('testing')

    def setUp(self):
        self.app = current_app
        self.db_name = self.app.config['MONGODB_SETTINGS']['db']

    def tearDown(self):
        try:
            dbmongo.connection.drop_database(self.db_name)
        except Exception:
            dbmongo.connection.connection.client.drop_database(self.db_name)

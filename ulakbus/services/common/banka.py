# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zato.server.service import Service
from ulakbus.models.ogrenci import Banka, BankaAuth


class AuthException(Exception):
    pass


def authenticate(f):
    def auth(self):
        try:
            self.banka = Banka.object.get(kod=str(self.banka_kodu))
            BankaAuth.object.get(username=self.bank_username, password=self.bank_password, banka=self.banka)
            self.logger.info("Authentication completed successfully.")
        except:
            raise AuthException("Authentication failed.")
        return f(self)

    return auth


class BankaService(Service):
    """
    Banka Zato Servisi
    """

    def __init__(self):
        self.banka = None

    class SimpleIO:
        input_required = ('banka_kodu', 'bank_username', 'bank_password')
        output_required = ()

    def handle(self):
        try:
            self.get_data()
        except AuthException as e:
            self.logger.info(e.message)

    @authenticate
    def get_data(self):
        pass

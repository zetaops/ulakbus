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
    """
    Banka yetkilendirme kontrolu
    """

    def auth(self):
        try:
            self.banka = Banka.objects.get(kod=str(self.banka_kodu))
            BankaAuth.objects.get(username=self.bank_username, password=self.bank_password, banka=self.banka)
            self.logger.info("Authentication completed successfully.")
        except:
            raise AuthException("Authentication failed.")
        return f(self)

    return auth


class BankaService(Service):
    """
    Banka Zato Servisi

    :param banka_kodu: Universite tarafindan bankaya verilen kod
    :type banka_kodu: int -> str

    :param bank_username: Universite tarafindan bankaya verilen kullanici kodu
    :type bank_username: str

    :param bank_password: Universite tarafindan bankaya verilen kullanici sifresi
    :type bank_username: str
    """

    def __init__(self):
        self.banka = None
        super(BankaService, self).__init__()

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

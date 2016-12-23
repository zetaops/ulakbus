# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Banka Service

Banka servislerinin kalıtılacağı abstract Banka servisini ve
banka yetkilendirme kontrolü fonksiyonunu içeren modül.

"""

from ulakbus.models.ogrenci import Banka, BankaAuth
from ulakbus.services.ulakbus_service import UlakbusService


class AuthException(Exception):
    """
    Banka yetkilendirmesi için verilen bilgilerin sistemdeki bilgilerle
    uyuşmaması durumunda fırlatılan Yetkilendirme Hatası

    """

    pass


def authenticate(func):
    """
    Banka yetkilendirme kontrolü için decorator fonksiyon.

    Banka servislerine istek geldiğinde öncelikle bu fonksiyon tetiklenir ve
    Banka kullanıcı bilgileri kontrol edilir.

    Bilgiler sistemdeki bilgilerle uyuşuyorsa işleme devam edilir.
    Aksi taktirde AuthException hatası verilir.

    Args:
        func (function): Yetkilendirme işleminden geçmesi gereken fonksiyon.

    """

    def auth(self):
        try:
            self.banka = Banka.objects.get(kod=str(self.request.input.banka_kodu))
            BankaAuth.objects.get(username=self.request.input.bank_username,
                                  password=self.request.input.bank_password,
                                  banka=self.banka)
            self.logger.info("Authentication completed successfully.")
        except Exception as e:
            raise AuthException("Authentication failed. %s" % e)
        return func(self)

    return auth


class BankaService(UlakbusService):
    """
    Banka servislerinin kalıtılacağı abstract Zato Servisi.

    Banka servisleri bu servisle yetkilendirme işleminden geçip
    gerekli girdileri elde eder ve çıktıları geri döndürürler.

    Note:
        self.request (zato.server.service.Request):
            Servise gelen isteği tutan Zato nesnesi.
            Girdileri elde etmek için `self.request.input` kullanılır.
        self.response (zato.server.service.Response):
            Servisten dönecek olan cevabı tutan Zato nesnesi.
            Çıktı parametrelerini saklamak için `self.response.payload` kullanılır.

    """

    HAS_CHANNEL = False

    def __init__(self):
        #: Banka: Servisleri kullanacak olan yetkilendirilecek banka.
        self.banka = None
        super(BankaService, self).__init__()

    class SimpleIO:
        """
        Servis girdilerinin ve çıktılarının belirlendiği yapı.

        Servis çağrısı yapılırken:
            - request_elem: Servise gelen isteğin (JSON, XML) ismi
            - input_required: Zorunlu olarak sağalanacak girdilerin listesi
            - input_optional: İsteğe bağlı olarak sağlanacak girdilerin listesi
            - default_value: İsteğe bağlı girdilerin değerlerinin, servis çağrılırken
              verilmemesi durumunda kullanılacak varsayılan değer

        Servisin döneceği cevap belirlenirken:
            - response_elem: Servisten dönen veriyi içeren (payload)
              cevabın (JSON, XML) ismi
            - output_required: Zorunlu olarak döndürülerek çıktıların listesi
            - output_optional: İsteğe bağlı olarak döndürülecek çıktıların listesi

        Note:
            SimpleIO sınıfında belirlenen özellikler,
            doğrudan yer aldığı servisin özellikleri olmaktadır.

            - banka_kodu (str): Üniversite tarafından bankaya verilen kod
            - bank_username (str): Üniversite tarafından bankaya verilen kullanıcı adı
            - bank_password (str): Üniversite tarafından bankaya verilen şifre

        """

        input_required = ('banka_kodu', 'bank_username', 'bank_password')
        output_required = ()

    def handle(self):
        """
        Servis çağrıldığında tetiklenen metod.

        Yetkilendirme işleminin sonucuna göre servis çalışmaya devam eder.

        """

        try:
            self.get_data()
        except AuthException:
            self.logger.exception("Authentication failed.")

    @authenticate
    def get_data(self):
        """
        Servise gelen girdileri alan ve bu girdilere göre gerekli bilgileri
        elde edip cevap olarak döndüren metod.

        Gerçekleştirimi bu servisten kalıtılan servisler tarafından yapılmaktadır.

        """

        pass

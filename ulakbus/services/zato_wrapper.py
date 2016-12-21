# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""HITAP Zato Service Wrapper

Includes Zato Service Wrapper and wrapper functions for services
such as Hitap, Mernis, KPS etc.


Example:

    .. code-block:: python

        from zato_wrapper_class import HitapHizmetCetveliGetir
        zs = HitapHizmetCetvelGetir(tckn="12345678900")
        response = zs.zato_request()  # list, with lines of hizmet cetveli


    .. code-block:: python

        from zato_wrapper_class import HitapHizmetCetveliSenkronizeEt
        zs = HitapHizmetCetveliSenkronizeEt(tckn="12345678900")
        response = zs.zato_request()  # 'ok' or 'error'

"""

from pyoko.conf import settings
import requests
import json
from .zato_url_paths import service_url_paths
import urlparse


class ZatoService(object):
    """
    Simple zato service wrapper class.
    You can write your zato services extending this class.

    This class simply needs some parameter to be set
    as you see in init payload and service uri.

    Ping service returns just 'ok' which can be used as an health check
    to determine zato servers is alive or not.

    ``service_uri`` and ``payload`` parameters especially is
    set by extending class' __init__.

    Attributes:
        payload (str): an empty dict as default
        service_uri (str): "ping" as default

    """

    def __init__(self):
        self.payload = "{}"
        self.service_uri = "ping"

    def get_uri(self):
        """
        Simply returns full uri of zato service object.
        It uses ``ZATO_SERVER`` from settings module.

        The ``ZATO_SERVER`` can be set as environment variable as below::

            export ZATO_SERVER='http://127.0.0.1/'

        Returns:
            (str): unique identification string of service on zato services
            including join of zato server url (generally a load balancer url)
            and service name on zato.

        """

        return urlparse.urljoin(settings.ZATO_SERVER, self.service_uri)

    def zato_request(self):
        """
        Makes zato requests. Zato expects payloads as json over POST method
        and sends back json. Return json contains two parts
        one is status and the other is result.

        Status part is can be ``ok`` or ``error`` depends on
        what happens in zato servers while running. Result part is
        the data part which is expected by consumer.

        Returns:
            str: if requests fails, returns ``None``
            or simply string of zato service response payload

        """

        uri = self.get_uri()
        payload = json.loads(self.payload)
        r = requests.post(uri, data=json.dumps(payload))
        if r.status_code == 200:
            response = r.json()
            r.close()
            try:
                if response['status'] == 'ok':
                    return self.rebuild_response(response['result'])
                else:
                    # all zato internal errors will be handled here,
                    # riak error, connection error etc..
                    raise Exception("your service request failed with error %s"
                                    % response['result'])
            except KeyError:
                raise Exception("your service response contains no status code, "
                                "check your zato service package")

        if r.status_code == 404:
            raise Exception("Service called '%s' is not defined on zato "
                            "servers or service_uri changed" % self.service_uri)
        # other than 404 errors will be handled here,
        # such as unauthorized requests, permission denied or etc..
        else:
            raise Exception("Status code is something different 200 or 404 which is %s, "
                            "this means something really went bad, check zato server logs"
                            % r.status_code)

    def rebuild_response(self, response_data):
        """
        Rebuild response data

        Args:
            response_data (dict): contains data returned from service

        Returns:
            response_data (dict): reformatted data compatible with our data models

        """
        return response_data


class TcknService(ZatoService):
    @staticmethod
    def check_turkish_identity_number(tckn):
        """
        Türkiye Cumhuriyeti Kimlik Numarası geçerlilik kontrolü.
        11 karakter uzunluğunda karakter dizisi olmalı.

        Args:
            tckn (str): 11 karakter uzunluğunda TCKN.

        Returns:
            str: TCKN

        """

        if not tckn:
            raise Exception("tckn can not be empty")

        if type(tckn) is not str:
            raise TypeError("tckn must be string which is %s" % type(tckn))

        if len(tckn) != 11:
            raise Exception("tckn length must be 11")

        return tckn


class HitapService(TcknService):
    pass


class HitapServiceError(Exception):
    pass


class HitapAcikSureGetir(HitapService):
    """
    Hitap üzerinden, personelin açık süre hizmet bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapAcikSureGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapAcikSureSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki açık süre hizmet bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapAcikSureSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapAcikSureEkle(HitapService):
    """
    Personelin açık süre hizmet bilgilerinin Hitap'a,
    eklemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapAcikSureEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapAcikSureGuncelle(HitapService):
    """
    Personelin açık süre hizmet bilgilerinin Hitap üzerinde
    guncellemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapAcikSureGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapAcikSureSil(HitapService):
    """
    Personelin açık süre hizmet bilgilerinin Hitap üzerinden
    silme işlemini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapAcikSureSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapAskerlikGetir(HitapService):
    """
    Hitap üzerinden, personelin askerlik bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapAskerlikGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapAskerlikSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki askerlik bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapAskerlikSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapAskerlikEkle(HitapService):
    """
    Personelin askerlik bilgilerinin Hitap'a eklemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapAskerlikEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapAskerlikGuncelle(HitapService):
    """
    Personelin askerlik bilgilerinin Hitap üzerinde
    guncellemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapAskerlikGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapAskerlikSil(HitapService):
    """
    Personelin askerlik bilgilerinin Hitap üzerinden
    silme işlemini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapAskerlikSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapBirlestirmeGetir(HitapService):
    """
    Hitap üzerinden, personelin hizmet birleştirme bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapBirlestirmeGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapBirlestirmeSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki hizmet birleştirme bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapBirlestirmeSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapBirlestirmeEkle(HitapService):
    """
    Personelin hizmet birleştirme bilgilerinin Hitap'a
    eklemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapBirlestirmeEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapBirlestirmeGuncelle(HitapService):
    """
    Personelin hizmet birleştirme bilgilerinin Hitap üzerinde
    güncellemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapBirlestirmeGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapBirlestirmeSil(HitapService):
    """
    Personelin hizmet birleştirme bilgilerinin Hitap üzerinde
    silme işlemini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapBirlestirmeSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapBorclanmaGetir(HitapService):
    """
    Hitap üzerinden, personelin borçlanma bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapBorclanmaGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapBorclanmaSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki hizmet borçlanma bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapBorclanmaSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapBorclanmaEkle(HitapService):
    """
    Personelin hizmet borçlanma bilgilerinin Hitap'a
    eklemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapBorclanmaEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapBorclanmaGuncelle(HitapService):
    """
    Personelin hizmet borçlanma bilgilerinin Hitap üzerinde
    güncellemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapBorclanmaGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapBorclanmaSil(HitapService):
    """
    Personelin hizmet borçlanma bilgilerinin Hitap üzerinden
    silme işlemini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapBorclanmaSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapHizmetCetveliGetir(HitapService):
    """
    Hitap üzerinden, personelin hizmet kaydı bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapHizmetCetveliGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapHizmetCetveliSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki hizmet kaydı bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapHizmetCetveliSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapHizmetCetveliEkle(HitapService):
    """
    Personelin hizmet kaydı bilgilerinin Hitap'a
    eklemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapHizmetCetveliEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapHizmetCetveliGuncelle(HitapService):
    """
    Personelin hizmet kaydı bilgilerinin Hitap üzerinde
    güncellemesini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapHizmetCetveliGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapHizmetCetveliSil(HitapService):
    """
    Personelin hizmet kaydı bilgilerinin Hitap üzerinde
    silme işlemini yapar.

    Args:
      service_payload (dict): Servise gönderilecek olan veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapHizmetCetveliSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapIHSGetir(HitapService):
    """
    Hitap üzerinden, personelin itibari hizmet süresi zammı
    bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapIHSGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapIHSSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki itibari hizmet süresi zammı bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapIHSSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapIHSEkle(HitapService):
    """Hitap'a personelin itibari hizmet süresi zammı
    bilgisi ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapIHSEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapIHSGuncelle(HitapService):
    """Hitap üzerinde personelin itibari hizmet süresi zammı
    bilgilerini günceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapIHSGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapIHSSil(HitapService):
    """Hitap üzerinde personelin itibari hizmet süresi zammı
    bilgilerini siler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapIHSSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapIstisnaiIlgiGetir(HitapService):
    """
    Hitap üzerinden personelin istisnai ilgi
    bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapIstisnaiIlgiGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapIstisnaiIlgiSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki istisnai ilgi bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapIstisnaiIlgiSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapIstisnaiIlgiEkle(HitapService):
    """Hitap'a personelin istisnai ilgi bilgilerini ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapIstisnaiIlgiEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapIstisnaiIlgiGuncelle(HitapService):
    """Hitap üzerinde personelin istisnai ilgi bilgilerini
     günceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapIstisnaiIlgiGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapIstisnaiIlgiSil(HitapService):
    """Hitap üzerinde personelin istisnai ilgi bilgilerini siler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapIstisnaiIlgiSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapKursGetir(HitapService):
    """
    Hitap üzerinden, personelin kurs bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapKursGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapKursSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki kurs bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapKursSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapKursEkle(HitapService):
    """Hitap'a personelin kurs bilgilerini ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapKursEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapKursGuncelle(HitapService):
    """Personelin Hitap'taki kurs bilgilerini günceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapKursGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapKursSil(HitapService):
    """Personelin Hitap'taki kurs bilgilerini siler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapKursSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapMahkemeGetir(HitapService):
    """
    Hitap üzerinden, personelin mahkeme bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapMahkemeGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapMahkemeSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki mahkeme bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapMahkemeSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapMahkemeGuncelle(HitapService):
    """Personelin Hitap'taki mahkeme bilgilerini gunceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapMahkemeGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapMahkemeEkle(HitapService):
    """Personelin mahkeme bilgilerini Hitap'a ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapMahkemeEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapMahkemeSil(HitapService):
    """Personelin Hitap'taki mahkeme bilgilerini siler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapMahkemeSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapNufusGetir(HitapService):
    """
    Hitap üzerinden, personelin nüfus bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapNufusGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapNufusSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki nüfus bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapNufusSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapNufusEkle(HitapService):
    """Personelin nufus bilgilerini Hitap'a ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapNufusEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapNufusGuncelle(HitapService):
    """Personelin  Hitap'ta bulunan nufus bilgilerini gunceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapNufusGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapNufusSil(HitapService):
    pass


class HitapOkulGetir(HitapService):
    """
    Hitap üzerinden, personelin okul bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapOkulGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapOkulSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki okul bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapOkulSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapOkulEkle(HitapService):
    """Personelin okul bilgilerini Hitap'a ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapOkulEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapOkulGuncelle(HitapService):
    """Personelin Hitap'ta bulunan okul bilgilerini gunceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapOkulGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapOkulSil(HitapService):
    """Personelin Hitap'ta bulunan okul bilgilerini siler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapOkulSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapTazminatGetir(HitapService):
    """
    Hitap üzerinden, personelin tazminat bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapTazminatGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapTazminatSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki tazminat bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapTazminatSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapTazminatEkle(HitapService):
    """Personelin tazminat bilgilerini Hitap'a ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapTazminatEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapTazminatGuncelle(HitapService):
    """Personelin Hitap'ta bulunan tazminat bilgilerini günceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapTazminatGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapTazminatSil(HitapService):
    """Personelin Hitap'ta bulunan tazminat bilgilerini siler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapTazminatSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapUnvanGetir(HitapService):
    """
    Hitap üzerinden, personelin ünvan bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapUnvanGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapUnvanSenkronizeEt(HitapService):
    """
    Personelin Hitap'taki ünvan bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(HitapUnvanSenkronizeEt, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)


class HitapUnvanEkle(HitapService):
    """Personelin ünvan bilgilerini Hitap'a ekler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapUnvanEkle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapUnvanGuncelle(HitapService):
    """Personelin Hitap'ta bulunan ünvan bilgilerini günceller.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapUnvanGuncelle, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class HitapUnvanSil(HitapService):
    """Personelin Hitap'ta bulunan ünvan bilgilerini siler.

    Args:
      service_payload (dict): Servise gönderilecek veri

    Attributes:
        service_uri (str): İlgili Hitap servisinin adı
        payload (str): Servis verisi

    """

    def __init__(self, service_payload={}):
        super(HitapUnvanSil, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dump(service_payload)


class MernisKimlikBilgileriGetir(TcknService):
    """
    Personelin Mernis Kimlik bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili servisin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(MernisKimlikBilgileriGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)

    def rebuild_response(self, response_data):
        """
        Kimlik Bilgileri servisinden dönen datayı modellerimize uygun hale getirir.

        Args:
            response_data (dict): contains data returned from service

        Returns:
            response_data (dict): reformatted data compatible with our data models

        """
        ret = {}

        try:
            kb = response_data['KisiBilgisi']

            ret['tckn'] = kb['TCKimlikNo']
            ret['ad'] = kb['TemelBilgisi']['Ad']
            ret['soyad'] = kb['TemelBilgisi']['Soyad']
            ret['cinsiyet'] = kb['TemelBilgisi']['Cinsiyet']['Kod']
            ret['dogum_tarihi'] = '%s.%s.%s' % (
                kb['TemelBilgisi']['DogumTarih']['Gun'], kb['TemelBilgisi']['DogumTarih']['Ay'],
                kb['TemelBilgisi']['DogumTarih']['Yil'])
            ret['dogum_yeri'] = kb['TemelBilgisi']['DogumYer']
            ret['baba_adi'] = kb['TemelBilgisi']['BabaAd']
            ret['ana_adi'] = kb['TemelBilgisi']['AnneAd']
            ret['medeni_hali'] = kb['DurumBilgisi']['MedeniHal']['Kod']
            ret['kayitli_oldugu_il'] = kb['KayitYeriBilgisi']['Il']['Aciklama']
            ret['kayitli_oldugu_ilce'] = kb['KayitYeriBilgisi']['Ilce']['Aciklama']
            ret['kayitli_oldugu_mahalle_koy'] = kb['KayitYeriBilgisi']['Cilt']['Aciklama']
            ret['kayitli_oldugu_cilt_no'] = kb['KayitYeriBilgisi']['Cilt']['Kod']
            ret['kayitli_oldugu_aile_sira_no'] = kb['KayitYeriBilgisi']['AileSiraNo']
            ret['kayitli_oldugu_sira_no'] = kb['KayitYeriBilgisi']['BireySiraNo']
        except KeyError:
            ret['hata'] = True

        return ret


class MernisCuzdanBilgileriGetir(TcknService):
    """
    Personelin Mernis üzerinden nüfus cüzdanı bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili servisin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(MernisCuzdanBilgileriGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)

    def rebuild_response(self, response_data):
        """
        Mernis Cüzdan Bilgileri servisinden dönen datayı modellerimize uygun hale getirir.

        Args:
            response_data (dict): contains data returned from service

        Returns:
            response_data (dict): reformatted data compatible with our data models

        """
        ret = {}

        try:
            kb = response_data['CuzdanBilgisi']
            ret['tckn'] = kb['TCKimlikNo']
            ret['cuzdan_seri'] = kb['SeriNo'][0:3]
            ret['cuzdan_seri_no'] = kb['SeriNo'][3:]
            ret['kimlik_cuzdani_verildigi_yer'] = kb['VerildigiIlce']['b:Aciklama']
            ret['kimlik_cuzdani_verilis_nedeni'] = kb['CuzdanVerilmeNeden']['b:Aciklama']
            ret['kimlik_cuzdani_kayit_no'] = kb['KayitNo']
            ret['kimlik_cuzdani_verilis_tarihi'] = '%s.%s.%s' % (
                kb['VerilmeTarih']['b:Gun'], kb['VerilmeTarih']['b:Ay'],
                kb['VerilmeTarih']['b:Yil'])
        except KeyError:
            ret['hata'] = True

        return ret


class KPSAdresBilgileriGetir(TcknService):
    """
    Personelin KPS Adres bilgilerini sorgular.

    Args:
        tckn (str): Türkiye Cumhuriyeti Kimlik Numarası

    Attributes:
        service_uri (str): İlgili servisin adı
        payload (str): Servis verisi

    """

    def __init__(self, tckn=""):
        super(KPSAdresBilgileriGetir, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)

    def rebuild_response(self, response_data):
        """
        KPS Adres Bilgileri servisinden dönen datayı modellerimize uygun hale getirir.

        Args:
            response_data (dict): contains data returned from service

        Returns:
            response_data (dict): reformatted data compatible with our data models

        """
        ret = {}
        try:
            kb = response_data['KimlikNoileKisiAdresBilgileri']['YerlesimYeriAdresi']
            ret['ikamet_adresi'] = kb['AcikAdres']
            ret['ikamet_il'] = kb['IlIlceMerkezAdresi']['Il']
            ret['ikamet_ilce'] = kb['IlIlceMerkezAdresi']['Ilce']
        except KeyError:
            ret['hata'] = True

        return ret

class DersProgramiOlustur(ZatoService):
    """
    dp = DersProgramiOlustur(service_payload={"bolum": 123445})
    response = dp.zato_request()
    """

    def __init__(self, service_payload={}):
        super(ZatoService, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dumps(service_payload)


class SinavProgramiOlustur(ZatoService):
    """
    dp = SinavProgramiOlustur(service_payload={"bolum": 123445})
    response = dp.zato_request()
    """

    def __init__(self, service_payload={}):
        super(ZatoService, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dumps(service_payload)

class E_PostaYolla(ZatoService):
    def __init__(self, service_payload={}):
        super(ZatoService, self).__init__()
        self.service_uri = service_url_paths[self.__class__.__name__]["url"]
        self.payload = json.dumps(service_payload)

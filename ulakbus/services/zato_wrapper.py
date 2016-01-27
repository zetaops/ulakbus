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


from ulakbus import settings
import requests
import json
from zato_url_paths import service_url_paths


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

        return '/'.join([settings.ZATO_SERVER, self.service_uri])

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
                    return response['result']
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
    pass


class HitapAcikSureGuncelle(HitapService):
    pass


class HitapAcikSureSil(HitapService):
    pass


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
    pass


class HitapAskerlikGuncelle(HitapService):
    pass


class HitapAskerlikSil(HitapService):
    pass


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
    pass


class HitapBirlestirmeGuncelle(HitapService):
    pass


class HitapBirlestirmeSil(HitapService):
    pass


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
    pass


class HitapBorclanmaGuncelle(HitapService):
    pass


class HitapBorclanmaSil(HitapService):
    pass


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
    pass


class HitapHizmetCetveliGuncelle(HitapService):
    pass


class HitapHizmetCetveliSil(HitapService):
    pass


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
    pass


class HitapIHSGuncelle(HitapService):
    pass


class HitapIHSSil(HitapService):
    pass


class HitapIstisnaiIlgiGetir(HitapService):
    """
    Hitap üzerinden, personelin istisnai ilgi
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
    pass


class HitapIstisnaiIlgiGuncelle(HitapService):
    pass


class HitapIstisnaiIlgiSil(HitapService):
    pass


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
    pass


class HitapKursGuncelle(HitapService):
    pass


class HitapKursSil(HitapService):
    pass


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
    pass


class HitapMahkemeEkle(HitapService):
    pass


class HitapMahkemeSil(HitapService):
    pass


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
    pass


class HitapNufusGuncelle(HitapService):
    pass


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
    pass


class HitapOkulGuncelle(HitapService):
    pass


class HitapOkulSil(HitapService):
    pass


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
    pass


class HitapTazminatGuncelle(HitapService):
    pass


class HitapTazminatSil(HitapService):
    pass


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
    pass


class HitapUnvanGuncelle(HitapService):
    pass


class HitapUnvanSil(HitapService):
    pass


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

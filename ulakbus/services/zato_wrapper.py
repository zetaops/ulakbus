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
import importlib


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

    """

    payload = "{}"

    @staticmethod
    def get_uri(service_uri):
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

        return urlparse.urljoin(settings.ZATO_SERVER, service_uri)

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
        service_uri = service_url_paths[self.__class__.__name__]["url"]
        uri = self.get_uri(service_uri)
        payload = json.loads(self.payload)
        r = requests.post(uri, data=json.dumps(payload))
        if r.status_code == 200:
            response = r.json()
            r.close()
            try:
                if response['status'] == 'ok':
                    return self.rebuild_response(response)
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
                            "servers or service_uri changed" % service_uri)
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

    payload = "{}"

    def __init__(self, tckn=""):
        super(ZatoService, self).__init__()
        self.payload = '{"tckn":"%s"}' % self.check_turkish_identity_number(tckn)

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


class HitapService(ZatoService):

    payload = "{}"

    service_class_path = ''
    service_class_name = ''

    def __init__(self, kayit):
        module = importlib.import_module(self.service_class_path)
        model = getattr(module, self.service_class_name)

        self.payload = get_payload_object(model, kayit)


class HitapServiceError(Exception):
    pass


class HitapHizmetEkle(HitapService):
    pass


class HitapHizmetGuncelle(HitapService):
    pass


class HitapHizmetSil(HitapService):
    pass


class HitapHizmetSorgula(TcknService):
    pass


class HitapHizmetSync(TcknService):
    pass


class HitapAcikSureGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin açık süre hizmet bilgilerini sorgular.

    """

    pass


class HitapAcikSureSenkronizeEt(HitapHizmetGuncelle):
    """
    Personelin Hitap'taki açık süre hizmet bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapAcikSureEkle(HitapHizmetEkle):
    """
    Personelin açık süre hizmet bilgilerinin Hitap'a,
    eklemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_acik_sure_ekle'
    service_class_name = 'HizmetAcikSureEkle'


class HitapAcikSureGuncelle(HitapHizmetGuncelle):
    """
    Personelin açık süre hizmet bilgilerinin Hitap üzerinde
    guncellemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_acik_sure_guncelle'
    service_class_name = 'HizmetAcikSureGuncelle'


class HitapAcikSureSil(HitapHizmetSil):
    """
    Personelin açık süre hizmet bilgilerinin Hitap üzerinden
    silme işlemini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_acik_sure_sil'
    service_class_name = 'HizmetAcikSureSil'


class HitapAskerlikGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin askerlik bilgilerini sorgular.

    """
    pass


class HitapAskerlikSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki askerlik bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapAskerlikEkle(HitapHizmetEkle):
    """
    Personelin askerlik bilgilerinin Hitap'a eklemesini yapar.

    """

    service_class_path = 'ulakbus.services.personel.hitap.hizmet_askerlik_ekle'
    service_class_name = 'HizmetAskerlikEkle'


class HitapAskerlikGuncelle(HitapHizmetGuncelle):
    """
    Personelin askerlik bilgilerinin Hitap üzerinde
    guncellemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_askerlik_guncelle'
    service_class_name = 'HizmetAskerlikGuncelle'


class HitapAskerlikSil(HitapHizmetSil):
    """
    Personelin askerlik bilgilerinin Hitap üzerinden
    silme işlemini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_askerlik_sil'
    service_class_name = 'HizmetAskerlikSil'


class HitapBirlestirmeGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin hizmet birleştirme bilgilerini sorgular.

    """
    pass


class HitapBirlestirmeSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki hizmet birleştirme bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapBirlestirmeEkle(HitapHizmetEkle):
    """
    Personelin hizmet birleştirme bilgilerinin Hitap'a
    eklemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_birlestirme_ekle'
    service_class_name = 'HizmetBirlestirmeEkle'


class HitapBirlestirmeGuncelle(HitapHizmetGuncelle):
    """
    Personelin hizmet birleştirme bilgilerinin Hitap üzerinde
    güncellemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_birlestirme_guncelle'
    service_class_name = 'HizmetBirlestirmeGuncelle'


class HitapBirlestirmeSil(HitapHizmetSil):
    """
    Personelin hizmet birleştirme bilgilerinin Hitap üzerinde
    silme işlemini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_birlestirme_sil'
    service_class_name = 'HizmetBirlestirmeSil'


class HitapBorclanmaGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin borçlanma bilgilerini sorgular.

    """
    pass


class HitapBorclanmaSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki hizmet borçlanma bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapBorclanmaEkle(HitapHizmetEkle):
    """
    Personelin hizmet borçlanma bilgilerinin Hitap'a
    eklemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_borclanma_ekle'
    service_class_name = 'HizmetBorclanmaEkle'


class HitapBorclanmaGuncelle(HitapHizmetGuncelle):
    """
    Personelin hizmet borçlanma bilgilerinin Hitap üzerinde
    güncellemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_borclanma_guncelle'
    service_class_name = 'HizmetBorclanmaGuncelle'


class HitapBorclanmaSil(HitapHizmetSil):
    """
    Personelin hizmet borçlanma bilgilerinin Hitap üzerinden
    silme işlemini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_borclanma_sil'
    service_class_name = 'HizmetBorclanmaSil'


class HitapHizmetCetveliGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin hizmet kaydı bilgilerini sorgular.

    """
    pass


class HitapHizmetCetveliSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki hizmet kaydı bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapHizmetCetveliEkle(HitapHizmetEkle):
    """
    Personelin hizmet kaydı bilgilerinin Hitap'a
    eklemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_cetveli_ekle'
    service_class_name = 'HizmetCetveliEkle'


class HitapHizmetCetveliGuncelle(HitapHizmetGuncelle):
    """
    Personelin hizmet kaydı bilgilerinin Hitap üzerinde
    güncellemesini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_cetveli_guncelle'
    service_class_name = 'HizmetCetveliGuncelle'


class HitapHizmetCetveliSil(HitapHizmetSil):
    """
    Personelin hizmet kaydı bilgilerinin Hitap üzerinde
    silme işlemini yapar.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_cetveli_sil'
    service_class_name = 'HizmetCetvelSil'


class HitapIHSGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin itibari hizmet süresi zammı
    bilgilerini sorgular.

    """
    pass


class HitapIHSSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki itibari hizmet süresi zammı bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapIHSEkle(HitapHizmetEkle):
    """Hitap'a personelin itibari hizmet süresi zammı
    bilgisi ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_ihs_ekle'
    service_class_name = 'HizmetIHSEkle'


class HitapIHSGuncelle(HitapHizmetGuncelle):
    """Hitap üzerinde personelin itibari hizmet süresi zammı
    bilgilerini günceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_ihs_guncelle'
    service_class_name = 'HizmetIHSGuncelle'


class HitapIHSSil(HitapHizmetSil):
    """Hitap üzerinde personelin itibari hizmet süresi zammı
    bilgilerini siler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_ihs_sil'
    service_class_name = 'HizmetIHSSil'


class HitapIstisnaiIlgiGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden personelin istisnai ilgi
    bilgilerini sorgular.

    """
    pass


class HitapIstisnaiIlgiSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki istisnai ilgi bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapIstisnaiIlgiEkle(HitapHizmetEkle):
    """
    Hitap'a personelin istisnai ilgi bilgilerini ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_istisnai_ilgi_ekle'
    service_class_name = 'HizmetIstisnaiIlgiEkle'


class HitapIstisnaiIlgiGuncelle(HitapHizmetGuncelle):
    """
    Hitap üzerinde personelin istisnai ilgi bilgilerini
    günceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_istisnai_ilgi_guncelle'
    service_class_name = 'HizmetIstisnaiIlgiGuncelle'


class HitapIstisnaiIlgiSil(HitapHizmetSil):
    """
    Hitap üzerinde personelin istisnai ilgi bilgilerini siler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_istisnai_ilgi_sil'
    service_class_name = 'HizmetIstisnaiIlgiSil'


class HitapKursGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin kurs bilgilerini sorgular.

    """
    pass


class HitapKursSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki kurs bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapKursEkle(HitapHizmetEkle):
    """
    Hitap'a personelin kurs bilgilerini ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_kurs_ekle'
    service_class_name = 'HizmetKursEkle'


class HitapKursGuncelle(HitapHizmetGuncelle):
    """
    Personelin Hitap'taki kurs bilgilerini günceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_kurs_guncelle'
    service_class_name = 'HizmetKursGuncelle'


class HitapKursSil(HitapHizmetSil):
    """
    Personelin Hitap'taki kurs bilgilerini siler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_kurs_sil'
    service_class_name = 'HizmetKursSil'


class HitapMahkemeGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin mahkeme bilgilerini sorgular.

    """
    pass


class HitapMahkemeSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki mahkeme bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapMahkemeGuncelle(HitapHizmetGuncelle):
    """
    Personelin Hitap'taki mahkeme bilgilerini gunceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_mahkeme_guncelle'
    service_class_name = 'HizmetMahkemeGuncelle'


class HitapMahkemeEkle(HitapHizmetEkle):
    """
    Personelin mahkeme bilgilerini Hitap'a ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_mahkeme_ekle'
    service_class_name = 'HizmetMahkemeEkle'


class HitapMahkemeSil(HitapHizmetSil):
    """
    Personelin Hitap'taki mahkeme bilgilerini siler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_mahkeme_sil'
    service_class_name = 'HizmetMahkemeSil'


class HitapNufusGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin nüfus bilgilerini sorgular.

    """
    pass


class HitapNufusSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki nüfus bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapNufusEkle(HitapHizmetEkle):
    """
    Personelin nufus bilgilerini Hitap'a ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_nufus_ekle'
    service_class_name = 'HizmetNufusEkle'


class HitapNufusGuncelle(HitapHizmetGuncelle):
    """
    Personelin  Hitap'ta bulunan nufus bilgilerini gunceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_nufus_guncelle'
    service_class_name = 'HizmetNufusGuncelle'


class HitapNufusSil(HitapHizmetSil):
    pass


class HitapOkulGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin okul bilgilerini sorgular.

    """
    pass


class HitapOkulSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki okul bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapOkulEkle(HitapHizmetEkle):
    """
    Personelin okul bilgilerini Hitap'a ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_okul_ekle'
    service_class_name = 'HizmetOkulEkle'


class HitapOkulGuncelle(HitapHizmetGuncelle):
    """
    Personelin Hitap'ta bulunan okul bilgilerini gunceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_okul_guncelle'
    service_class_name = 'HizmetOkulGuncelle'


class HitapOkulSil(HitapHizmetSil):
    """
    Personelin Hitap'ta bulunan okul bilgilerini siler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_okul_sil'
    service_class_name = 'HizmetOkulSil'


class HitapTazminatGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin tazminat bilgilerini sorgular.

    """
    pass


class HitapTazminatSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki tazminat bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapTazminatEkle(HitapHizmetEkle):
    """
    Personelin tazminat bilgilerini Hitap'a ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_tazminat_ekle'
    service_class_name = 'HizmetTazminatEkle'


class HitapTazminatGuncelle(HitapHizmetGuncelle):
    """
    Personelin Hitap'ta bulunan tazminat bilgilerini günceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_tazminat_guncelle'
    service_class_name = 'HizmetTazminatGuncelle'


class HitapTazminatSil(HitapHizmetSil):
    """
    Personelin Hitap'ta bulunan tazminat bilgilerini siler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_tazminat_sil'
    service_class_name = 'HizmetTazminatSil'


class HitapUnvanGetir(HitapHizmetSorgula):
    """
    Hitap üzerinden, personelin ünvan bilgilerini sorgular.

    """
    pass


class HitapUnvanSenkronizeEt(HitapHizmetSync):
    """
    Personelin Hitap'taki ünvan bilgilerinin,
    yereldeki kayıtlarla senkronizasyonunu yapar.

    """
    pass


class HitapUnvanEkle(HitapHizmetEkle):
    """
    Personelin ünvan bilgilerini Hitap'a ekler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_unvan_ekle'
    service_class_name = 'HizmetUnvanEkle'


class HitapUnvanGuncelle(HitapHizmetGuncelle):
    """
    Personelin Hitap'ta bulunan ünvan bilgilerini günceller.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_unvan_guncelle'
    service_class_name = 'HizmetUnvanGuncelle'


class HitapUnvanSil(HitapHizmetSil):
    """
    Personelin Hitap'ta bulunan ünvan bilgilerini siler.

    """
    service_class_path = 'ulakbus.services.personel.hitap.hizmet_unvan_sil'
    service_class_name = 'HizmetUnvanSil'


class MernisKimlikBilgileriGetir(TcknService):
    """
    Personelin Mernis Kimlik bilgilerini sorgular.

    """

    def rebuild_response(self, response_data):
        """
        Kimlik Bilgileri servisinden dönen datayı modellerimize uygun hale getirir.

        Args:
            response_data (dict): contains data returned from service

        Returns:
            response_data (dict): reformatted data compatible with our data models

        """
        response_data = response_data['result']
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

    """

    def rebuild_response(self, response_data):
        """
        Mernis Cüzdan Bilgileri servisinden dönen datayı modellerimize uygun hale getirir.

        Args:
            response_data (dict): contains data returned from service

        Returns:
            response_data (dict): reformatted data compatible with our data models

        """
        response_data = response_data['result']
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

    """

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

    # def __init__(self, kayit):
    #     super(ZatoService, self).__init__()
    #
    #     self.payload = json.dumps(service_payload)
    pass


class SinavProgramiOlustur(ZatoService):
    """
    dp = SinavProgramiOlustur(service_payload={"bolum": 123445})
    response = dp.zato_request()

    """
    #
    # def __init__(self, kayit):
    #     super(ZatoService, self).__init__()
    #
    #     self.payload = json.dumps(service_payload)
    pass


class EPostaYolla(ZatoService):
    # def __init__(self, kayit):
    #     super(ZatoService, self).__init__()
    #
    #     self.payload = json.dumps(service_payload)
    pass


def get_payload_object(hitap_model, kayit):
    import datetime

    payload_object = dict()

    for key in hitap_model.service_dict['fields'].values():

        if isinstance(kayit, dict):
            value = kayit[key]
        else:
            value = getattr(kayit, key)
            if type(value) == datetime.date:
                value = value.strftime("%d.%m.%Y")

        payload_object[key] = value

    payload = json.dumps(payload_object)
    return payload

# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Personellerin  Kimlik ve İletişim  Bilgileri  İş Akışına ait
sınıf ve metotları içeren modüldür.

Kimlik ve İletişim Bilgileri iş akışının yürütülmesini sağlar.

"""

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.lib.translation import gettext as _, gettext_lazy

from zengine.views.crud import CrudView
from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir
from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir


class KimlikBilgileriForm(JsonForm):
    """
    ``KimlikIletişim`` sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ['tckn', 'ad', 'soyad', 'cinsiyet', 'uyruk', 'medeni_hali', 'cuzdan_seri',
                   'cuzdan_seri_no', 'baba_adi', 'ana_adi', 'dogum_tarihi', 'dogum_tarihi',
                   'dogum_yeri', 'medeni_hali', 'kayitli_oldugu_il', 'kayitli_oldugu_ilce',
                   'kayitli_oldugu_mahalle_koy',
                   'kayitli_oldugu_cilt_no', 'kayitli_oldugu_aile_sira_no',
                   'kayitli_oldugu_sira_no',
                   'kimlik_cuzdani_verildigi_yer', 'kimlik_cuzdani_verilis_nedeni',
                   'kimlik_cuzdani_kayit_no',
                   'kimlik_cuzdani_verilis_tarihi']

    kaydet = fields.Button(gettext_lazy(u"Kaydet"), cmd="save")
    mernis = fields.Button(gettext_lazy(u"Mernis'ten Kimlik Bilgileri Getir"), cmd="mernis_kimlik_sorgula")


class IletisimBilgileriForm(JsonForm):
    """
    ``KimlikIletisim`` sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ['ikamet_adresi', 'ikamet_il', 'ikamet_ilce', 'adres_2', 'adres_2_posta_kodu',
                   'oda_no', 'oda_tel_no', 'cep_telefonu', 'e_posta', 'e_posta_2', 'e_posta_3',
                   'web_sitesi']

    kaydet = fields.Button(gettext_lazy(u"Kaydet"), cmd="save")
    kps = fields.Button(gettext_lazy(u"KPS'den Adres Bilgileri Getir"), cmd="kps_adres_sorgula")


class DigerBilgilerForm(JsonForm):
    """
    ``KimlikIletisim`` sınıfı için form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ['yayinlar', 'projeler', 'verdigi_dersler', 'kan_grubu', 'ehliyet',
                   'unvan', 'biyografi', 'notlar', 'engelli_durumu', 'engel_grubu',
                   'engel_derecesi', 'engel_orani', 'personel_turu']

    kaydet = fields.Button(gettext_lazy(u"Kaydet"), cmd="save")


class KimlikIletisim(CrudView):
    """Kimlik ve İletişim Bilgileri İş Akışı

    Kimlik ve İletişim Bilgileri, aşağıda tanımlı iş akışı adımlarını yürütür:

        - Kimlik Bilgileri Formu
        - Mernis Kimlik Sorgulama
        - Kimlik Bilgileri Kaydet
        - İletişim Bilgileri Formu
        - KPS Adres Sorgulama
        - Iletişim Bilgileri Kaydet
        - Diğer Bilgiler Formu
        - Diğer Bilgileri Kaydet

    Bu iş akışında kullanılan metotlar şu şekildedir:

    Kimlik Bilgilerini Formunu Listele:
       CrudView list metodu kullanılmıştır. Bu metot default olarak tanımlanmıştır.
       Kimlik Bilgileri formunu listeler.

    Mernis'ten Kimlik Bilgileri Getir:
       MERNİS, merkezi nüfus idare sisteminin kısa proje adıdır. Bu metot sayesinde
       personele ait kimlik bilgilerine MERNİS'ten erişilir. Kimlik Bilgileri formundaki
       alanlar MERNİS'ten gelen bilgiler doğrultusunda doldurulur.

    Kaydet:
       MERNİS'ten gelen bilgileri ve yetkili kişinin personelle girdiği bilgileri
       kaydeder. Bu adım ``CrudView.save()`` metodunu kullanır.

    İletişim Bilgilerini Formunu Listele:
       CrudView list metodu kullanılmıştır.Bu metot default olarak tanımlanmıştır.
       İletişim Bilgileri formunu listeler.

    KPS'den Adres Bilgileri Getir:
       Bu metot sayesinde personele ait yerleşim yeri bilgilerine kamu kurumları
       tarafından erişilir. İletişim Bilgileri formundaki alanlar
       KPS'ten gelen bilgiler doğrultusunda doldurulur.

    Kaydet:
       KPS'ten gelen bilgileri ya da yetkili kişinin personelle ilgili girdiği
       bilgileri kaydeder. Bu adım ``CrudView.save()`` metodunu kullanır.

    Diğer Bilgiler Formu:
       CrudView list metodu kullanılmıştır.Bu metot default olarak tanımlanmıştır.
       Diğer Bilgiler formunu listeler.

    Kaydet:
       Yetkili kişinin personelle ilgili girdiği bilgileri kaydeder.
       İş akışı adımdan sonra sona eriyor.

    Bu sınıf ``CrudView`` extend edilerek hazırlanmıştır. Temel model ``Personel``
    modelidir. Meta.model bu amaçla kullanılmıştır.

    Adımlar arası geçiş manuel yürütülmektedir.

    """

    class Meta:
        model = 'Personel'

    def mernis_kimlik_sorgula(self):
        """Mernis Sorgulama

        Zato wrapper metodlarıyla Mernis servisine bağlanır, servisten dönen
        değerlerle nesneyi doldurup kaydeder.

        """

        zs = MernisKimlikBilgileriGetir(tckn=self.object.tckn)
        response = zs.zato_request()
        self.object(**response)
        self.object.save()

    def kps_adres_sorgula(self):
        """KPS Sorgulama

        Zato wrapper metodlarıyla KPS servisine bağlanır, servisten dönen
        değerlerle nesneyi doldurup kaydeder.

        """

        zs = KPSAdresBilgileriGetir(tckn=self.object.tckn)
        response = zs.zato_request()
        self.object(**response)
        self.object.save()

    def kimlik_bilgileri(self):
        """Kimlik Bilgileri Formu"""

        self.form_out(KimlikBilgileriForm(self.object, current=self.current))

    def iletisim_bilgileri(self):
        """İletişim Bilgileri Formu"""

        self.form_out(IletisimBilgileriForm(self.object, current=self.current))

    def diger_bilgiler(self):
        """Diğer Bilgiler Formu"""

        self.form_out(DigerBilgilerForm(self.object, current=self.current))

# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""
Kimlik ve  İletişim Bilgileri işlemleri için kullanacağımız temel model ``Personel`` modelidir.
Meta.model bu amaçla kullanılmıştır.

İş akışında, ``CrudView`` genişletilerek (extend) işletilmektedir. Adımlar arası geçiş manuel sekilde
yürütülmektedir.



"""
from zengine.forms import JsonForm
from zengine.forms import fields

from zengine.views.crud import CrudView
from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir
from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir


class KimlikBilgileriForm(JsonForm):
    """
    Kimlikİletişim için object form olarak kullanılacaktır. Form, include listesindeki
    alanlara sahiptir.

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

    kaydet = fields.Button("Kaydet", cmd="save")
    mernis = fields.Button("Mernis'ten Kimlik Bilgileri Getir", cmd="mernis_kimlik_sorgula")


class IletisimBilgileriForm(JsonForm):
    """
    Kimlikİletişim için object form olarak kullanılacaktır. Form, include listesindeki
    alanlara sahiptir.

    """
    class Meta:
        include = ['ikamet_adresi', 'ikamet_il', 'ikamet_ilce', 'adres_2', 'adres_2_posta_kodu',
                   'oda_no', 'oda_tel_no', 'cep_telefonu', 'e_posta', 'e_posta_2', 'e_posta_3',
                   'web_sitesi']

    kaydet = fields.Button("Kaydet", cmd="save")
    kps = fields.Button("KPS'den Adres Bilgileri Getir", cmd="kps_adres_sorgula")


class DigerBilgilerForm(JsonForm):
    """
    Kimlikİletişim için object form olarak kullanılacaktır. Form, include listesindeki
    alanlara sahiptir.

    """
    class Meta:
        include = ['yayinlar', 'projeler', 'verdigi_dersler', 'kan_grubu', 'ehliyet',
                   'unvan', 'biyografi', 'notlar', 'engelli_durumu', 'engel_grubu',
                   'engel_derecesi', 'engel_orani', 'personel_turu']

    kaydet = fields.Button("Kaydet", cmd="save")


class KimlikIletisim(CrudView):
    """
    Kimlik ve İletişim Bilgileri, aşağıda tanımlı iş akışı adımlarını yürütür.

    - Kimlik Bilgileri Formu
    - Mernis Kimlik Sorgulama
    - Kimlik Bilgileri Kaydet
    - İletişim Bilgileri Formu
    - KPS Adres Sorgulama
    - Iletişim Bilgileri Kaydet

    Bu iş akışında kullanılan metotlar şu şekildedir:

    Kimlik ve İletişim Bilgilerini Listele:
       CrudView list metodu kullanılmıştır. Kimlik Bilgileri formunu listeler.

    Mernis'ten Kimlik Bilgileri Getir:
       MERNİS, merkezi nüfus idare sisteminin kısa proje adıdır. Bu sistem ile nüfus kayıtları bilgisayar ortamına
       aktarılarak veritabanları  oluşturulmuştur. Bu metot ile personele ait kimlik bilgilerine kamu kurumları
       tarafından MERNIS'ten erişilir.


    KPS'den Adres Bilgileri Getir:
       Bu metot ile, Nüfus ve Vatandaşlık İşleri Genel Müdürlüğü tarafından kaydı tutulan kişiye ait nüfus
       ve yerleşim yeri bilgilerine (merkezi veritabanında tutulan verilere) kamu kurumları tarafından erişilir.


    Kaydet:
       MERNİS'ten, KPS'ten gelen bilgileri ve yetkili kişinin girdiği bilgileri kaydeder. İş akışı bu metottan
       sonra sona eriyor.

    """
    class Meta:
        model = 'Personel'

    def mernis_kimlik_sorgula(self):
        zs = MernisKimlikBilgileriGetir(tckn=self.object.tckn)
        response = zs.zato_request()
        self.object(**response)
        self.object.save()

    def kps_adres_sorgula(self):
        zs = KPSAdresBilgileriGetir(tckn=self.object.tckn)
        response = zs.zato_request()
        self.object(**response)
        self.object.save()

    def kimlik_bilgileri(self):
        self.form_out(KimlikBilgileriForm(self.object, current=self.current))

    def iletisim_bilgileri(self):
        self.form_out(IletisimBilgileriForm(self.object, current=self.current))

    def diger_bilgiler(self):
        self.form_out(DigerBilgilerForm(self.object, current=self.current))

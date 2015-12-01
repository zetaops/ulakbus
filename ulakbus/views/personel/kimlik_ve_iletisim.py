# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Kimlik ve Iletisim Bilgileri WF adimlarini yurutur. WF 6 adimdan olusmaktadir.
#
# 1- Kimlik Bilgileri Formu
# 2- Mernis Kimlik Sorgulama
# 3- Kimlik Bilgileri Kaydet
# 4- Ileitisim Bilgileri Formu
# 5- KPS Adres Sorgulama
# 6- Iletisim Bilgileri Kaydet
#
# Bu WF, CrudView extend edilerek isletilmektedir. Adimlar arasi dispatch manuel sekilde yurutulmektedir.
# Her adim basina kullanilan metodlar su sekildedir:
#
from zengine.lib.forms import JsonForm

from zengine.views.crud import CrudView
from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir
from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir
from pyoko import form


class KimlikBilgileriForm(JsonForm):
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

    kaydet = form.Button("Kaydet", cmd="save")
    mernis = form.Button("Mernis'ten Kimlik Bilgileri Getir", cmd="mernis_kimlik_sorgula")


class IletisimBilgileriForm(JsonForm):
    class Meta:
        include = ['ikamet_adresi', 'ikamet_il', 'ikamet_ilce', 'adres_2', 'adres_2_posta_kodu',
                   'oda_no', 'oda_tel_no', 'cep_telefonu', 'e_posta', 'e_posta_2', 'e_posta_3',
                   'web_sitesi']

    kaydet = form.Button("Kaydet", cmd="save")
    kps = form.Button("KPS'den Adres Bilgileri Getir", cmd="kps_adres_sorgula")


class DigerBilgilerForm(JsonForm):
    class Meta:
        include = ['yayinlar', 'projeler', 'verdigi_dersler', 'kan_grubu', 'ehliyet',
                   'unvan', 'biyografi', 'notlar', 'engelli_durumu', 'engel_grubu',
                   'engel_derecesi', 'engel_orani', 'personel_turu']

    kaydet = form.Button("Kaydet", cmd="save")


class KimlikIletisim(CrudView):
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

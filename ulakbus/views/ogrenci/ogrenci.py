# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from collections import OrderedDict
from zengine.forms import fields
from zengine import forms
from zengine.views.crud import CrudView
from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir
from ulakbus.services.zato_wrapper import KPSAdresBilgileriGetir
from ulakbus.models.ogrenci import Ogrenci


class KimlikBilgileriForm(forms.JsonForm):
    class Meta:
        include = ['tckn', "ad", "soyad", "cinsiyet", "dogum_tarihi", "dogum_yeri", "uyruk",
                   "medeni_hali", "baba_adi", "ana_adi",
                   "cuzdan_seri", "cuzdan_seri_no", "kayitli_oldugu_il", "kayitli_oldugu_ilce",
                   "kayitli_oldugu_mahalle_koy",
                   "kayitli_oldugu_cilt_no", "kayitli_oldugu_aile_sıra_no",
                   "kayitli_oldugu_sira_no", "kimlik_cuzdani_verildigi_yer",
                   "kimlik_cuzdani_verilis_nedeni", "kimlik_cuzdani_kayit_no",
                   "kimlik_cuzdani_verilis_tarihi"]

    kaydet = fields.Button("Kaydet", cmd="save")
    mernis_sorgula = fields.Button("Mernis Sorgula", cmd="mernis_sorgula")


class KimlikBilgileri(CrudView):
    class Meta:
        model = "Ogrenci"

    def kimlik_bilgileri(self):
        self.form_out(KimlikBilgileriForm(self.object, current=self.current))

    def mernis_sorgula(self):
        servis = MernisKimlikBilgileriGetir(tckn=self.object.tckn)
        kimlik_bilgisi = servis.zato_request()
        self.object(**kimlik_bilgisi)
        self.object.save()


class IletisimBilgileriForm(forms.JsonForm):
    class Meta:
        include = ["ikamet_il", "ikamet_ilce", "ikamet_adresi", "posta_kodu", "eposta", "tel_no"]

    kaydet = fields.Button("Kaydet", cmd="save")
    kps_sorgula = fields.Button("KPS Sorgula", cmd="kps_sorgula")


class IletisimBilgileri(CrudView):
    class Meta:
        model = "Ogrenci"

    def iletisim_bilgileri(self):
        self.form_out(IletisimBilgileriForm(self.object, current=self.current))

    def kps_sorgula(self):
        servis = KPSAdresBilgileriGetir(tckn=self.object.tckn)
        iletisim_bilgisi = servis.zato_request()
        self.object(**iletisim_bilgisi)
        self.object.save()


class OncekiEgitimBilgileriForm(forms.JsonForm):
    class Meta:
        include = ["okul_adi", "diploma_notu", "mezuniyet_yili"]

    kaydet = fields.Button("Kaydet", cmd="save")


class OncekiEgitimBilgileri(CrudView):
    class Meta:
        model = "OncekiEgitimBilgisi"

    def onceki_egitim_bilgileri(self):
        self.form_out(OncekiEgitimBilgileriForm(self.object, current=self.current))


def ogrenci_bilgileri(current):
    current.output['client_cmd'] = ['show', ]
    ogrenci = Ogrenci.objects.get(user_id=current.user_id)

    # ordered tablo ornegi
    kimlik_bilgileri = OrderedDict({})
    kimlik_bilgileri.update({'Ad Soyad': "%s %s" % (ogrenci.ad, ogrenci.soyad)})
    kimlik_bilgileri.update({'Cinsiyet': ogrenci.cinsiyet})
    kimlik_bilgileri.update({'Kimlik No': ogrenci.tckn})
    kimlik_bilgileri.update({'Uyruk': ogrenci.tckn})
    kimlik_bilgileri.update({'Doğum Tarihi': '{:%d.%m.%Y}'.format(ogrenci.dogum_tarihi)})
    kimlik_bilgileri.update({'Doğum Yeri': ogrenci.dogum_yeri})
    kimlik_bilgileri.update({'Baba Adı': ogrenci.baba_adi})
    kimlik_bilgileri.update({'Anne Adı': ogrenci.ana_adi})
    kimlik_bilgileri.update({'Medeni Hali': ogrenci.medeni_hali})

    # unordered tablo ornegi
    iletisim_bilgileri = {
        'Eposta': ogrenci.e_posta,
        'Telefon': ogrenci.tel_no,
        'Sitem Kullanıcı Adı': current.user.username
    }

    current.output['object'] = [
        {
            "title": "Kimlik Bilgileri",
            "type": "table",
            "fields": kimlik_bilgileri
        },
        {
            "title": "İletişim Bilgileri",
            "type": "table",
            "fields": iletisim_bilgileri
        }
    ]

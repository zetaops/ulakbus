# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.

from pyoko.model import field
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.base import SimpleView
from ulakbus.models.personel import Kadro


# Views
class YeniPersonelEkle(SimpleView):
    def show_view(self):
        self.current.output['forms'] = YeniPersonelTcknForm().serialize()


class KimlikBilgileri(SimpleView):
    def show_view(self):
        form = KimlikBilgileriForm()
        form.ad = self.current.input['kimlik_bilgileri']['ad']
        form.ad = self.current.input['kimlik_bilgileri']['soyad']
        form.ad = self.current.input['kimlik_bilgileri']['tckn']
        form.ad = self.current.input['kimlik_bilgileri']['dogum_yeri']
        form.ad = self.current.input['kimlik_bilgileri']['dogum_tarihi']
        self.current.output['forms'] = form.serialize()

    def do_view(self):
        from ulakbus.models.personel import Personel
        yeni_personel = Personel()
        yeni_personel.tckn = self.current.input['form']['tckn']

        nufus_kayitlari = yeni_personel.NufusKayitlari()
        nufus_kayitlari.ad = self.current.input['form']['ad']
        nufus_kayitlari.soyad = self.current.input['form']['soyad']
        nufus_kayitlari.dogum_tarihi = self.current.input['form']['dogum_tarihi']
        yeni_personel.save()

        self.current['task_data']['tckn'] = self.current.input['form']['tckn']


class IletisimveEngelliDurumBilgileri(SimpleView):
    def show_view(self):
        mernis_adres = mernis_adres_bilgileri_getir(self.current.input['tckn'])
        form = IletisimveEngelliDurumBilgileriForm()
        form.ikamet_adresi = mernis_adres['adres']
        form.il = mernis_adres['il']
        form.ilce = mernis_adres['ilce']
        self.current.output['forms'] = form.serialize()

    def do_view(self):
        pass


class Atama(SimpleView):
    def show_view(self):
        pass

    def do_view(self):
        pass


def mernis_kimlik_bilgileri_getir(current):
    tckn = current.input['tckn']
    # mernis servisi henuz hazir degil
    # from ulakbus.services.zato_wrapper import MernisKimlikBilgileriGetir
    # mernis_bilgileri = MernisKimlikBilgileriGetir(tckn=tckn)
    # response = mernis_bilgileri.zato_request()
    # bu sebeple response elle olusturuyoruz.

    response = {"ad": "Kamil", "soyad": "Soylu", "tckn": "12345678900", "dogum_yeri": "Afyon",
                "dogum_tarihi": "10.10.1940"}
    current.task_data['mernis_tamam'] = True
    current.task_data['kimlik_bilgileri'] = response

    current.set_message(title='%s TC no için Hitap servisi başlatıldı' % tckn,
                        msg='', typ=1, url="/wftoken/%s" % current.token)


def mernis_adres_bilgileri_getir(tckn):
    # mernis servisi henuz hazir degil
    # from ulakbus.services.zato_wrapper import MernisAdresBilgileriGetir
    # mernis_bilgileri = MernisAdresBilgileriGetir(tckn=tckn)
    # response = mernis_bilgileri.zato_request()
    # bu sebeple response elle olusturuyoruz.

    response = {"il": "Konya", "ilce": "Meram", "adres": "Meram Caddesi No4 Meram Konya"}
    return response


# Formlar
class YeniPersonelTcknForm(JsonForm):
    class Meta:
        title = 'Yeni Personel Ekle'
        help_text = "Kimlik Numarası ile MERNIS ve HITAP bilgileri getir."

    tcno = field.String("TC No")
    cmd = field.String("Bilgileri Getir", type="button")


class KimlikBilgileriForm(JsonForm):
    class Meta:
        title = 'Yeni Personel Ekle'
        help_text = "Kimlik Numarası ile MERNIS ve HITAP bilgileri getir."

    tckn = field.String("TC No")
    ad = field.String("Adı")
    soyad = field.String("Soyadı")
    cinsiyet = field.String("Cinsiyet")
    uyruk = field.String("Uyruk")
    cuzdan_seri = field.String("Seri")
    cuzdan_seri_no = field.String("Seri No")
    baba_adi = field.String("Ana Adi")
    ana_adi = field.String("Baba Adi")
    dogum_tarihi = field.Date("Doğum Tarihi")
    dogum_yeri = field.String("Doğum Yeri")
    medeni_hali = field.String("Medeni Hali")
    kayitli_oldugu_il = field.String("Il", )
    kayitli_oldugu_ilce = field.String("Ilce")
    kayitli_oldugu_mahalle_koy = field.String("Mahalle/Koy")
    kayitli_oldugu_cilt_no = field.String("Cilt No")
    kayitli_oldugu_aile_sira_no = field.String("Aile Sira No")
    kayitli_oldugu_sira_no = field.String("Sira No")
    kimlik_cuzdani_verildigi_yer = field.String("Cuzdanin Verildigi Yer")
    kimlik_cuzdani_verilis_nedeni = field.String("Cuzdanin Verilis Nedeni")
    kimlik_cuzdani_kayit_no = field.String("Cuzdan Kayit No")
    kimlik_cuzdani_verilis_tarihi = field.String("Cuzdan Kayit Tarihi")
    cmd = fields.Button("Kaydet")


class IletisimveEngelliDurumBilgileriForm(JsonForm):
    class Meta:
        title = 'Iletisim Bilgileri'
        help_text = "Yeni Personelin Iletisim Bilgilerini Duzenle."

    ikamet_il = field.String("İkamet Il")
    ikamet_ilce = field.String("İkamet Ilce")
    ikamet_adresi = field.String("İkamet Adresi")
    adres_2 = field.String("Adres 2")
    adres_2_posta_kodu = field.String("Adres 2 Posta Kodu", index=True)
    oda_tel_no = field.String("Oda Telefon Numarası")
    cep_telefonu = field.String("Cep Telefonu")
    e_posta = field.String("E-Posta")
    e_posta_2 = field.String("E-Posta")
    e_posta_3 = field.String("E-Posta")
    web_sitesi = field.String("Web Sitesi")
    notlar = field.Text("Not")
    engelli_durumu = field.String("Engellilik")
    engel_grubu = field.String("Engel Grubu")
    engel_derecesi = field.String("Engel Derecesi")
    engel_orani = field.Integer("Engellilik Orani")

    # getir = field.String("Adres Bilgileri Getir")
    cmd = field.String("Kaydet")


class AtamaForm(JsonForm):
    class Meta:
        title = 'Iletisim Bilgileri'
        help_text = "Yeni Personelin Iletisim Bilgilerini Duzenle."

    kurum_sicil_no = field.String("Kurum Sicil No")
    personel_tip = field.Integer("Personel Tip")
    hizmet_sinifi = field.Integer("Hizmet Sinifi")
    emekli_sicil_no = field.String("Emekli Sicil No")
    emekli_giris_tarihi = field.String("Emekli Giris Tarihi")
    statu = field.String("Statu")
    brans = field.String("Brans")
    birim = field.String("birim")

    kurumda_ise_baslama_tarihi = field.String("Tarih")
    kurumda_ise_baslama_durumu = field.String("Durum")

    calistigi_birimde_ise_baslama_tarihi = field.String("Calistigi Birimde Ise Baslama Tarihi")
    calistigi_birimde_ise_baslama_ibraz_tarihi = field.String("Ibraz Tarihi")
    calistigi_birimde_ise_baslama_durum = field.String("Durum")
    calistigi_birimde_ise_baslama_aciklama = field.String("Aciklama")
    calistigi_birimde_ise_baslama_nereden = field.String("Nereden")
    calistigi_birimde_ise_baslama_mecburi_hizmet = field.String("Mecburi Hizmet Tarihi")

    gorev_suresi_baslama = field.Date("Gorev Suresi Baslama Tarihi")
    gorev_suresi_bitis = field.Date("Bitis Tarihi")
    gorev_suresi_aciklama = field.String("Aciklama")

    atama_yapilan_kadro = Kadro("Kadro")
    atama_yapilan_kadro_tarih = field.Date("Kadro Tarih")
    atama_yapilan_kadro_derece = field.Integer("Kadro Derece")
    atama_yapilan_kadro_derece_tarih = field.Date("Kadro Derece Tarih")
    atama_yapilan_kadro_unvan = field.String("Kadro Unvan")
    atama_yapilan_kadro_unvan_tarih = field.String("Kadro Unvan Tarih")

    atama_gorev_ayligi_derece = field.String("Derce")
    atama_gorev_ayligi_kademe = field.String("Kademe")
    atama_gorev_ayligi_ek_gosterge = field.String("Ek Gosterge")
    atama_gorev_ayligi_terfi_tarihi = field.String("Terfi Tarihi")

    atama_kazanilmis_hak_ayligi_derece = field.String("Derece")
    atama_kazanilmis_hak_ayligi_kademe = field.String("Kademe")
    atama_kazanilmis_hak_ayligi_ek_gosterge = field.String("Ek Gosterge")
    atama_kazanilmis_hak_ayligi_terfi_tarihi = field.String("Terfi Tarihi")

    atama_emekli_muk_derece = field.String("İkamet Il")
    atama_emekli_muk_kademe = field.String("İkamet Il")
    atama_emekli_muk_ek_gosterge = field.String("İkamet Il")
    atama_emekli_muk_terfi_tarihi = field.String("İkamet Il")

    cmd = fields.Button("Kaydet")

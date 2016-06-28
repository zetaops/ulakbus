# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

"""
    Görevlendirme

    İki tür görevlendirme vardır.
    - Kurum içi görevlendirme
    - Kurum dışı görevlendirme

    Bu iş akışı CrudView nesnesi extend edilerek işletilmektedir.
"""

from pyoko.exceptions import ObjectDoesNotExist
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView, obj_filter
from pyoko import ListNode
from ulakbus.models import AbstractRole, Unit, Personel
from ulakbus.models import KurumDisiGorevlendirmeBilgileri, KurumIciGorevlendirmeBilgileri

class GorevlendirmeTurSecForm(JsonForm):
    gorevlendirme_tur = fields.Integer("Görevlendirme Tür", choices="gorev_tipi")
    kaydet_buton = fields.Button("Kaydet ve Devam Et", cmd="gorevlendirme_tur_kaydet")

class KurumIciGorevlendirmeForm(JsonForm):
    goreve_baslama_tarihi = fields.Date("Göreve Başlama Tarihi")
    gorev_bitis_tarihi = fields.Date("Görev Bitiş Tarihi")
    birim = Unit()
    soyut_rol = AbstractRole()
    aciklama = fields.Text("Açıklama")
    resmi_yazi_sayi = fields.String("Resmi Yazı Sayı")
    resmi_yazi_tarih = fields.Date("Resmi Yazı Tarih")
    kaydet_buton = fields.Button("Kaydet ve Devam Et", cmd="kaydet")

class KurumDisiGorevlendirmeForm(JsonForm):
    goreve_baslama_tarihi = fields.Date("Göreve Başlama Tarihi")
    gorev_bitis_tarihi = fields.Date("Görev Bitiş Tarihi")
    aciklama = fields.Text("Açıklama")
    resmi_yazi_sayi = fields.String("Resmi Yazı Sayı")
    resmi_yazi_tarih = fields.Date("Resmi Yazı Tarih")
    maas = fields.Boolean("Maaş", type="checkbox")
    yevmiye = fields.Boolean("Yevmiye", type="checkbox")
    yolluk = fields.Boolean("Yolluk", type="checkbox")
    ulke = fields.Integer("Ülke")
    soyut_rol = AbstractRole()
    kaydet_buton = fields.Button("Kaydet ve Devam Et", cmd="kaydet")

class Gorevlendirme(CrudView):
    class Meta:
        model = "KurumIciGorevlendirmeBilgileri"

    def gorevlendirme_tur_sec(self):
        """
            Görevlendirme tipinin seçildiği formu return eden bir metoddur.
        """

        # Seçili personel id si saklanıyor
        self.current.task_data["personel_id"] = self.current.input["id"]
        self.form_out(GorevlendirmeTurSecForm(current=self.current))

    def gorevlendirme_tur_kaydet(self):
        # Görevlendirme türü wf nin ilerleyen adımları için task data da saklandı
        self.current.task_data["gorevlendirme_tur"] = self.current.input["form"]["gorevlendirme_tur"]

    def kurum_ici_gorevlendirme_form(self):
        self.form_out(KurumIciGorevlendirmeForm(current=self.current))

    def kurum_disi_gorevlendirme_form(self):
        self.form_out(KurumDisiGorevlendirmeForm(current=self.current))

    def kaydet(self):
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        if self.current.task_data["gorevlendirme_tur"] == 1:
            gorevlendirme = KurumDisiGorevlendirmeBilgileri()
            gorevlendirme.kurum_disi_gorev_baslama_tarihi = self.current.input["form"]["goreve_baslama_tarihi"]
            gorevlendirme.kurum_disi_gorev_bitis_tarihi = self.current.input["form"]["gorev_bitis_tarihi"]
            gorevlendirme.aciklama = self.current.input["form"]["aciklama"]
            gorevlendirme.resmi_yazi_sayi = self.current.input["form"]["resmi_yazi_sayi"]
            gorevlendirme.resmi_yazi_tarih = self.current.input["form"]["resmi_yazi_tarih"]
            gorevlendirme.maas = self.current.input["form"]["maas"]
            gorevlendirme.yevmiye = self.current.input["form"]["yevmiye"]
            gorevlendirme.yolluk = self.current.input["form"]["yolluk"]
            gorevlendirme.ulke = self.current.input["form"]["ulke"]
            gorevlendirme.soyut_rol = self.current.input["form"]["soyut_rol"]
            gorevlendirme.personel = personel
            gorevlendirme.save()
        elif self.current.task_data["gorevlendirme_tur"] == 2:
            gorevlendirme = KurumIciGorevlendirmeBilgileri()
            gorevlendirme.kurum_ici_gorev_baslama_tarihi = self.current.input["form"]["goreve_baslama_tarihi"]
            gorevlendirme.kurum_ici_gorev_bitis_tarihi = self.current.input["form"]["gorev_bitis_tarihi"]
            gorevlendirme.birim = self.current.input["form"]["birim"]
            gorevlendirme.soyut_rol = self.current.input["form"]["soyut_rol"]
            gorevlendirme.aciklama = self.current.input["form"]["aciklama"]
            gorevlendirme.resmi_yazi_sayi = self.current.input["form"]["resmi_yazi_sayi"]
            gorevlendirme.resmi_yazi_tarih = self.current.input["form"]["resmi_yazi_tarih"]
            gorevlendirme.personel = personel
            gorevlendirme.save()


        # D6PqVfErY3mX8SfrW88EBKqMyYC => Dekan soyut rolünün id si
        # 2ry2lgJhp6iR9QNVuAehY1F7O1g => Rektör soyut rolüne ait id
        if (self.current.input["form"]["soyut_rol"] == "D6PqVfErY3mX8SfrW88EBKqMyYC") | (
                self.current.input["form"]["soyut_rol"] == "2ry2lgJhp6iR9QNVuAehY1F7O1g"):
            self.current.task_data["hizmet_cetvel_giris"] = True
        else:
            self.current.task_data["hizmet_cetvel_giris"] = False

class HizmetCetveliForm(JsonForm):
    class Meta:
        include = ["kayit_no", "baslama_tarihi", "bitis_tarihi", "gorev", "unvan_kod", "yevmiye", "ucret", "hizmet_sinifi",
                    "kadro_derece", "odeme_derece", "odeme_kademe", "odeme_ekgosterge", "kazanilmis_hak_ayligi_derece",
                    "kazanilmis_hak_ayligi_kademe", "kazanilmis_hak_ayligi_ekgosterge", "emekli_derece", "emekli_kademe",
                    "emekli_ekgosterge", "sebep_kod", "kurum_onay_tarihi"]

class HizmetCetveli(CrudView):
    class Meta:
        model = "HizmetKayitlari"

    def giris_form(self):
        self.form_out(HizmetCetveliForm(self.object, current = self.current))

    def kaydet(self):
        self.set_form_data_to_object()
        personel = Personel.objects.get(self.current.task_data["personel_id"])
        self.object.personel = personel
        self.object.tckn = personel.tckn
        self.object.save()

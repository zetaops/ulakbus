# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
""" 8 Yıllık Terfi Modülü

Bu modül Ulakbüs uygulaması için görev süresi 8 yılı doldurmuş personellerin terfi işlemlerini içerir.

"""
from ulakbus.models import Personel, Ceza, HizmetKayitlari
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __
from zengine import forms
from pyoko import ListNode
import datetime
from ulakbus.settings import DATE_DEFAULT_FORMAT
from ulakbus.lib.personel import terfi
from ulakbus.lib.hizmet_sureleri import HizmetSureleri


class TerfiKontrolForm(forms.JsonForm):
    class Meta:
        inline_edit = ['secim']

    class TerfiListe(ListNode):
        class Meta:
            title = __(u"Personeller")

        secim = fields.Boolean(__(u"Secim"), type="checkbox")
        ad = fields.String(__(u"Ad"))
        soyad = fields.String(__(u"Soyad"))
        key = fields.String(hidden=True)

    terfi_et = fields.Button(__(u"Terfi Et"), cmd="terfi_et")


class TerfiOnayForm(JsonForm):
    class Meta:
        inline_edit = ["baslangic_tarihi", "bitis_tarihi"]

    class TerfiListe(ListNode):
        class Meta:
            title = __(u"Personeller")

        ad = fields.String(__(u"Ad"))
        soyad = fields.String(__(u"Soyad"))
        baslangic_tarihi = fields.Date(__(u"Başlangıç Tarihi"),
                                       default=datetime.date.today().strftime(DATE_DEFAULT_FORMAT))
        bitis_tarihi = fields.Date(__(u"Bitiş Tarihi"), default=(
            datetime.date.today() + datetime.timedelta(days=15)).strftime(DATE_DEFAULT_FORMAT))

    onayla = fields.Button(__(u"Onayla"), cmd="onayla")
    iptal = fields.Button(__(u"İptal"), cmd="iptal")


class TerfiKontrol(CrudView):
    class Meta:
        model = "Personel"

    def terfi_kontrol(self):
        """
        8 yılı geçen terfi edilecek personelleri listeler.Personele ait ceza, sicil ve görev süresi kontrollerini içerir.

        Args:
            personel_list: Terfi edilecek personellerin listesini içerir.

        Returns:
            terfisi_mevcut: Terfi edilecek bir personel listesi mevcutsa True döndürür.
        """
        personel_list = [hizmet.personel for hizmet in
                         HizmetKayitlari.objects.filter().exclude(sebep_kod=278)]
        personel_list = self.ceza_kontrol(personel_list)
        personel_list = self.sicil_notu_var_mi(personel_list)
        personel_list = self.sicil_kontrol(personel_list)
        personel_list = self.gorev_suresi_kontrol(personel_list)
        self.current.task_data['personel_list'] = [personel.key for personel in personel_list]
        self.current.task_data['terfisi_mevcut'] = bool(personel_list)

    def gorev_suresi_kontrol(self, personeller):
        return filter(lambda personel: self.fiili_hizmet_getir(personel) == 8, personeller)

    def fiili_hizmet_getir(personel, self):
        """
        Personele ait hizmet süresinin 8 yılı geçip geçmediği kontrol edilir.

        Args:
            hizmet_suresi: Personele ait hizmet_suresi nesnesidir.

        Returns:
            personel_list: Personellere ait terfi listesini döndürür.
        """
        hizmet_suresi = HizmetSureleri()
        hizmet_suresi.personel = personel
        return hizmet_suresi.fiili_hizmet_getir()

    def ceza_kontrol(self, personeller):
        return filter(lambda personel: not Ceza.objects.filter(personel=personel).count(),
                      personeller)

    def sicil_notu_var_mi(self, personeller):
        return filter(lambda personel: personel.SicilNot, personeller)

    def sicil_notu_kontrol(self, personel):
        return True if personel.SicilNot[0].sicil_not > 80 else False

    def sicil_yili_kontrol(self, personel):
        return True if personel.SicilNot[0].sicil_yili.year == 2010 or personel.SicilNot[
                                                                           0].sicil_yili.year == 2009 else False

    def sicil_kontrol(self, personeller):
        """
        Personelin sicil_yili  2009 ve 2010 yilları arasında mı ve sicil_notu 80'den büyük mü kontrolleri yapılır.

        Args:
            sicil_notu_kontrol: Personele ait sicil notunu içerir.
            sicil_yili_kontrol: Personele ait sicil yılını içerir.

        Returns:
            personel_list: Personellere ait terfi listesini döndürür.
        """
        return filter(
            lambda personel: self.sicil_yili_kontrol(personel) and self.sicil_notu_kontrol(
                personel), personeller)

    def terfi_listesi_goruntule(self):
        self.current.output["meta"]["allow_actions"] = False
        _form = TerfiKontrolForm(title=_(u'Terfisi Gelen Personeller Listesi'))
        for personel_key in self.current.task_data['personel_list']:
            personel = Personel.objects.get(personel_key)
            _form.TerfiListe(ad=personel.ad, soyad=personel.soyad, key=personel_key)
        self.form_out(_form)

    def terfi_onay_form(self):
        self.current.output["meta"]["allow_actions"] = False
        terfi_liste = [chosen for chosen in self.input['form']['TerfiListe'] if
                       chosen['secim']]
        _form = TerfiOnayForm(title="Terfi Onay Form")
        for personel in terfi_liste:
            _form.TerfiListe(ad=personel["ad"], soyad=personel["soyad"], key=personel["key"])
            _form.help_text = _("Seçili personellere ait terfi işlemini onaylıyor musunuz?")
        self.form_out(_form)

    def terfi_et(self):
        for terfi in self.input["form"]["TerfiListe"]:
            personel = Personel.objects.get(ad=terfi["ad"], soyad=terfi["soyad"])
            terfi(personel, terfi["baslangic_tarihi"], terfi["bitis_tarihi"])

    def terfi_bilgilendirme(self):
        form = JsonForm(title="Terfi Bilgilendirme")
        form.help_text = "Personellere Ait Yeni Terfi Bulunamadı."
        form.tamam = fields.Button(_(u'Ana Menuye Don'))
        self.form_out(form)

    def yonlendir(self):
        self.current.output['cmd'] = 'reload'

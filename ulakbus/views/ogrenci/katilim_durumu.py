# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict

from pyoko.exceptions import ObjectDoesNotExist

from pyoko import ListNode
from ulakbus.models import Sube, OgrenciDersi, DersKatilimi

from zengine.forms import fields
from ulakbus.lib.view_helpers import prepare_choices_for_model

from zengine import forms
from zengine.views.crud import CrudView

__author__ = 'Ali Riza Keles'


class DevamsizlikForm(forms.JsonForm):
    class Meta:
        inline_edit = ['katilim_durumu', 'aciklama']

    class Ogrenciler(ListNode):
        ogrenci_no = fields.String('No')
        ad_soyad = fields.String('Ad Soyad')
        katilim_durumu = fields.Integer('Katılım Durumu')
        aciklama = fields.String('Açıklama')
        ogrenci_key = fields.String('ogrenci_key', hidden=True)
        ders_key = fields.String('ders_key', hidden=True)


class KatilimDurumu(CrudView):
    """Okutman Not Girişi

    Okutmanların öğrenci devamsızlıklarını sisteme girebilmesini
    sağlayan workflowa ait metdodları barındıran sınıftır.

    """

    class Meta:
        model = "DersKatilimi"

    def sube_sec(self):
        """Sube seçim adımına karşılık gelen metod."""
        _form = forms.JsonForm(current=self.current, title="Ders Seçim Formu")
        _form.sube = fields.Integer("Sube Seçiniz",
                                    choices=prepare_choices_for_model(Sube,
                                                                      okutman_id=self.get_okutman_key))
        _form.sec = fields.Button("Seç", cmd="Ders Şubesi Seçin")
        self.form_out(_form)

    def katilim_durumu(self):
        """Öğrencileri listesinden bir form oluşturur. Yerinde düzenleme
        ile öğrenci devamsızlıkları girilir."""

        _form = DevamsizlikForm(current=self.current, title="Ders Katılımı Giriş Formu")

        try:
            sube_key = self.current.input['form']['sube']
            self.current.task_data["sube_key"] = sube_key
        except KeyError:
            sube_key = self.current.task_data["sube_key"]

        ogrenciler = OgrenciDersi.objects.filter(sube_id=sube_key)

        for ogr in ogrenciler:
            try:
                katilim = DersKatilimi.objects.get(ders_id=sube_key, ogrenci=ogr.ogrenci)
                katilim_durumu = katilim.katilim_durumu
            except ObjectDoesNotExist:
                katilim_durumu = ""

            _form.Ogrenciler(ad_soyad='%s %s' % (ogr.ogrenci.ad, ogr.ogrenci.soyad),
                             ogrenci_no=ogr.ogrenci_program.ogrenci_no,
                             katilim_durumu=katilim_durumu, ogrenci_key=ogr.ogrenci.key,
                             ders_key=ogr.sube.key)

        _form.kaydet = fields.Button("Önizleme", cmd="kontrol")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

    def kontrol(self):
        """Önceki adımda forma girilen bilgilerin doğruluğunun
        kontrol edilmesi için bilgileri bir tablo şeklinde ekrana
        getirir."""

        ogrenci_katilim_durumlari = self.current.input['form']['Ogrenciler']
        self.current.task_data["katilim_durumlari"] = ogrenci_katilim_durumlari

        katilim_durumlari = []
        for ogr in ogrenci_katilim_durumlari:
            katilim_durumu = OrderedDict({})
            katilim_durumu['Öğrenci No'] = ogr['ogrenci_no']
            katilim_durumu['Adı Soyadı'] = ogr['ad_soyad']
            katilim_durumu['Değerlendirme'] = ogr['katilim_durumu']
            katilim_durumu['ogrenci_key'] = ogr['ogrenci_key']
            katilim_durumu['ders_key'] = ogr['ders_key']
            katilim_durumlari.append(katilim_durumu)

        _form = forms.JsonForm(current=self.current,
                               title="Katılım Durumu Bilgileri Önizleme Ekranı")
        _form.duzenle = fields.Button("Geri Dön ve Düzenle", cmd="katilim_durumu",
                                      flow="katilim_durumu")
        _form.kaydet = fields.Button("Kaydet", cmd="kaydet", flow="end")

        self.current.output['object'] = {
            "type": "table-multiRow",
            "fields": katilim_durumlari,
            "actions": False
        }

        self.form_out(_form)

    def kaydet(self):
        """Doğruluğu onaylanan bilgileri kaydeder."""
        for katilim in self.current.task_data['katilim_durumlari']:
            ders_katilimi, is_new = DersKatilimi.objects.get_or_create(
                ogrenci_id=katilim['ogrenci_key'], ders_id=katilim['ders_key'])
            ders_katilimi.katilim_durumu = katilim['katilim_durumu']
            ders_katilimi.save()

    def bilgi_ver(self):
        """Yapılan işlem hakkında bilgi verir."""
        sube = Sube.objects.get(self.current.task_data['sube_key'])

        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Devamsızlıklar Kaydedildi',
            "msg": '%s dersine ait ogrenci katilim bilgileri  kaydedildi' % sube.ders.ad}

    @property
    def get_okutman_key(self):
        """Harici okutman ve okutman kayıt key'lerinin ayrımını sağlayan method.
        """
        return self.current.user.personel.okutman.key if self.current.user.personel.key else self.current.user.harici_okutman.okutman.key

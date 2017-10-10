# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from collections import OrderedDict
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext_lazy as __
from ulakbus.lib.personel import yol_masrafi_hesapla, yevmiye_hesapla


class BilgiAlmaForm(JsonForm):
    konaklama_gun_sayisi = fields.Integer(__(u"Konaklama gün sayısı"))
    yolculuk_km = fields.Float(__(u"Yolculuk km "))
    tasit_ucreti = fields.Float(__(u"Taşıt ücreti"))
    yolculuk_gun_sayisi = fields.Integer(__(u"Yolculuk gün Sayısı"))
    birey_sayisi = fields.Integer(__(u"Bakmakla yükümlü olduğu kişi sayısı"))

    hesapla = fields.Button(__(u"Hesapla"))


class BilgiVerForm(JsonForm):
    tamam = fields.Button(__(u"Tamam"))


class YolYevmiyeHesapla(CrudView):
    class Meta:
        model = "Personel"

    def __init__(self, current):
        CrudView.__init__(self, current)
        # kontrol edebilmek için task data ya kendim bir personel_id ekledim
        self.current.task_data['personel_id'] = "UuXR8pmKQNzfaPHB2K5wxhC7WDo"
        if not self.object.key:
            self.object = self.model_class.objects.get(
                self.current.task_data.get('personel_id', self.input.pop('object_id', '')))
        self.current.output["meta"]["allow_search"] = False

    def bilgi_al_form(self):
        _form = BilgiAlmaForm(current=self.current,
                              title=__(u"Lütfen Tüm Alanları Eksiksiz Doldurun"))
        self.form_out(_form)

    def hesapla(self):
        ekgosterge = self.object.gorev_ayligi_ekgosterge
        derece = self.object.gorev_ayligi_derece
        konaklama_gun_sayisi = self.current.input['form']['konaklama_gun_sayisi']
        yolculuk_km = self.current.input['form']['yolculuk_km']
        tasit_ucreti = self.current.input['form']['tasit_ucreti']
        yolculuk_gun_sayisi = self.current.input['form']['yolculuk_gun_sayisi']
        birey_sayisi = self.current.input['form']['birey_sayisi']
        yevmiye = yevmiye_hesapla(konaklama_gun_sayisi, derece, ekgosterge)
        yol_masrafi = yol_masrafi_hesapla(derece, ekgosterge, yolculuk_km, tasit_ucreti,
                                          yolculuk_gun_sayisi, birey_sayisi)
        self.current.task_data['yevmiye'] = yevmiye
        self.current.task_data['yol_masrafi'] = yol_masrafi

    def bilgi_ver_form(self):
        self.current.output["meta"]["allow_actions"] = False
        bilgi_ver = OrderedDict([
            ('yevmiye', str(self.current.task_data['yevmiye'])),
            ('yol_masrafi', str(self.current.task_data['yol_masrafi'])),
        ])
        self.output['object'] = bilgi_ver
        self.form_out(BilgiVerForm(title=__('Toplam Masraflar')))


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
from ulakbus.models.personel import Personel


class BilgiAlmaForm(JsonForm):
    konaklama_gun_sayisi = fields.Integer(__(u"Konaklama gün sayısı"))
    yolculuk_km = fields.Float(__(u"Yolculuk km "))
    tasit_ucreti = fields.Float(__(u"Taşıt ücreti"))
    yolculuk_gun_sayisi = fields.Integer(__(u"Yolculuk gün Sayısı"))
    birey_sayisi = fields.Integer(__(u"Bakmakla yükümlü olduğu kişi sayısı"))

    hesapla = fields.Button(__(u"Hesapla"))

class BilgiAlmaForm2(JsonForm):
    konaklama_gun_sayisi = fields.Integer(__(u"Konaklama gün sayısı"))
    yolculuk_km = fields.Float(__(u"Yolculuk km "))
    tasit_ucreti = fields.Float(__(u"Taşıt ücreti"))
    yolculuk_gun_sayisi = fields.Integer(__(u"Yolculuk gün Sayısı"))
    birey_sayisi = fields.Integer(__(u"Bakmakla yükümlü olduğu kişi sayısı"))
    ekgosterge = fields.Integer(__(u"Personel ek gösterge"))
    derece = fields.Integer(__(u"Personel Derece"))

    hesapla = fields.Button(__(u"Hesapla"))


class BilgiVerForm(JsonForm):
    tamam = fields.Button(__(u"Tamam"))


class YolYevmiyeHesapla(CrudView):
    class Meta:
        model = "Personel"

    def kontrol(self):
        #self.current.task_data['personel_id']="UuXR8pmKQNzfaPHB2K5wxhC7WDo" #calisiyor
        self.current.task_data['kontrol'] = 0 # personel_id olmadıgında hata vermesin diye
        if 'personel_id' in self.current.task_data:
            self.current.task_data['kontrol'] = 1

    def bilgi_al_form(self):
        _form = BilgiAlmaForm(current=self.current,
                              title=__(u"Lütfen Tüm Alanları Eksiksiz Doldurun"))
        self.form_out(_form)

    def bilgi_al_form2(self):
        _form = BilgiAlmaForm2(current=self.current,
                              title=__(u"Lütfen Tüm Alanları Eksiksiz Doldurun"))
        self.form_out(_form)

    def hesapla(self):
        if self.current.task_data['kontrol']==1:
            personel = Personel.objects.get(key=self.current.task_data.get('personel_id'))
            ekgosterge = personel.gorev_ayligi_ekgosterge
            derece = personel.gorev_ayligi_derece
        else:
            ekgosterge = self.current.input['form']['ekgosterge']
            derece = self.current.input['form']['derece']
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


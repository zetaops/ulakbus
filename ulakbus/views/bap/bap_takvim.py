# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from datetime import datetime

from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import BAPTakvim, BAPProjeTurleri

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.utils import gettext as _, gettext_lazy as __

from pyoko import ListNode


class TakvimOlusturForm(JsonForm):
    class Meta:
        title = __(u"Bap Takvim Oluştur")

    class ProjeTuru(ListNode):
        class Meta:
            verbose_name = __(u"Proje Türü")
            verbose_name_plural = __(u"Proje Türleri")

        proje_turu = fields.Integer(__(u"Proje Türü Seçiniz"),
                                    choices=prepare_choices_for_model(BAPProjeTurleri))

    class OnemliTarihler(ListNode):
        class Meta:
            verbose_name = __(u"Önemli Tarih")
            verbose_name_plural = __(u"Önemli Tarihler")

        baslangic_tarihi = fields.Date(__(u"Başlangıç Tarihi"))
        bitis_tarihi = fields.Date(__(u"Bitiş Tarihi"))
        aciklama = fields.Integer(__(u"Açıklama Seçiniz"), choices='onemli_tarih_aciklama')

    takvim_aciklama = fields.Text(__(u"Takvim Açıklaması"))
    donem = fields.Integer(__(u"Takvimin Yayınlanacağı Dönem"))

    kaydet = fields.Button(_(u"Kaydet"))
    iptal = fields.Button(_(u"İptal"), cmd='list', form_validation=False)


class TakvimListForm(JsonForm):
    class Meta:
        title = __(u"Bap Takvim")
    genel_takvim = fields.Button(__(u"Genel Takvim Ekle"), cmd='add_edit_form')
    proje_tur_takvim = fields.Button(__(u"Proje Tür Takvim Ekle"), cmd='add_edit_form')


class BapTakvim(CrudView):
    class Meta:
        model = 'BAPTakvim'

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'object_id' in self.current.task_data and self.cmd == 'add_edit_form' and \
                'object_id' not in self.input:
            del self.current.task_data['object_id']
            self.object = BAPTakvim()

    def list(self, custom_form=TakvimListForm(readable=True)):
        CrudView.list(self, custom_form)

    def add_edit_form(self):
        form = TakvimOlusturForm(current=self.current, title=_(u"Takvim Olustur"))

        if ('form' in self.input and self.input['form']['genel_takvim']) or (
                not self.object.ProjeTuru and 'object_id' in self.current.task_data):
            form.exclude = ['ProjeTuru']
        if 'object_id' in self.input and self.object:
            if self.object.ProjeTuru:
                [form.ProjeTuru(proje_turu=proje.key) for proje in self.object.ProjeTuru.objects]
            form.OnemliTarihler = self.object.OnemliTarihler
            form.takvim_aciklama = self.object.takvim_aciklama
            form.donem = self.object.donem
        self.form_out(form)

    def save(self):
        if 'object_id' in self.current.task_data:
            takvim = BAPTakvim.objects.get(self.current.task_data['object_id'])
            takvim.OnemliTarihler.clear()
            takvim.ProjeTuru.clear()
        else:
            takvim = BAPTakvim()

        takvim.donem = self.input['form']['donem']
        takvim.takvim_aciklama = self.input['form']['takvim_aciklama']

        [takvim.OnemliTarihler(aciklama=tarih['aciklama'],
                               baslangic_tarihi=datetime.strptime(
                                   tarih['baslangic_tarihi'],
                                   '%d.%m.%Y' if tarih['baslangic_tarihi'].find(":") == -1 else
                                   '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                               bitis_tarihi=datetime.strptime(
                                   tarih['bitis_tarihi'],
                                   '%d.%m.%Y' if tarih['bitis_tarihi'].find(":") == -1 else
                                   '%Y-%m-%dT%H:%M:%S.%fZ').date())
         for tarih in self.input['form']['OnemliTarihler']]

        if 'ProjeTuru' in self.input['form']:
            [takvim.ProjeTuru(proje_turu=BAPProjeTurleri.objects.get(
                proje['proje_turu_id']['key'] if 'proje_turu_id' in proje else proje['proje_turu']))
             for proje in self.input['form']['ProjeTuru']]

        takvim.blocking_save()

    def takvim_yayinla_onay(self):
        pass

    def takvim_yayinla(self):
        pass

    @obj_filter
    def proje_turu_islem(self, obj, result):
        result['actions'].extend([
            {'name': _(u'Sil'), 'cmd': 'confirm_deletion', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'}])
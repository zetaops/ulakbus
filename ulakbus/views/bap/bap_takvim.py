# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from datetime import datetime

from ulakbus.models import BAPTakvim, BAPProjeTurleri

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.utils import gettext as _, gettext_lazy as __


class TakvimOlusturForm(JsonForm):
    class Meta:
        title = __(u"Bap Takvim Oluştur")

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

    def list(self, custom_form=None):
        custom_form = TakvimListForm()
        CrudView.list(self, custom_form)

    def add_edit_form(self):
        form = TakvimOlusturForm(self.object, current=self.current, title=_(u"Takvim Oluştur"))

        if ('form' in self.input and self.input['form']['genel_takvim']) or (
                not self.object.ProjeTuru and 'object_id' in self.current.task_data):
            form.exclude = ['ProjeTuru']
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
            [takvim.ProjeTuru(proje_turu=BAPProjeTurleri.objects.get(proje['proje_turu_id']))
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
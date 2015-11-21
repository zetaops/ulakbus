# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Yeni Personel Ekle WF adimlarini icerir.
from pyoko import form
from zengine.views.crud import CrudView, obj_filter

from zengine.lib.forms import JsonForm
from ulakbus.models.personel import Kadro


class KadroIslemleri(CrudView):
    class Meta:
        model = 'Kadro'
        dispatch = False
        object_actions = []

    class ObjectForm(JsonForm):
        class Meta:
            exclude = ['durum', ]

        save_edit = form.Button("Kaydet")

    # def kadro_ekle_form(self):
    #     self.object_form.exclude = ['durum',]
    #     self.form()

    def kadro_kaydet(self):
        super(KadroIslemleri, self).set_form_data_to_object()
        self.object.durum = 1
        self.save()

    def sakli_izinli_degistir(self):
        self.object.durum = 1
        self.save()

    @obj_filter
    def sakli_kadro(self, obj, result):
        if obj.durum == 1:
            result['actions'] = [{'name': 'Izinli Yap', 'cmd': 'form', 'mode': 'normal', 'show_as': 'button'}, ]
        return result

    @obj_filter
    def izinli_kadro(self, obj, result):
        if obj.durum == 2:
            result['actions'] = [{'name': 'Sakli Yap', 'cmd': 'form', 'mode': 'normal', 'show_as': 'button'}, ]
        return result

    @obj_filter
    def duzenlenebilir_veya_silinebilir_kadro(self, obj, result):
        if obj.durum == 2 or obj.durum == 1:
            result['actions'] = [
                {'name': 'Sil', 'cmd': 'delete', 'mode': 'bg', 'show_as': 'button'},
                {'name': 'Düzenle', 'cmd': 'form', 'mode': 'normal', 'show_as': 'button'},
            ]
        return result

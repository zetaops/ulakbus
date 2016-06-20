# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.models import Ogrenci, OgrenciDersi, Sube
from zengine.forms import fields
from zengine.lib import forms
from zengine.views.crud import CrudView


def sube_arama(current):
    q = current.input.get('query')
    r = []

    for o in Sube.objects.search_on(*['ders_adi'], contains=q):
        r.append((o.key, o.__unicode__()))

    current.output['objects'] = r


class DersSecimForm(forms.JsonForm):
    class Meta:
        inline_edit = ['secim']

    class Dersler(ListNode):
        key = fields.String(hidden=True)
        ders_adi = fields.String('Ders')

    ileri = fields.Button("İleri")


class OgrenciDersEkleme(CrudView):
    class Meta:
        model = 'Ders'

    def ogrenci_ders_secme(self):
        user_key = self.current.user.key
        ogrenci = Ogrenci.objects.get(user_id=user_key)
        ogrenci_dersleri_lst = OgrenciDersi.objects.filter(ogrenci=ogrenci)
        _form = DersSecimForm(title='Ders Seçiniz', current=self.current)
        for ogr_dersi in ogrenci_dersleri_lst:
            if ogr_dersi.sube.ders.zorunlu and not ogr_dersi.katilim_durumu:
                _form.Dersler(key=ogr_dersi.sube.key, ders_adi=ogr_dersi.sube.ders_adi)

        self.form_out(_form)
        self.ders_secim_form_inline_edit()

    def ders_secim_form_inline_edit(self):
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['type'] = 'model'
        self.output['forms']['schema']['properties']['Dersler']['schema'][0]['model_name'] = "Ders"
        self.output['forms']['schema']['properties']['Dersler']['quick_add'] = True
        self.output['forms']['schema']['properties']['Dersler']['quick_add_field'] = "ders_adi"
        self.output['forms']['schema']['properties']['Dersler']['quick_add_view'] = "sube_arama"

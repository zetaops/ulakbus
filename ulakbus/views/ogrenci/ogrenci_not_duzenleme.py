# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import Sube, Sinav, OgrenciDersi, DegerlendirmeNot, Ogrenci
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView


class OgrenciSecimForm(forms.JsonForm):
    class Meta:
        inline_edit = ['secim']

    class Ogrenciler(ListNode):
        ogrenci_key = fields.String('ogrenci_key', hidden=True)
        secim = fields.Boolean(type="checkbox")
        ad_soyad = fields.String('Ad Soyad')


# class SubeSecimForm(forms.JsonForm):
#     class Subeler(ListNode):
#         key = fields.String('sube_key', hidden=True)
#         ders_adi = fields.String('Şube')
#
#     ileri = fields.Button('İleri')

class SubeSecimForm(forms.JsonForm):
    class Meta:
        title = 'Şube Seçim'
    sube = fields.String('Şube Seçiniz', type='typeahead')
    ileri = fields.Button('İleri')


class NotDuzenlemeForm(forms.JsonForm):
    class Meta:
        include = ['puan']

    kaydet = fields.Button('Kaydet')


def sube_arama(current):
    subeler = []
    query = current.input.get('query')
    for sube in Sube.objects.search_on(*['ders_adi'], contains=query):
        subeler.append((sube.key, sube.ders_adi))

    current.output['objects'] = subeler


class OgrenciNotDuzenleme(CrudView):
    class Meta:
        model = 'DegerlendirmeNot'

    def fakulte_yonetim_karar_no_gir(self):
        """
        Fakülte Yönetim Kurulu tarafından belirlenen karar no girilir.

        """

        # TODO: Fakülte yönetim kurulunun kararı loglanacak.
        _form = forms.JsonForm(current=self.current,
                               title='Fakülte Yönetim Kurulunun Karar Numarasını Giriniz.')
        _form.karar = fields.String('Karar No', index=True)
        _form.kaydet = fields.Button('Kaydet')
        self.form_out(_form)

    def sube_sec(self):
        """

        """
        _form = SubeSecimForm(current=self.current)
        _form.set_choices_of('sube', choices=prepare_choices_for_model(Sube))
        # if 'subeler' in self.current.task_data:
        #     for sube in self.current.task_data['subeler']:
        #         _form.Subeler(key=sube['key'], ders_adi=sube['ders_adi'])

        self.form_out(_form)
        # self.inline_edit_sube_form()
        self.current.output["meta"]["allow_actions"] = True

    def subeyi_kontrol_et(self):
        self.current.task_data['sube_lst'] = self.current.input['form']['Subeler']
        if len(self.current.task_data['sube_lst']) != 1:
            self.current.task_data['cmd'] = 'sube_sec'
            self.current.task_data['subeler'] = self.current.task_data['sube_lst']

    def sinav_sec(self):
        sinavlar = []
        for sube in self.current.task_data['sube_lst']:
            sinav_lst = Sinav.objects.filter(sube_id=sube['key'])
            for sinav in sinav_lst:
                _sinav = (sinav.key, sinav.__unicode__())
                sinavlar.append(_sinav)

        _form = forms.JsonForm(current=self.current, title='Sınav Seçiniz')
        _form.sinav = fields.Integer('Sınavlar', choices=tuple(sinavlar))
        _form.ileri = fields.Button('İleri')
        self.form_out(_form)

    def ogrenci_sec(self):
        _sinav = Sinav.objects.get(self.current.input['form']['sinav'])
        self.current.task_data['sinav_key'] = self.current.input['form']['sinav']
        ogrenci_dersi_lst = OgrenciDersi.objects.filter(sube=_sinav.sube)
        _form = OgrenciSecimForm(current=self.current, title='Öğrenci Seçiniz')
        for ogrenci_dersi in ogrenci_dersi_lst:
            _form.Ogrenciler(ogrenci_key=ogrenci_dersi.ogrenci.key,
                             ad_soyad='%s %s' % (ogrenci_dersi.ogrenci.ad, ogrenci_dersi.ogrenci.soyad))
        _form.ileri = fields.Button('İleri')
        self.form_out(_form)
        self.current.output['meta']['allow_actions'] = False

    def ogrenci_secim_kaydet(self):
        self.current.task_data['ogrenciler'] = [ogr for ogr in self.current.input['form']['Ogrenciler'] if ogr['secim']]
        msg = {"title": 'Not Düzenleme İşlemi',
               "body": 'Not düzenleme işlemi için sınav, öğrenci, şube seçimi başarıyla tamamlanmıştır.'}

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def not_duzenle(self):
        _ogrenci = self.current.task_data['ogrenciler'].pop()
        ogrenci_object = Ogrenci.objects.get(_ogrenci['ogrenci_key'])
        _sinav = Sinav.objects.get(self.current.task_data['sinav_key'])
        degerlendirme_not = DegerlendirmeNot.objects.get(sinav_id=self.current.task_data['sinav_key'],
                                                         ogrenci_id=_ogrenci['ogrenci_key'])
        _form = NotDuzenlemeForm(degerlendirme_not, current=self.current, title='Not Düzenleme Ekranı')
        _form.help_text = '%s adlı öğrencininin %s adlı sınava ait puanı' % (ogrenci_object, _sinav)
        self.form_out(_form)

    def bilgi_ver(self):
        self.current.output['msgbox'] = {'type': 'info', "title": 'Not Düzenleme',
                                         "msg": 'Öğrencilere ait notlar başarıyla düzenlendi'}

    # def inline_edit_sube_form(self):
    #     self.output['forms']['schema']['properties']['Subeler']['quick_add'] = True
    #     self.output['forms']['schema']['properties']['Subeler']['quick_add_field'] = "ders_adi"
    #     self.output['forms']['schema']['properties']['Subeler']['quick_add_view'] = "sube_arama"

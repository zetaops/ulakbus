# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import OgrenciProgram, OgrenciDersi, Sinav, DegerlendirmeNot
from ulakbus.views.ders.ders import prepare_choices_for_model
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView


class NotDuzenlemeForm(forms.JsonForm):
    class Meta:
        include = ['puan']

    kaydet = fields.Button('Kaydet')


class NotDuzenleme(CrudView):
    class Meta:
        model = 'DegerlendirmeNot'

    def fakulte_yonetim_karari(self):
        # TODO: Fakülte yönetim kurulunun kararı loglanacak.
        self.current.task_data['ogrenci_id'] = self.current.input['id']
        _form = forms.JsonForm(current=self.current, title='Fakülte Yönetim Kurulunun Karar Numarasını Giriniz.')
        _form.karar = fields.String('Karar No', index=True)
        _form.kaydet = fields.Button('Kaydet')
        self.form_out(_form)

    def program_sec(self):
        _form = forms.JsonForm(current=self.current, title='Program Seçiniz.')
        _choices = prepare_choices_for_model(OgrenciProgram, ogrenci_id=self.current.task_data['ogrenci_id'])
        _form.program = fields.Integer(choices=_choices)
        _form.onayla = fields.Button('Seç')
        self.form_out(_form)

    def ders_sec(self):
        program_id = self.current.input['form']['program']
        _form = forms.JsonForm(current=self.current, title='Ders Seçiniz.')
        _choices = prepare_choices_for_model(OgrenciDersi, ogrenci_program_id=program_id)
        _form.ders = fields.Integer(choices=_choices)
        _form.onayla = fields.Button('Seç')
        self.form_out(_form)

    def sinav_sec(self):
        self.current.task_data['ders_id'] = self.current.input['form']['ders']
        ders = OgrenciDersi.objects.get(self.current.task_data['ders_id'])
        _form = forms.JsonForm(current=self.current, title='Sınav Seçiniz.')
        _choices = prepare_choices_for_model(Sinav, sube_id=ders.sube.key)
        _form.sinav = fields.Integer(choices=_choices)
        _form.onayla = fields.Button('Seç')
        self.form_out(_form)

    def not_duzenle(self):
        sinav_id = self.current.input['form']['sinav']
        ogrenci_id = self.current.task_data['ogrenci_id']
        degerlendirme_not = DegerlendirmeNot.objects.filter(sinav_id=sinav_id, ogrenci_id=ogrenci_id)[0]
        title = '%s adlı öğrencinin % sınava ait notunu düzenleyiniz.' % (
            degerlendirme_not.ogrenci, degerlendirme_not.sinav)
        _form = NotDuzenlemeForm(degerlendirme_not, current=self.current, title=title)
        self.form_out(_form)

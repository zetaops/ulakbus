# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import random
from pyoko import form
from zengine.lib.forms import JsonForm
from zengine.views.crud import CrudView
from ulakbus.models.ogrenci import Program
from ulakbus.models.ogrenci import Ders


class ProgramBilgisiForm(JsonForm):
    class Meta:
        include = ['program']

    sec = form.Button("Seç", cmd="program_sec")


class DersBilgileriForm(JsonForm):
    class Meta:
        include = ['ad', 'kod', 'tanim', 'aciklama', 'onkosul', 'uygulama_saati', 'teori_saati', 'ects_kredisi',
                   'yerel_kredisi', 'zorunlu', 'ders_dili', 'ders_turu', 'ders_amaci', 'ogrenme_ciktilari',
                   'ders_icerigi', 'ders_kategorisi', 'ders_kaynaklari', 'ders_mufredati', 'verilis_bicimi', 'donem',
                   'ders_koordinatoru']

    kaydet = form.Button("Kaydet", cmd="kaydet", flow="end")
    kaydet_yeni_kayit = form.Button("Kaydet/Yeni Kayıt Ekle", cmd="kaydet", flow="start")


class DersEkle(CrudView):
    class Meta:
        model = "Ders"

    def program_sec(self):
        self.set_form_data_to_object()
        self.current.task_data['program_id'] = self.object.program.key

    def kaydet(self):
        self.set_form_data_to_object()
        self.object.program = Program.objects.get(self.current.task_data['program_id'])
        self.save_object()
        # self.current.task_data['next'] = self.current.input['next']

    def ders_bilgileri(self):
        self.form_out(DersBilgileriForm(self.object, current=self.current))

    def program_bilgisi(self):
        self.form_out(ProgramBilgisiForm(self.object, current=self.current))


class ProgramForm(JsonForm):
    programs = Program.objects.filter()
    program_choices = []
    for pr in programs:
        program_choices.append((pr.key, pr.adi))

    program = form.Integer(choices=program_choices)
    sec = form.Button("Sec", cmd="ders_sec")


class DersListeForm(JsonForm):
    dersler = Ders.objects.filter(program_key=self.current.input['form']['program'])
    ders = Ders.objects.filter()
    for d in dersler:
        f[d.id] = form.String(d.ad)


class DersSubelendirme(CrudView):
    class Meta:
        model = "Sube"

    def program_sec(self):
        self.form_out(ProgramForm(current=self.current))

    def ders_sec(self):
        self.form_out(DersListeForm())

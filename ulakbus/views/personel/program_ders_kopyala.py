# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine import forms
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import Ogrenci, OgrenciProgram, Program,Donem

class ProgramSecimForm(forms.JsonForm):
    """
    ``DanismanAtama`` sınıfı için form olarak kullanılacaktır.
    """

    sec = fields.Button("Seç")

class ProgramKopyalama(CrudView):
    """Danışman Atama
    Öğrencilere danışman atamalarının yapılmasını sağlayan workflowa ait
    metdodları barındıran sınıftır.
    """

    class Meta:
        model = "OgrenciProgram"

    def program_sec(self):
        """Program Seçim Adımı
        Programlar veritabanından çekilip, açılır menu içine
        doldurulur.
        """
        guncel_donem = Donem.objects.filter(guncel=True)[0]
        ogrenci_id = self.current.input['id']
        self.current.task_data['ogrenci_id'] = ogrenci_id
        self.current.task_data['donem_id'] = guncel_donem.key

        _form = ProgramSecimForm(current=self.current, title="Kopyalanacak Programı Seçiniz")
        _choices = prepare_choices_for_model(OgrenciProgram, ogrenci_id=ogrenci_id)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)

    def senato_no_gir(self):
        pass

    def senato_no_kaydet(self):
        pass

    def ders_kopyala(self):
        pass

    def ders_tablo(self):
        pass

    def ders_duzenle_form(self):
        pass

    def ders_duzenle(self):
        pass

    
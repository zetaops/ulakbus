# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import Program, Sube

class ProgramSecimForm(JsonForm):
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
        _form = ProgramSecimForm(current=self.current, title="Kopyalanacak Programı Seçiniz")
        _choices = prepare_choices_for_model(Sube)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)



    def senato_no_gir(self):
         _form = ProgramSecimForm(current=self.current, title="Kopyalanacak Programı Seçiniz")
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


# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict

from pyoko import ListNode
from zengine.views.crud import CrudView, form_modifier
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import Program, Ders

class ProgramDersForm(JsonForm):

    class Dersler(ListNode):

        secim = fields.Boolean(type="checkbox")
        ders_adi = fields.String('Ders')
        key = fields.String('Key', hidden=True)
        onkosul = fields.String("Önkoşul", index=True)
        uygulama_saati = fields.Integer("Uygulama Saati", index=True)
        aciklama = fields.String('Aciklama')


class ProgramKopyalama(CrudView):

    class Meta:
        model = "Program"

    def program_sec(self):

        _form = JsonForm(current=self.current, title="Kopyalanacak Programı Seçiniz")
        _choices = prepare_choices_for_model(Program)
        _form.program = fields.Integer(choices=_choices)
        _form.sec = fields.Button("Seç")
        self.form_out(_form)

    def senato_no_gir(self):

        _form = JsonForm(current=self.current, title="Senato Numarasi Giriniz")
        _form.senato_karar_no = fields.String("Senato Karar Numarası", index=True)
        _form.kaydet = fields.Button("Kaydet", cmd="save")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_selection"] = False
        self.current.task_data['program_id'] = self.input['form']['program']

    def senato_numarasi_kaydet(self):

       Program.Version.senato_karar_no = self.input['form']['senato_karar_no']


    def ders_kopyala(self):

        program = Program.objects.get(self.current.task_data['program_id'])
        program_dersleri = Ders.objects.filter(program=program)
        self.current.task_data['dersler'] = program_dersleri


    def ders_tablo(self):

        #program = Program.objects.get(self.current.task_data['program_id'])
        #dersler = Ders.objects.get(self.current.task_data)

        try:
            _form = ProgramDersForm(current=self.current, title="Kopyalanacak Dersleri Seçiniz")
            #program_dersleri = Ders.objects.filter(program=program)
            #self.current.task_data['dersler'] = program_dersleri
            for ders in self.current.task_data['dersler']:
                _form.Dersler(secim=False, ders_adi=ders.ad, key=ders.key,
                            aciklama=ders.aciklama, onkosul = ders.onkosul, uygulama_saati = ders.uygulama_saati)

            _form.kaydet = fields.Button("Tamamla", cmd="save", flow="personel_bilgilendir")
            _form.duzenle = fields.Button("Degisiklikleri Kaydet", cmd="save", flow="ders_duzenle")
            self.form_out(_form)

            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_selection"] = False

        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Program Dersleri Listeleme Başarısız. Hata Kodu : %s' % e.message
            }


    def ders_duzenle(self):

        dersler = self.current.input['form']['Dersler']
        self.current.task_data["ders"] = dersler

        for ders in self.current.task_data["ders"]:
            if ders.aciklama:
                self.current.task_data['dersler']['aciklama'] = ders.aciklama

    def personel_bilgilendir(self):

        self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Onay Mesaji',
                "msg": 'Program Dersleri Basariyla Kopyalandi'
            }


    @form_modifier
    def program_ders_form_inline_edit(self, serialized_form):
        """ProgramDersForm'da seçim ve açıklama alanlarına inline
        edit özelliği sağlayan method.

        Args:
            serialized_form: serialized form

        """
        if 'Dersler' in serialized_form['schema']['properties']:
            serialized_form['inline_edit'] = ['secim', 'aciklama','onkosul','uygulama_saati']
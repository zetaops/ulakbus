# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko import ListNode
from zengine.views.crud import CrudView, form_modifier
from zengine.forms import fields
from zengine.forms import JsonForm
from ulakbus.views.ders.ders import prepare_choices_for_model
from ulakbus.models.ogrenci import Program, Sube, Ders

class SenatoForm(JsonForm):
    """
    ``OncekiEgitimBilgileri`` sınıfı  için object form olarak kullanılacaktır. Form,
    include listesinde, aşağıda tanımlı alanlara sahiptir.

    """

    class Meta:
        include = ["Version"]

    kaydet = fields.Button("Kaydet", cmd="save")


class ProgramDersForm(JsonForm):
    class Dersler(ListNode):
        secim = fields.Boolean(type="checkbox")
        ders_adi = fields.String('Ders')
        key = fields.String('Key', hidden=True)
        aciklama = fields.String('Aciklama')

    sec = fields.Button("Kaydet")


class ProgramKopyalama(CrudView):
    """Danışman Atama
    Öğrencilere danışman atamalarının yapılmasını sağlayan workflowa ait
    metdodları barındıran sınıftır.
    """

    class Meta:
        model = "Program"

    def program_sec(self):
        """Program Seçim Adımı
        Programlar veritabanından çekilip, açılır menu içine
        doldurulur.
        """
        _form = JsonForm(current=self.current, title="Kopyalanacak Programı Seçiniz")
        _choices = prepare_choices_for_model(Program)
        _form.program = fields.Integer(choices=_choices)
        _form.sec = fields.Button("Seç")
        self.form_out(_form)

    def ders_kopyala(self):
        pass

    def ders_tablo(self):
        self.current.task_data['program_id'] = self.input['form']['program']
        program = Program.objects.get(self.current.task_data['program_id'])
        try:
            _form = ProgramDersForm(current=self.current, title="Kopyalanacak Dersleri Seçiniz")
            program_dersleri = Ders.objects.filter(program=program)
            for ders in program_dersleri:
                _form.Dersler(secim=False, ders_adi=ders.ad, key=ders.key,
                               aciklama=ders.aciklama)
            self.form_out(_form)
            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_selection"] = False
        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Program Dersleri Listeleme Başarısız. Hata Kodu : %s' % e.message
            }

        _form = ProgramDersForm(current=self.current, title="Dersler")
        _choices = prepare_choices_for_model(Ders)
        _form.program = fields.Integer(choices=_choices)
        self.form_out(_form)

    def ders_duzenle_form(self):
        pass

    def ders_duzenle(self):
        pass

        # def bilgilendirme(self):
        #   self.current.output['msgbox'] = {
        #      'type': 'info', "title": 'Onay Mesaji',
        #    "msg": 'Program dersleri kopyalandi.'
        # }

    @form_modifier
    def program_ders_form_inline_edit(self, serialized_form):
        """ProgramDersForm'da seçim ve açıklama alanlarına inline
        edit özelliği sağlayan method.

        Args:
            serialized_form: serialized form

        """
        if 'Dersler' in serialized_form['schema']['properties']:
            serialized_form['inline_edit'] = ['secim', 'aciklama']

class SenatoNumara(CrudView):
    class Meta:
        model = "Program"

    def senato_no_gir(self):
        self.form_out(SenatoForm(self.object, current=self.current, title="Senato Numarasi Giriniz"))

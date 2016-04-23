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
from ulakbus.models.ogrenci import Program, Ders, Donem

class ProgramDersForm(JsonForm):
    class Dersler(ListNode):
        secim = fields.Boolean(type="checkbox")
        ders_adi = fields.String('Ders')
        key = fields.String('Key', hidden=True)
        onkosul = fields.String("Önkoşul", index=True)
        uygulama_saati = fields.Integer("Uygulama Saati", index=True)
        aciklama = fields.String('Aciklama')
        kod = fields.String('Kod')


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
        self.current.task_data['program_id'] = self.current.input['form']['program']
        _form = JsonForm(current=self.current, title="Senato Numarasi Giriniz")
        _form.senato_karar_no = fields.String("Senato Karar Numarası", index=True)
        _form.kaydet = fields.Button("Kaydet")
        self.form_out(_form)
        # self.current.output["meta"]["allow_actions"] = False
        # self.current.output["meta"]["allow_selection"] = False

    def senato_no_kaydet_ders_kopyala(self):

        senato_karar_no = self.current.input['form']['senato_karar_no']

        program = Program.objects.get(self.current.task_data['program_id'])
        program.Version.add(senato_karar_no=senato_karar_no)
        program.save()

        for ders in Ders.objects.filter(program=program):
            ders.donem = Donem.guncel_donem()
            ders.key = None
            ders.program_versiyon = senato_karar_no
            ders.save()

    # def ders_kopyala(self):
    #     program = Program.objects.get(self.current.task_data['program_id'])
    #
    #     for ders in Ders.objects.filter(program=program):
    #         ders.donem = Donem.guncel_donem()
    #         ders.key = None
    #         ders.save()

    def ders_tablo(self):

        program = Program.objects.get(self.current.task_data['program_id'])
        try:
            _form = ProgramDersForm(current=self.current, title="Degisiklik Yapilacak Dersleri Seçiniz")
            program_dersleri = Ders.objects.filter(program=program, donem=Donem.guncel_donem())

            for ders in program_dersleri:
                _form.Dersler(secim=False, kod=ders.kod, ders_adi=ders.ad)

                # _form.kaydet = fields.Button("Tamamla", flow="personel_bilgilendir")
            _form.duzenle = fields.Button("Onayla", flow="ders_duzenle")
            self.form_out(_form)

            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_selection"] = False

        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Program Dersleri Listeleme Başarısız. Hata Kodu : %s' % e.message
            }

    def ders_duzenle(self):

        if len(self.current.task_data["dersler"]) == 0: #tanimlanmamissa
            self.current.task_data["dersler"] = self.current.input['form']['Dersler']
            dict = []
            for secim in self.current.task_data["dersler"]:
                if secim['secim'] == True:
                    dict.append(secim)
            self.current.task_data["secilenler"] = dict

        _form = ProgramDersForm(current=self.current, title="Duzeltmeyi Yapiniz")
        if len(self.current.task_data["secilenler"]) != 0:
            ders = self.current.task_data["secilenler"][0]
            _form.Secilenler(Dersler=ders)
            _form.duzenle = fields.Button("Degisiklikleri Kaydet", flow="ders_duzenle")
            self.form_out()

        else:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Onay Mesajı',
                "msg": 'Degişikliklerinizi bitirdiniz, Tamamla diyerek tum degişikliklerinizi onaylayabilirsiniz.'
            }
            fields.Button("Tamamla", flow="personel_bilgilendir")

    # degisiklik_ders = Ders.objects.get(key=ders['key'])
    # if degisiklik_ders.aciklama != ders['aciklama']:
    #   degisiklik_ders.aciklama = ders['aciklama']
    #  degisiklik_ders.save()

    def ders_kaydet(self):
        ders = self.current.task_data["secilenler"][0]
        degisiklik_ders = Ders.objects.get(key=ders['key'])
        degisiklik_ders = ders
        degisiklik_ders.save()
        del self.current.task_data["secilenler"][0]
        # if degisiklik_ders.aciklama != ders['aciklama']:
        #   degisiklik_ders.aciklama = ders['aciklama']
        #  degisiklik_ders.save()

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
            serialized_form['inline_edit'] = ['secim', 'aciklama', 'onkosul', 'uygulama_saati', 'kod']

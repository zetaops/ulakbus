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


class SecilenDersForm(JsonForm):
    class Meta:
        # model = 'Ders'
        include = ['ad', 'kod', 'tanim', 'aciklama','donem']
        # , 'onkosul', 'uygulama_saati', 'teori_saati']
        # 'ects_kredisi',
        # 'yerel_kredisi', 'zorunlu', 'ders_dili', 'ders_turu', 'ders_amaci',
        # 'ogrenme_ciktilari',
        # 'ders_icerigi', 'ders_kategorisi', 'ders_kaynaklari', 'ders_mufredati',
        # 'verilis_bicimi', 'donem',
        # 'ders_koordinatoru']


class DersDuzenle(CrudView):
    class Meta:
        model = "Ders"

    def ders_bilgileri_duzenle(self):
        try:
            self.current.task_data["dersler"]

        except:
            self.current.task_data["dersler"] = self.current.input['form']['Dersler']
            secilen_dersler = []
            for secilen_ders in self.current.task_data["dersler"]:
                if secilen_ders['secim'] == True:
                    secilen_dersler.append(secilen_ders)
            self.current.task_data["secilenler"] = secilen_dersler
            self.current.task_data["control"] = True

        if len(self.current.task_data["secilenler"]) != 0:
            secilen_ders = self.current.task_data["secilenler"][0]
            ders = Ders.objects.get(key=secilen_ders['key'])

            _form = SecilenDersForm(ders, current=self.current, title="Degisikligi Yapiniz")
            _form.kaydet = fields.Button("Kaydet", flow="ders_kaydet")
            self.form_out(_form)
            self.current.task_data["control"] = False

        elif len(self.current.task_data["secilenler"]) == 0 and self.current.task_data["control"]:
            _form = JsonForm(current=self.current, title="Degisiklik Yapmak Icin Ders Secmelisiniz!")
            _form.tamamla = fields.Button("Ders Secme Ekranina Geri Don", flow="ders_tablo")
            self.form_out(_form)
            del self.current.task_data["dersler"]

        else:
            _form = JsonForm(current=self.current,
                             title="Islemi bitirmek için 'Tamamla' butonuna basınız.")
            _form.tamamla = fields.Button("Tamamla", flow="personel_bilgilendir")
            self.form_out(_form)

    def ders_kaydet(self):

        self.set_form_data_to_object()
        self.save()
        del self.current.task_data["secilenler"][0]


class ProgramDersForm(JsonForm):
    class Dersler(ListNode):
        secim = fields.Boolean(type="checkbox")
        ad = fields.String("Ad", index=True)
        kod = fields.String("Kod", index=True)
        key = fields.String('Key', hidden=True)


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

    def senato_no_kaydet_ders_kopyala(self):

        senato_karar_no = self.current.input['form']['senato_karar_no']
        program = Program.objects.get(self.current.task_data['program_id'])
        program.Version.add(senato_karar_no=senato_karar_no)
        program.save()

        for ders in Ders.objects.filter(program=program):

            ders.key = None
            ders.donem = Donem.guncel_donem()
            ders.program_versiyon = senato_karar_no
            ders.save()

    def ders_tablo(self):

        program = Program.objects.get(self.current.task_data['program_id'])
        try:
            _form = ProgramDersForm(current=self.current, title="Degisiklik Yapmak Istediginiz Dersleri Seçiniz")
            program_dersleri = Ders.objects.filter(program=program,donem = Donem.guncel_donem())
            for ders in program_dersleri:
                _form.Dersler(secim=False, kod=ders.kod, ad=ders.ad, key=ders.key)
            _form.duzenle = fields.Button("Onayla")
            self.form_out(_form)

            self.current.output["meta"]["allow_actions"] = False
            self.current.output["meta"]["allow_selection"] = False

        except Exception as e:
            self.current.output['msgbox'] = {
                'type': 'warning', "title": 'Bir Hata Oluştu',
                "msg": 'Program Dersleri Listeleme Başarısız. Hata Kodu : %s' % e.message
            }

    def personel_bilgilendir(self):

        self.current.output['msgbox'] = {
            'type': 'warning', "title": 'Onay Mesaji',
            "msg": 'Degisiklikler Kaydedildi ve Program Dersleri Basariyla Kopyalandi'
        }

    @form_modifier
    def program_ders_form_inline_edit(self, serialized_form):
        """ProgramDersForm'da seçim ve açıklama alanlarına inline
        edit özelliği sağlayan method.

        Args:
            serialized_form: serialized form

        """
        if 'Dersler' in serialized_form['schema']['properties']:
            serialized_form['inline_edit'] = ['secim']

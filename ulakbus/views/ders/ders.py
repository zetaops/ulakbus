# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import ListNode
from zengine import forms
from zengine.forms import fields
from zengine.views.crud import CrudView
from ulakbus.models.ogrenci import Program, Okutman
from ulakbus.models.ogrenci import Ders
from ulakbus.models.ogrenci import Sube


def prepare_choices_for_model(model, **kwargs):
    return [(m.key, m.__unicode__()) for m in model.objects.filter(**kwargs)]


def okutman_choices():
    return [{'name': name, 'value': value} for value, name in prepare_choices_for_model(Okutman)]


class ProgramBilgisiForm(forms.JsonForm):
    class Meta:
        include = ['program']

    sec = fields.Button("Seç", cmd="program_sec")


class DersBilgileriForm(forms.JsonForm):
    class Meta:
        include = ['ad', 'kod', 'tanim', 'aciklama', 'onkosul', 'uygulama_saati', 'teori_saati',
                   'ects_kredisi',
                   'yerel_kredisi', 'zorunlu', 'ders_dili', 'ders_turu', 'ders_amaci',
                   'ogrenme_ciktilari',
                   'ders_icerigi', 'ders_kategorisi', 'ders_kaynaklari', 'ders_mufredati',
                   'verilis_bicimi', 'donem',
                   'ders_koordinatoru']

    kaydet = fields.Button("Kaydet", cmd="kaydet", flow="end")
    kaydet_yeni_kayit = fields.Button("Kaydet/Yeni Kayıt Ekle", cmd="kaydet", flow="start")


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


class BosForm(forms.JsonForm):
    sec = fields.Button("Sec", cmd="ders_sec")


class ProgramForm(forms.JsonForm):
    sec = fields.Button("Sec", cmd="ders_sec")


class SubelendirmeForm(forms.JsonForm):
    kaydet_ders = fields.Button("Kaydet ve Ders Seçim Ekranına Dön", cmd="subelendirme_kaydet",
                                flow="ders_okutman_formu")
    program_sec = fields.Button("Kaydet ve Program Seçim Ekranına Dön", cmd="subelendirme_kaydet",
                                flow="program_sec")
    bilgi_ver = fields.Button("Tamamla ve Hocaları Bilgilendir", cmd="subelendirme_kaydet",
                              flow="bilgi_ver")

    class Subeler(ListNode):
        ad = fields.String('Sube Adi')
        kontenjan = fields.Integer('Sube Kontenjani')
        dis_kontenjan = fields.Integer('Sube Dis Kontenjani')
        okutman = fields.String('Okutman', choices=okutman_choices)


class DersSubelendirme(CrudView):
    class Meta:
        model = "Sube"

    def program_sec(self):
        _form = ProgramForm(current=self.current)
        choices = prepare_choices_for_model(Program)
        _form.program = fields.Integer(choices=choices)
        self.form_out(_form)

    def ders_sec(self):
        self.set_client_cmd('form')
        self.output['objects'] = [['Dersler'], ]

        if 'program' in self.current.input['form']:
            self.current.task_data['program'] = self.current.input['form']['program']

        p = Program.objects.get(key=self.current.task_data['program'])
        dersler = Ders.objects.filter(program=p)
        # dersler = Ders.objects.filter()
        for d in dersler:
            ders = "{} - {} ({} ECTS)".format(d.kod, d.ad, d.ects_kredisi)
            subeler = Sube.objects.filter(ders=d)
            sube = []
            for s in subeler:
                sube.append(
                        {
                            "sube_ad": s.ad,
                            "okutman_ad": s.okutman.ad,
                            "okutman_soyad": s.okutman.soyad,
                            "okutman_unvan": s.okutman.unvan,
                            "kontenjan": s.kontenjan,
                        }
                )

            ders_subeleri = ["{okutman_unvan} {okutman_ad}"
                             "{okutman_soyad}, Sube:{sube_ad} Kontenjan{kontenjan} \n".format(**sb)
                             for sb in sube]

            item = {
                "fields": ["{} \n {}".format(ders, ders_subeleri), ],
                "actions": [
                    {'name': 'Subelendir', 'cmd': 'ders_okutman_formu', 'show_as': 'button',
                     'object_key': 'sube'},
                ],
                "key": d.key
            }
            self.output['objects'].append(item)

    def ders_okutman_formu(self):
        # subelendirme icin secilen dersi getir
        ders = Ders.objects.get(key=self.current.input['sube'])
        # sonraki adimlar icin task data icine koy
        self.current.task_data['ders_key'] = ders.key

        # formu olusturmaya basla
        subelendirme_form = SubelendirmeForm(current=self.current,
                                             title='%s / %s dersi icin subelendirme' % (
                                                 ders.donem, ders))
        # formun sube listesini olustur
        subeler = Sube.objects.filter(ders=ders)
        for sube in subeler:
            subelendirme_form.Subeler(ad=sube.ad, kontenjan=sube.kontenjan,
                                      dis_kontenjan=sube.dis_kontenjan,
                                      okutman=sube.okutman.key)

        self.form_out(subelendirme_form)

    def subelendirme_kaydet(self):
        sb = self.input['form']['Subeler']
        ders = self.current.task_data['ders_key']
        mevcut_subeler = Sube.objects.filter(ders_id=ders)
        for s in sb:
            okutman = s['okutman']
            sube, is_new = Sube.objects.get_or_create(okutman_id=okutman, ders_id=ders)
            # mevcut_subelerden cikar
            mevcut_subeler = list(set(mevcut_subeler) - {sube})
            sube.kontenjan = s['kontenjan']
            sube.dis_kontenjan = s['dis_kontenjan']
            sube.ad = s['ad']
            sube.save()
        # mevcut subelerde kalanlari sil
        for s in mevcut_subeler:
            s.delete()

    def bilgi_ver(self):
        sbs = Sube.objects.filter(ders_id=self.current.task_data['ders_key'])
        okutmanlar = [s.okutman.__unicode__() for s in sbs]
        self.current.set_message(type='info', title='Mesaj Iletildi',
                                 msg='Şubelendirme Bilgileri şu hocalara iletildi: %s' % ", ".join(
                                     okutmanlar))

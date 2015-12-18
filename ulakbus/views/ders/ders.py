# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import form, ListNode
from zengine.lib.forms import JsonForm
from zengine.views.crud import CrudView
from ulakbus.models.ogrenci import Program, Okutman
from ulakbus.models.ogrenci import Ders
from ulakbus.models.ogrenci import Sube


def prepare_choices_for_model(model, **kwargs):
    query_filter = ''
    ms = model.objects.filter(**kwargs)
    choices = []
    for m in ms:
        choices.append((m.key, m.__unicode__()))
    return choices


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


class BosForm(JsonForm):
    sec = form.Button("Sec", cmd="ders_sec")


class ProgramForm(JsonForm):
    sec = form.Button("Sec", cmd="ders_sec")


class SubelendirmeForm(JsonForm):
    sec = form.Button("Kaydet", cmd="subelendirme_kaydet")

    class Subeler(ListNode):
        ad = form.String('Sube Adi')
        kontenjan = form.Integer('Sube Kontenjani')
        dis_kontenjan = form.Integer('Sube Dis Kontenjani')
        okutman = form.Integer('Okutman', choices=prepare_choices_for_model(Okutman))


class DersSubelendirme(CrudView):
    class Meta:
        model = "Sube"

    def program_sec(self):
        _form = ProgramForm(current=self.current)
        choices = prepare_choices_for_model(Program)
        _form.program = form.Integer(choices=choices)
        self.form_out(_form)

    def ders_sec(self):
        self.set_client_cmd('form')
        self.output['objects'] = [['Dersler'], ]
        # dersler = Ders.objects.filter(program_key=self.current.input['form']['program'])
        dersler = Ders.objects.filter()
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
                             "{okutman_soyad}, Sube:{sube_ad} Kontenjan{kontenjan} \n".format(**sb) for sb in sube]

            item = {
                "fields": ["{} \n {}".format(ders, ders_subeleri), ],
                "actions": [
                    {'name': 'Subelendir', 'cmd': 'ders_okutman_formu', 'show_as': 'button', 'object_key': 'sube'},
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
                                             title='%s / %s dersi icin subelendirme' % (ders.donem, ders))
        # formun sube listesini olustur
        subeler = Sube.objects.filter(ders=ders)
        for sube in subeler:
            subelendirme_form.Subeler(ad=sube.ad, kontenjan=sube.kontenjan, dis_kontenjan=sube.dis_kontenjan,
                                      okutman=sube.okutman.key)
        # sb = {}
        # i = 0
        # for sube in subeler:
        #     sb.update({
        #         'subead_%s' % i: form.String('Sube Adi', default=sube.ad),
        #         'subekon_%s' % i: form.String('Sube Kontenjan', default=sube.kontenjan),
        #         'subediskon_%s' % i: form.String('Sube Dis Kontenjan', default=sube.dis_kontenjan),
        #         'subeoktman_%s' % i: form.String('Okutman', default=sube.okutman.ad)
        #     })
        #     i += 1
        # for k, v in sb.items():
        #     setattr(subelendirme_form, k, v)

        self.form_out(subelendirme_form)

    def subelendirme_kaydet(self):
        sb = self.input['form']['Subeler']
        ders = Ders.objects.get(key=self.current.task_data['ders_key'])
        for s in sb:
            okutman = s.okutman
            sube = Sube.objects.get_or_create(okutman=okutman, ders=ders)
            sube.kontenjan = s.kontenjan
            sube.dis_kontenjan = s.dis_kontenjan
            sube.ad = s.ad
            sube.save()

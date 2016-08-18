# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from collections import OrderedDict

from ulakbus.models import DersEtkinligi, Room
from ulakbus.models.ders_sinav_programi import HAFTA
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView


class DerslikSecimFormu(JsonForm):
    """
    Derslik Seç adımında kullanılan formdur.

    """
    ileri = fields.Button("İleri")


class DerslikDersProgrami(CrudView):
    """ Derslik Ders Programı İş Akışı
    Derslik Ders Programi,bir bölümün sahip olduğu dersliklere ait ders programlarını gösterir ve
    kullanıcının ders programlarını yazdırabilmesine olanak sağlar.

    Bu iş akışı 2 adımdan oluşur.

    Derslik Seç:
    Derslikler listelenir.

    Derslik Ders Programını Göster:
    Seçilen dersliğe ait ders programlarını ekrana basar.

    """
    class Meta:
        model = 'DersEtkinligi'

    def derslik_sec(self):
        """
        Derslikler listelenir.

        """
        _form = DerslikSecimFormu(title='Derslik Seçiniz', current=self.current)
        ders_etkinlikleri = DersEtkinligi.objects.filter(solved=True)
        _choices = [(_etkinlik.room.key, _etkinlik.room.__unicode__()) for _etkinlik in ders_etkinlikleri]
        _form.derslik = fields.Integer(choices=_choices)
        self.form_out(_form)

    def derslik_ders_programini_goster(self):
        """
        Seçilen dersliğe ait ders programlarını ekrana basar.

        """
        room = Room.objects.get(self.current.input['form']['derslik'])

        def hafta_gun_olustur(hafta):
            hafta_dict = {}
            for i in range(len(hafta)):
                hafta_dict[hafta[i][0]] = hafta[i][1]

            return hafta_dict

        def ders_etkinlik_olustur(ders_etkinlikleri):
            ders_etkinlik = {}
            for d_e in ders_etkinlikleri:
                if d_e.gun in ders_etkinlik:
                    ders_etkinlik[d_e.gun].append(d_e)
                else:
                    ders_etkinlik[d_e.gun] = [d_e]
            return ders_etkinlik

        ders_etkinlikleri = ders_etkinlik_olustur(DersEtkinligi.objects.filter(room=room))
        self.output['objects'] = [['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']]
        hafta_dict = hafta_gun_olustur(HAFTA)
        for i in range(max(map(len, ders_etkinlikleri.values()))):
            ders_etkinlikleri_dict = OrderedDict({})
            for hafta_gun in hafta_dict.keys():
                if hafta_gun in ders_etkinlikleri:
                    try:
                        etkinlik = ders_etkinlikleri[hafta_gun][i]
                        baslangic_saati = "**%s**" % etkinlik.baslangic_saat + ':' + "**%s**" % etkinlik.baslangic_dakika
                        bitis_saati = "**%s**" % etkinlik.bitis_saat + ':' "**%s**" % etkinlik.bitis_dakika
                        ders_etkinlikleri_dict[hafta_dict[hafta_gun]] = baslangic_saati + ' - ' + bitis_saati + ' ' + \
                                                                        etkinlik.sube.ders_adi
                    except IndexError:
                        ders_etkinlikleri_dict[hafta_dict[hafta_gun]] = ""
                else:
                    ders_etkinlikleri_dict[hafta_dict[hafta_gun]] = ""
            item = {
                "type": "table-multiRow",
                "fields": ders_etkinlikleri_dict,
                "actions": False,
                'key': ''
            }
            self.output['objects'].append(item)

        _form = JsonForm(title="%s Dersliğine Ait Ders Programları" % room.__unicode__())
        _form.yazdir = fields.Button('Pdf yazdır')
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import SinavEtkinligi, Room
from ulakbus.models.ders_sinav_programi import HAFTA
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from collections import OrderedDict
import calendar


class DerslikSecimFormu(JsonForm):
    """
    Derslik Sınav ProgramLaı iş akışının sınav seç adımında kullanılan form.
    """

    ileri = fields.Button("İleri")


class DerslikSinavProgramlari(CrudView):
    """ Derslik Sınav Programları
    Derslik Sınav Programları iş akışı, seçilen dersliğe ait sınav programlarını gösterip kullanıcının
    yazdırabilmesine olanak sağlar.

    İş akışı 2 adımdan oluşur.

    Derslik Seç:
    Derslik Seçilir.

    Derslik Sınav Programlarını Göster:
    Seçilen dersliğe ait sınavlar etkinliklerinin ders adını ve tarihi gösterir.

    """

    class Meta:
        model = "SinavEtkinligi"

    def derslik_sec(self):
        """
        Derslik Seçilir.

        """
        _form = DerslikSecimFormu(title="Derslik Seçiniz", current=self.current)
        _choices = [(s_yerleri.room.key, s_yerleri.room.__unicode__()) for s_etkinlik in
                    SinavEtkinligi.objects.filter(solved=True)
                    for s_yerleri in s_etkinlik.SinavYerleri if s_etkinlik.SinavYerleri]
        _form.derslik = fields.Integer(choices=_choices)
        self.form_out(_form)

    def derslik_sinav_programlarini_goster(self):
        """
        Seçilen dersliğe ait sınavlar etkinliklerinin ders adını ve tarihi gösterir.

        """
        def hafta_gun_olustur(HAFTA):
            hafta_dict = {}
            for i in range(len(HAFTA)):
                hafta_dict[HAFTA[i][0]] = HAFTA[i][1]

            return hafta_dict

        def sinav_etkinlik_olustur(sinav_etkinlikleri):
            sinav_etkinlik = {}
            for s_e in sinav_etkinlikleri:
                try:
                    tarih = s_e.tarih
                    gun = calendar.weekday(tarih.year, tarih.month, tarih.day) + 1

                    if gun in sinav_etkinlik:
                        sinav_etkinlik[gun].append(s_e)
                    else:
                        sinav_etkinlik[gun] = [s_e]
                except:
                    pass
            return sinav_etkinlik

        room = Room.objects.get(self.current.input['form']['derslik'])
        object_list = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        self.output['objects'] = [object_list]
        s_etkinlikleri = [s for s in SinavEtkinligi.objects if room in s.SinavYerleri and s.solved]
        sinav_etkinlikleri = sinav_etkinlik_olustur(s_etkinlikleri)
        hafta_dict = hafta_gun_olustur(HAFTA)
        for i in range(max(map(len, sinav_etkinlikleri.values()))):
            sinav_etkinlik_list = OrderedDict({})
            for hafta_gun in hafta_dict.keys():
                    if hafta_gun in sinav_etkinlikleri:
                        try:
                            etkinlik = sinav_etkinlikleri[hafta_gun][i]
                            sinav_saat = "**%02d**" % etkinlik.tarih.time().hour + ':' + "**%02d**" % etkinlik.tarih.time().minute
                            sinav_etkinlik_list[hafta_dict[hafta_gun]] = "**%s**" % etkinlik.tarih.strftime(
                                '%d.%m.%Y') + ' - ' + sinav_saat + ' ' + etkinlik.sube.ders_adi
                        except IndexError:
                            sinav_etkinlik_list[hafta_dict[hafta_gun]] = ''

                    else:
                        sinav_etkinlik_list[hafta_dict[hafta_gun]] = ''
            item = {
                "type": "table-multiRow",
                "fields": sinav_etkinlik_list,
                "actions": False,
                'key': ''
            }
            self.output['objects'].append(item)
        _form = JsonForm(title="%s Dersliğine Ait Sınav Programlar" % room.__unicode__())
        _form.yazdir = fields.Button("Pdf Yazdır")
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False


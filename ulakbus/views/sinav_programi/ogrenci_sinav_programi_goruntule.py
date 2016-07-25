# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.models import Donem, Ogrenci, OgrenciDersi
from ulakbus.models.ders_programi import HAFTA
from ulakbus.views.sinav_programi import okutman_sinav_programi_goruntule as SP


class Ogrenci_Sinav_Programi_Goruntule(CrudView):
    def sinav_programi_goruntule(self):

        ogrenci = Ogrenci.objects.get(user=self.current.user)
        # ogrenci = Ogrenci.objects.get('Fj3ysQn3lMlgXcxhGILzsfAiGZ')
        guncel_donem = Donem.objects.get(guncel=True)
        ogrenci_dersleri = OgrenciDersi.objects.filter(ogrenci=ogrenci, donem=guncel_donem)

        subeler = []
        for ogrenci_ders in ogrenci_dersleri:
            subeler.append(ogrenci_ders.sube)

        ogrenci_adi = ogrenci.ad + ' ' + ogrenci.soyad

        sinav_etkinlik = SP.sinav_etkinlik_olustur(subeler)
        object_list = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        self.output['objects'] = [object_list]

        _form = JsonForm(current=self.current)
        _form.title = "%s %s Sınav Programı" % (ogrenci_adi, guncel_donem.ad)

        hafta_dict = SP.hafta_gun_olustur(HAFTA)
        for i in range(max(map(len, sinav_etkinlik.values()))):
            sinav_etkinlik_list = OrderedDict({})
            for hafta_gun in hafta_dict.keys():
                if hafta_gun in sinav_etkinlik:
                    try:
                        etkinlik = sinav_etkinlik[hafta_gun][i]
                        sinav_saat = "%02d" % etkinlik.tarih.time().hour + ':' + "%02d" % etkinlik.tarih.time().minute
                        sinav_etkinlik_list[hafta_dict[hafta_gun]] = etkinlik.sube.ad + ' / ' + etkinlik.tarih.strftime(
                            '%d:%m:%Y') + ' / ' + sinav_saat
                    except:
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

        self.form_out(_form)

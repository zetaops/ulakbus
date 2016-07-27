# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.models import Donem, Ogrenci, OgrenciDersi, \
    Sube  # eğer haftanın günü(1,2..) öğretim görevlisinin sınavı varsa
from ulakbus.models.ders_programi import HAFTA
from ulakbus.views.sinav_programi import okutman_sinav_programi_goruntule as SP


class Ogrenci_Sinav_Programi_Goruntule(CrudView):
    def sinav_programi_goruntule(self):

        """
        Öğrenci kendi şubelerine ait sinav
        programını görüntüleyebilir.

        """
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        guncel_donem = Donem.objects.get(guncel=True)
        # Güncel döneme ve giriş yapan, öğrenciye ait öğrenci_dersleri bulunur.
        ogrenci_dersleri = OgrenciDersi.objects.filter(ogrenci=ogrenci, donem=guncel_donem)

        subeler = []
        # Bulunan öğrenci derslerinin şubeleri bulunur ve listeye eklenir.
        for ogrenci_ders in ogrenci_dersleri:
            try:
                sube = Sube.objects.get(ogrenci_ders.sube.key)
                subeler.append(sube)
            except:
                pass

        ogrenci_adi = ogrenci.ad + ' ' + ogrenci.soyad

        # öğrencinin şubelerine göre sınav etkinlikleri
        # dictionary'e eklenir.
        sinav_etkinlik = SP.sinav_etkinlik_olustur(subeler)
        object_list = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        self.output['objects'] = [object_list]

        _form = JsonForm(current=self.current)
        _form.title = "%s / %s Sınav Programı" % (ogrenci_adi, guncel_donem.ad)

        hafta_dict = SP.hafta_gun_olustur(HAFTA)
        # Öğrencinin bir günde maksimum kaç tane sınavı olduğu bulunur
        # ve bu bilgi kadar dönülür.
        for i in range(max(map(len, sinav_etkinlik.values()))):
            sinav_etkinlik_list = OrderedDict({})
            # eğer haftanın günü(1,2..) öğrencinin sınavı varsa
            for hafta_gun in hafta_dict.keys():
                if hafta_gun in sinav_etkinlik:
                    try:
                        etkinlik = sinav_etkinlik[hafta_gun][i]
                        sinav_saat = "%02d:%02d" % (etkinlik.tarih.time().hour, etkinlik.tarih.time().minute)
                        sinav_etkinlik_list[hafta_dict[hafta_gun]] = str(
                            etkinlik.sube.ad) + ' / ' + etkinlik.tarih.strftime(
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

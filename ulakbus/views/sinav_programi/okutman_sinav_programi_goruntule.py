# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.models import Okutman, Personel, Sube, Donem
from ulakbus.models.ders_programi_data import SinavEtkinligi
from ulakbus.models.ders_programi import HAFTA
import calendar

class Okutman_Sinav_Programi_Goruntule(CrudView):

    def sinav_programi_goruntule(self):

        # personel = Personel.objects.get(user = self.current.user)
        # okutman = Okutman.objects.get(personel = personel)
        okutman = Okutman.objects.get('5RC4wiXxdolAHvw0o703Qzk1sw7') # it will change
        guncel_donem = Donem.objects.get(guncel = True) #it will change
        subeler = Sube.objects.filter(okutman=okutman, donem = guncel_donem)
        okutman_adi = okutman.ad + ' ' + okutman.soyad

        sinav_etkinlik = sinav_etkinlik_olustur(subeler)
        object_list = ['Pazartesi','Salı','Çarşamba','Perşembe','Cuma','Cumartesi','Pazar']
        self.output['objects'] = [object_list]

        _form = JsonForm(current=self.current)
        _form.title = "%s %s Sınav Programı" % (okutman_adi, guncel_donem.ad)

        hafta_dict = hafta_gun_olustur(HAFTA)
        for i in range(max(map(len,sinav_etkinlik.values()))):
            sinav_etkinlik_list = OrderedDict({})
            for hafta_gun in hafta_dict.keys():
                if hafta_gun in sinav_etkinlik:
                    try:
                        etkinlik = sinav_etkinlik[hafta_gun][i]
                        sinav_saat = "%02d" %etkinlik.tarih.time().hour +':' + "%02d" %etkinlik.tarih.time().minute
                        sinav_etkinlik_list[hafta_dict[hafta_gun]] = etkinlik.sube.ad+' / '+ etkinlik.tarih.strftime('%d:%m:%Y')+ ' / ' + sinav_saat
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

def sinav_etkinlik_olustur(subeler):

    sinav_etkinlik = {}
    for sube in subeler:
        try:
            etkinlik = SinavEtkinligi.objects.get(sube=sube)
            tarih = etkinlik.tarih
            gun = calendar.weekday(tarih.year, tarih.month, tarih.day) + 1

            if gun in sinav_etkinlik:
                sinav_etkinlik[gun].append(etkinlik)
            else:
                sinav_etkinlik[gun] = [etkinlik]
        except:
            pass
    return sinav_etkinlik

def hafta_gun_olustur(HAFTA):

    hafta_dict = {}
    for i in range(len(HAFTA)):
        hafta_dict[HAFTA[i][0]] = HAFTA[i][1]

    return hafta_dict






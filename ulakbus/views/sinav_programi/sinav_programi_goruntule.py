# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from ulakbus.lib.date_time_helper import map_etkinlik_hafta_gunleri
from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.models import Personel, Donem, Ogrenci
from ulakbus.models.ders_sinav_programi import HAFTA
from ...lib.ogrenci import aktif_sinav_listesi
from zengine.lib.translation import gettext as _, get_day_names


class SinavProgramiGoruntule(CrudView):
    def sinav_etkinlikleri(self, obj):
        sinav_etkinlikleri = aktif_sinav_listesi(obj)

        if len(sinav_etkinlikleri) > 0:
            self.current.task_data['sinav_kontrol'] = True
            self.current.task_data['sinav_etkinlikleri'] = map_etkinlik_hafta_gunleri(
                sinav_etkinlikleri)
        else:
            self.current.task_data['sinav_kontrol'] = False

    def ogrenci_sinav_listesi(self):
        """
        Öğretim görevlisinin yayınlanmış sınav programının olup olmadığını kontrol eder.
        """

        # Giriş yapılan öğretim görevlisinin personel objesi getirilir.
        ogrenci = Ogrenci.objects.get(user=self.current.user)
        self.current.task_data['user_ad'] = ogrenci.__unicode__()
        self.sinav_etkinlikleri(ogrenci)

    def okutman_sinav_listesi(self):
        """
        Öğretim görevlisinin yayınlanmış sınav programının olup olmadığını kontrol eder.
        """

        # Giriş yapılan öğretim görevlisinin personel objesi getirilir.
        personel = Personel.objects.get(user=self.current.user)
        okutman = personel.okutman
        self.current.task_data['user_ad'] = okutman.__unicode__()
        self.sinav_etkinlikleri(okutman)

    def sinav_programi_uyari(self):

        """
        Eğer yayınlanmış sınav programı yoksa uyarı verir.
        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Uyarı!'),
            "msg": _(u'Bulunduğunuz döneme ait, güncel yayınlanmış sınav programı bulunmamaktadır.')
        }

    def sinav_programi_goruntule(self):
        """
        Öğretim Görevlisi kendi şubelerine ait sinav
        programını görüntüleyebilir.

        """

        sinav_etkinlikleri = self.current.task_data['sinav_etkinlikleri']

        self.output['objects'] = [list(get_day_names().values())]
        hafta = dict(HAFTA)

        # Öğretim görevlisinin bir günde maksimum kaç tane sınavı olduğu bulunur
        # ve bu bilgi kadar dönülür.
        max_etkinlik = max(map(len, sinav_etkinlikleri.values()))

        for i in range(max_etkinlik):
            sinav_etkinlik_list = OrderedDict({})

            # eğer haftanın günü(1,2..) öğretim görevlisinin sınavı varsa
            for hafta_gun in hafta.keys():
                if hafta_gun in sinav_etkinlikleri:
                    try:
                        etkinlik = sinav_etkinlikleri[hafta_gun][i]
                        sinav_etkinlik_list[hafta[hafta_gun]] = etkinlik
                    except IndexError:
                        sinav_etkinlik_list[hafta[hafta_gun]] = ''

                else:
                    sinav_etkinlik_list[hafta[hafta_gun]] = ''

            item = {
                "type": "table-multiRow",
                "fields": sinav_etkinlik_list,
                "actions": False,
                'key': ''
            }
            self.output['objects'].append(item)

        _form = JsonForm(current=self.current)
        _form.title = _(u"%(ad)s / %(donem)s / Yarıyıl Sınav Programı") % \
                      {'ad': self.current.task_data['user_ad'],
                       'donem': Donem.guncel_donem(self.current).ad}

        self.form_out(_form)

# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.forms import JsonForm
from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.models import Okutman, Personel, Donem
from ulakbus.models.ders_programi_data import okutman_sinav_etkinligi_getir, SinavEtkinligi
from ulakbus.models.ders_programi import HAFTA
import calendar


class Okutman_Sinav_Programi_Goruntule(CrudView):
    def sinav_programi_kontrol(self):
        """
        Öğretim görevlisinin yayınlanmış sınav programının olup olmadığını kontrol eder.
        """

        # Giriş yapılan öğretim görevlisinin personel objesi getirilir.
        personel = Personel.objects.get(user=self.current.user)
        # Okutman objesi bulunur.
        okutman = Okutman.objects.get(personel=personel)

        sinav_etkinlikleri = okutman_sinav_etkinligi_getir(okutman)

        if len(sinav_etkinlikleri) > 0:
            self.current.task_data['sinav_kontrol'] = True
            self.current.task_data['sinav_etkinlikleri'] = map(lambda s: s.key, sinav_etkinlikleri)
        else:
            self.current.task_data['sinav_kontrol'] = False

    def sinav_programi_uyari(self):

        """
        Eğer yayınlanmış sınav programı yoksa uyarı verir.
        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": 'Uyarı!',
            "msg": 'Bulunduğunuz döneme ait, güncel yayınlanmış sınav programı bulunmamaktadır.'
        }

    def sinav_programi_goruntule(self):
        """
        Öğretim Görevlisi kendi şubelerine ait sinav
        programını görüntüleyebilir.

        """
        # Giriş yapılan öğretim görevlisinin personel objesi getirilir.
        personel = Personel.objects.get(user=self.current.user)
        # Okutman objesi bulunur.
        okutman = Okutman.objects.get(personel=personel)

        guncel_donem = Donem.objects.get(guncel=True)
        # Güncel döneme ve giriş yapan öğretim görevlisine ait şubeler bulunur.
        okutman_adi = okutman.ad + ' ' + okutman.soyad

        # Öğretim görevlisinin haftanın günlerine göre sınavları bir dictionary'de
        # tutulur. Dictionary'nin key'leri 1'den 7'ye kadardır. 1 Pazartesini 7'de
        # Pazar'ı gösterir.
        sinav_etkinlik = sinav_etkinlik_olustur(map(lambda s: SinavEtkinligi.objects.get(s),
                                                    self.current.task_data['sinav_etkinlikleri']))
        object_list = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']
        self.output['objects'] = [object_list]

        _form = JsonForm(current=self.current)
        _form.title = "%s / %s / Yarıyıl Sınav Programı" % (okutman_adi, guncel_donem.ad)

        hafta_dict = hafta_gun_olustur(HAFTA)
        # Öğretim görevlisinin bir günde maksimum kaç tane sınavı olduğu bulunur
        # ve bu bilgi kadar dönülür.
        for i in range(max(map(len, sinav_etkinlik.values()))):
            sinav_etkinlik_list = OrderedDict({})
            # eğer haftanın günü(1,2..) öğretim görevlisinin sınavı varsa
            for hafta_gun in hafta_dict.keys():
                if hafta_gun in sinav_etkinlik:
                    try:
                        etkinlik = sinav_etkinlik[hafta_gun][i]
                        sinav_saat = "%02d:%02d" % (etkinlik.tarih.time().hour, etkinlik.tarih.time().minute)
                        sinav_etkinlik_list[hafta_dict[hafta_gun]] = "%s / %s / %s / %s" % (
                        etkinlik.sube.ders.ad, etkinlik.sube.ad, etkinlik.tarih.strftime(
                            '%d:%m:%Y'), sinav_saat)
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


def sinav_etkinlik_olustur(sinav_etkinlikleri):
    sinav_etkinlik = {}
    # sınav_etkinlik dictionarynin yapısı şu şekildedir:
    # sinav_etkinlik = {1:[sinav object, sinav object],3:[sinav object]}
    for etkinlik in sinav_etkinlikleri:

        tarih = etkinlik.tarih
        gun = calendar.weekday(tarih.year, tarih.month, tarih.day) + 1

        # eğer varsa listeye ekler, yoksa list yaratılıp içerisine eklenir.
        if gun in sinav_etkinlik:
            sinav_etkinlik[gun].append(etkinlik)
        else:
            sinav_etkinlik[gun] = [etkinlik]

    # bir günde bulunan sınavlar zamanına göre küçükten büyüğe sıralanır.
    for etkinlik in sinav_etkinlik.keys():
        sinav_etkinlik[etkinlik] = sorted(sinav_etkinlik[etkinlik], key=zamana_gore_sirala)

    return sinav_etkinlik


def zamana_gore_sirala(sinav):
    return sinav.tarih


# HAFTA bir tuple listesidir, method HAFTA'yı dictionary haline çevirir.
def hafta_gun_olustur(HAFTA):
    hafta_dict = {}
    for i in range(len(HAFTA)):
        hafta_dict[HAFTA[i][0]] = HAFTA[i][1]

    return hafta_dict

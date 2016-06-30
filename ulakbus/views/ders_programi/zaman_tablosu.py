# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.views.crud import CrudView
from ulakbus.models.ders_programi import OgElemaniZamanPlani, ZamanCetveli
from collections import OrderedDict


class ZamanTablo(CrudView):

    def zaman_tablosu_listele(self):
        """
            Ilgili birime ait Ogretim elemanlarini ekranda gosterir.
            Ilk kez girildiginde birime ait ogretim elemanlarin, gunlerin
            saat araliklarindaki durumlari default olarak uygun olarak gelir.
            Duzenle butonuna tiklandigi zaman o ogretim elemanina ait gun saat dilimi
            degisebilir hale gelir.Degisiklikler bittigi zaman kaydedilip tekrar
            zaman_tablosu_listele is akisina gelir. Duzenlemeler yapildiktan sonra
            onayla butonuna tiklandiginda duzenlenen zaman tablosu birimin bolum
            baskanina onay icin gonderilir.

        """
        self.output['objects'] = [['Ogretim Elemani', 'Pazartesi', 'Sali', 'Carsamba', 'Persembe', 'Cuma']]
        unit = self.current.role.unit
        ogretim_elemani_zaman_planlari = OgElemaniZamanPlani.objects.filter(birim=unit)

        for oe in ogretim_elemani_zaman_planlari:
            zaman_tablosu = OrderedDict({})
            zaman_cetveli = ZamanCetveli.objects.filter(ogretim_elemani_zaman_plani=oe, birim=unit)
            zaman_tablosu['Ogretim Elemani'] = str(oe.okutman())
            zaman_tablosu['Pazartesi'] = ''.join(sorted(["""%s:%s-%s:%s= %s
            \n""" % (zc.zaman_dilimi.baslama_saat,
                     zc.zaman_dilimi.baslama_dakika,
                     zc.zaman_dilimi.bitis_saat,
                     zc.zaman_dilimi.bitis_dakika,
                     zc.durum) for zc in zaman_cetveli if zc.zaman_dilimi.gun == 1]))
            zaman_tablosu['Sali'] = ' '
            zaman_tablosu['Carsamba'] = ' '
            zaman_tablosu['Persembe'] = ' '
            zaman_tablosu['Cuma'] = ' '

            item = {
                "type": "table-multiRow",
                "fields": zaman_tablosu,
                "actions": [
                    {'name': 'Duzenle', 'cmd': 'duzenle', 'show_as': 'button', 'object_key': 'okutman'},
                ],
                'key': oe.okutman.key
            }

            self.output['objects'].append(item)

    def duzenle(self):
            pass

    def reddet(self):
        pass

    def ogretim_elemani_kaydet(self):
        pass

    def onaya_gonder(self):
        msg = {"title": 'Onay İçin Gönderildi!!',
               "body": 'Ögretim elemanı zaman tablosu onay için Bölüm Başkanına gönderildi.'}

        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgi_ekrani(self):
        pass

    # Lane Gecisi Bolum Baskani

    def onay_ekrani(self):
        pass

    def geri_gonder(self):
        pass

    def onayla_ve_bilgilendir(self):
        pass

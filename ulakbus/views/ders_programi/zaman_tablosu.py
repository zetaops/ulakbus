# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.views.crud import CrudView
from ulakbus.models.ders_programi import OgElemaniZamanPlani, ZamanCetveli, ZamanDilimleri


class ZamanTablo(CrudView):

    def ogretim_gorevlisi_sec(self):
        # default select first person
        try:
            if self.current.secili_og_elemani:
                self.current.ogretim_elemani = OgElemaniZamanPlani.objects.get(self.current.secili_og_elemani)
        except AttributeError:
            self.current.ogretim_elemani = OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)[0]

    def zaman_tablosu_listele(self):
        """
        Creates a message for the given channel.
        .. code-block:: python
            # response:
            {
                'ogretim_elemani': {
                    'oe_key': string   # ogretim_elemani_key
                    'name': string,     # name surname,
                    'toplam_ders_saati': int,   # hours,
                    'uygunluk_durumu': [{
                        'key': string,     # zaman_cetveli_key
                        'saat': string,  # 10:00-12:00,
                        'gun': int,     # 1 = pazartesi,
                        'durum': int    # 2 = mumkunse uygun degil,
                        }]}
            }
        """

        zaman_cetveli = sorted(ZamanCetveli.objects.filter(ogretim_elemani_zaman_plani=self.current.ogretim_elemani),
                               key=lambda z: (z.zaman_dilimi, z.gun))

        uygunluk_durumu = list()

        for zc in zaman_cetveli:
            durum = dict()
            durum['key'] = zc.key
            durum['saat'] = zc.zaman_dilimi.baslama_saat + ':' + zc.zaman_dilimi.baslama_dakika + '-' + \
                            zc.zaman_dilimi.bitis_saat + ':' + zc.zaman_dilimi.bitis_dakika
            durum['gun'] = zc.gun
            durum['durum'] = zc.durum
            uygunluk_durumu.append(durum)

        item = {'oe_key': self.current.ogretim_elemani.key,
                'name': self.current.ogretim_elemani.okutman.ad + ' ' + self.current.ogretim_elemani.okutman.soyad,
                'toplam_ders_saati': self.current.ogretim_elemani.toplam_ders_saati,
                'uygunluk_durumu': uygunluk_durumu}

        self.output['ogretim_elemani_zt'] = item

    def zaman_degisiklik_kaydet(self):
        """"

        # request:
        {
            'change':{
                'key': string   # key,
                'durum': int    # 1 = uygun,
                'cmd': 'degistir'}
        }

        """

        change = self.current.input['change']
        key = change['key']
        zc = ZamanCetveli.objects.get(key)
        zc.durum = change['durum']
        zc.save()

    def personel_sec(self):
        """

        # request:
        {
            'secili_og_elemani':{
                'key': string   #  personel key,
                'cmd': 'personel_sec'}
        }

        """
        self.current.secili_og_elemani = self.current.input['secili_og_elemani']['key']

    def onaya_gonder(self):
        msg = {"title": 'Onay İçin Gönderildi!!',
               "body": 'Ögretim elemanı zaman tablosu onay için Bölüm Başkanına gönderildi.'}

        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgilendirme(self):
        pass

    # Lane Gecisi Bolum Baskani

    def onay_ekrani(self):
        pass

    def reddet_ve_geri_gonder(self):
        pass

    def onayla(self):
        pass


class DerslikZamanTablosu(CrudView):
    pass

# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.views.crud import CrudView
from ulakbus.models.ders_programi import OgElemaniZamanPlani, ZamanCetveli, ZamanDilimleri, DerslikZamanPlani
from ulakbus.models import Room


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

    def derslik_sec(self):
        try:
            if self.current.secili_derslik:
                self.current.room = Room.objects.get(self.current.secili_derslik)
        except AttributeError:
            self.current.room = Room.objects.raw("room_departments.unit_id:" + self.current.role.unit.key)

    def listele(self):
        """
        Creates a message for the given channel.
        .. code-block:: python
            # response:
            {
                'derslik': {
                    'derslik_key': string   # ogretim_elemani_key
                    'name': string,     # name surname,
                    'kapasite': int,   # hours,
                    'zaman_plani': [{
                        'key': string,     # zaman_cetveli_key
                        'saat': string,  # 10:00-12:00,
                        'gun': int,     # 1 = pazartesi,
                        'durum': int    # 2 = Bolume Ait,
                        }]}
            }
        """

        dzps = sorted(DerslikZamanPlani.objects.filter(derslik=self.current.room),
                      key=lambda d: (d.gun, d.baslangic_saat, d.baslangic_dakika))

        zaman_plani = list()

        for dz in dzps:
            durum = dict()
            durum['key'] = dz.key
            durum['saat'] = dz.baslangic_saat + ':' + dz.baslangic_dakika + '-' + dz.bitis_saat + ':' + dz.bitis_dakika
            durum['gun'] = dz.gun
            durum['durum'] = dz.derslik_durum
            zaman_plani.append(durum)

        item = {'derslik_key': self.current.room.key,
                'name': self.current.room.name,
                'kapasite': self.current.room.capacity,
                'zaman_plani': zaman_plani}

        self.output['derslik_zaman_tablosu'] = item

    def degisiklikleri_kaydet(self):
        """"

        # request:
        {
            'change':{
                'key': string   # key,
                'durum': int    # 1 = uygun,
                'cmd': 'kaydet'}
        }

        """
        change = self.current.input['change']
        key = change['key']
        dz = DerslikZamanPlani.objects.get(key)
        dz.derslik_durum = change['durum']
        dz.save()

    def derslik_degistir(self):
        """

        # request:
        {
            'secili_derslik':{
                'key': string   #  personel key,
                'cmd': 'derslik_degistir'}
        }

        """
        self.current.secili_derslik = self.current.input['secili_derslik']['key']

    def onaya_gonder(self):
        msg = {"title": 'Onay İçin Gönderildi!!',
               "body": 'Derslik zaman tablosu onay için Bölüm Başkanına gönderildi.'}

        self.current.output['msgbox'] = msg
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onay_ekrani(self):
        pass

    def reddet_ve_geri_gonder(self):
        pass

    def onayla(self):
        pass

    def bilgilendirme(self):
        pass

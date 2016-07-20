# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from ulakbus.models.ders_programi import OgElemaniZamanPlani, ZamanCetveli, DerslikZamanPlani
from ulakbus.models import Room


class ZamanTablo(CrudView):

    def ogretim_gorevlisi_sec(self):
        """

        # request:
        {
            'secili_og_elemani':{
                'key': string   #  personel key,
                'cmd': 'personel_sec'}
        }

        """
        # default select first person
        try:
            if self.current.task_data['cmd'] == 'personel_sec':
                self.current.task_data['ogretim_elemani_key'] = self.current.input['secili_og_elemani']['key']
            elif self.current.task_data['cmd'] == 'hayir':
                pass
            else:
                self.current.task_data['ogretim_elemani_key'] = \
                    (OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)[0]).key
        except:
            self.current.task_data['ogretim_elemani_key'] = \
                (OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)[0]).key

    def zaman_tablosu_listele(self):
        """
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
        try:
            if self.current.task_data['red_aciklamasi']:
                self.current.output['msgbox'] = {"type": "warning",
                                                 "title": "Talebiniz Bolum Baskani Tarafindan Reddedildi",
                                                 "msg": self.current.task_data['red_aciklamasi']}
        except KeyError:
            pass

        self.current.ogretim_elemani = OgElemaniZamanPlani.objects.get(self.current.task_data['ogretim_elemani_key'])
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
        _form = JsonForm()
        _form.gonder = fields.Button('Onaya Gonder', cmd='onaya_gonder')
        self.form_out(_form)

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

    def onaya_gonder(self):
        _form = JsonForm(title='Ogretim Elemani Ders Programini Bolum Baskanina yollamak istiyor musunuz?')
        _form.evet = fields.Button('Evet', cmd='evet')
        _form.hayir = fields.Button('Hayir', cmd='hayir')
        self.form_out(_form)

    def mesaj(self):
        msg = {"title": 'Onay Icin Gonderildi!',
               "body": 'Talebiniz Basariyla iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgilendirme(self):
        msg = {"type": "info",
               "title": 'Talebiniz Onaylandi!',
               "msg": 'Gonderdiginiz ogretim elemani zaman tablosu Bolum Baskani tarafindan onaylandi'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.output['msgbox'] = msg

    # Lane Gecisi Bolum Baskani
    def onay_ekrani(self):
        """
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
        self.current.ogretim_elemani = OgElemaniZamanPlani.objects.get(self.current.task_data['ogretim_elemani_key'])
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
        _form = JsonForm()
        _form.onayla = fields.Button('Onayla', cmd='onay')
        _form.reddet = fields.Button('Reddet', cmd='reddet')
        self.form_out(_form)

    def kontrol_et(self):
        """

        # request:
        {
            'secili_og_elemani':{
                'key': string   #  personel key,
                'cmd': 'kontrol'}
        }

        """
        # default select first person
        try:
            if self.current.task_data['cmd'] == 'kontrol':
                self.current.task_data['ogretim_elemani_key'] = self.current.input['secili_og_elemani']['key']
            else:
                self.current.task_data['ogretim_elemani_key'] = \
                    (OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)[0]).key
        except:
            self.current.task_data['ogretim_elemani_key'] = \
                (OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)[0]).key

    def aciklama_yaz(self):
        _form = JsonForm()
        _form.mesaj = fields.String('Aciklama')
        _form.gonder = fields.Button('gonder')
        self.form_out(_form)

    def red_aciklamasini_gonder(self):
        self.current.task_data['red_aciklamasi'] = self.current.input['form']['mesaj']
        msg = {"title": 'Red Aciklamasi Gonderildi!',
               "body": 'Isleminiz basariyla gerceklesmistir'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onayla(self):
        msg = {"title": 'Ogretim Elemani Zaman Tablosunu Onayladiniz!',
               "body": 'Bolum ders programi koordinatorune onaylama iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg


class DerslikZamanTablosu(CrudView):

    def derslik_sec(self):
        """

        # request:
        {
            'secili_derslik':{
                'key': string   #  derslik key,
                'cmd': 'derslik_degistir'}
        }

        """
        try:
            if self.current.task_data['cmd'] == 'derslik_degistir':
                self.current.task_data['room_key'] = self.current.input['secili_derslik']['key']
            elif self.current.task_data['cmd'] == 'hayir':
                pass
            else:
                self.current.task_data['room_key'] = Room.objects.raw("room_departments.unit_id:" +
                                                                      self.current.role.unit.key)[0].key
        except:
            self.current.task_data['room_key'] = Room.objects.raw("room_departments.unit_id:" +
                                                                  self.current.role.unit.key)[0].key

    def listele(self):
        """
        .. code-block:: python
            # response:
            {
                'derslik_zaman_tablosu': {
                    'derslik_key': string   # derslik key
                    'name': string,     # room name,
                    'kapasite': int,   # capacity,
                    'zaman_plani': [{
                        'key': string,     # derslik zaman plani key
                        'saat': string,  # 10:00-12:00,
                        'gun': int,     # 1 = pazartesi,
                        'durum': int    # 2 = Bolume Ait,
                        }]}
            }
        """

        try:
            if self.current.task_data['red_aciklamasi']:
                self.current.output['msgbox'] = {"type": "warning",
                                                 "title": "Talebiniz Bolum Baskani Tarafindan Reddedildi",
                                                 "msg": self.current.task_data['red_aciklamasi']}
        except KeyError:
            pass

        self.current.room = Room.objects.get(self.current.task_data['room_key'])
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
        _form = JsonForm()
        _form.gonder = fields.Button('Onaya Gonder', cmd='onaya_gonder')
        self.form_out(_form)

    def degisiklikleri_kaydet(self):
        """"

        # request:
        {
            'change':{
                'key': string   # key,
                'durum': int    # 1 = Herkese Acik,
                'cmd': 'kaydet'}
        }

        """
        change = self.current.input['change']
        key = change['key']
        dz = DerslikZamanPlani.objects.get(key)
        dz.derslik_durum = change['durum']
        dz.save()

    def onaya_gonder(self):
        _form = JsonForm(title='Derslik Ders Programini Bolum Baskanina yollaman istiyor musunuz?')
        _form.evet = fields.Button('Evet', cmd='evet')
        _form.hayir = fields.Button('Hayir', cmd='hayir')
        self.form_out(_form)

    def mesaj(self):
        msg = {"title": 'Onay Icin Gonderildi!',
               "body": 'Talebiniz Basariyla iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def kontrol_et(self):
        """

        # request:
        {
            'secili_derslik':{
                'key': string   #  derslik key,
                'cmd': 'kontrol'}
        }

        """
        try:
            if self.current.task_data['cmd'] == 'kontrol':
                self.current.task_data['room_key'] = self.current.input['secili_derslik']['key']
            elif self.current.task_data['cmd'] == 'hayir':
                pass
            else:
                self.current.task_data['room_key'] = Room.objects.raw("room_departments.unit_id:" +
                                                                      self.current.role.unit.key)[0].key
        except:
            self.current.task_data['room_key'] = Room.objects.raw("room_departments.unit_id:" +
                                                                  self.current.role.unit.key)[0].key

    def onay_ekrani(self):
        """
        .. code-block:: python
            # response:
            {
                'derslik_zaman_tablosu': {
                    'derslik_key': string   # derslik key
                    'name': string,     # room name,
                    'kapasite': int,   # capacity,
                    'zaman_plani': [{
                        'key': string,     # derslik zaman plani key
                        'saat': string,  # 10:00-12:00,
                        'gun': int,     # 1 = pazartesi,
                        'durum': int    # 2 = Bolume Ait,
                        }]}
            }
        """
        self.current.room = Room.objects.get(self.current.task_data['room_key'])
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
        _form = JsonForm()
        _form.onayla = fields.Button('Onayla', cmd='onay')
        _form.reddet = fields.Button('Reddet', cmd='reddet')
        self.form_out(_form)

    def red_aciklama_yaz(self):
        _form = JsonForm()
        _form.mesaj = fields.String('Aciklama')
        _form.gonder = fields.Button('gonder')
        self.form_out(_form)

    def geri_gonder(self):
        self.current.task_data['red_aciklamasi'] = self.current.input['form']['mesaj']
        msg = {"title": 'Red Aciklamasi Gonderildi!',
               "body": 'Isleminiz basariyla gerceklesmistir'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onayla(self):
        msg = {"title": 'Derslik Zaman Tablosunu Onayladiniz!',
               "body": 'Bolum ders programi koordinatorune onaylama iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgilendirme(self):
        msg = {"type": "info",
               "title": 'Talebiniz Onaylandi!',
               "msg": 'Gonderdiginiz derslik zaman tablosu Bolum Baskani tarafindan onaylandi'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.output['msgbox'] = msg


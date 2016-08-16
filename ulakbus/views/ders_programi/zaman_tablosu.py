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
from ulakbus.models.ders_sinav_programi import OgElemaniZamanPlani, ZamanCetveli, DerslikZamanPlani, ZamanDilimleri
from ulakbus.models import Room


class ZamanTablo(CrudView):
    """
    .. code-block:: python
        # default_request:
        {
            'callbackID': string,
            'client_cmd':['string',],
            'forms': {},
            'meta': {},
            'reload_cmd': string,
            'reply_timestamp': float
            'token': string
        },

        # default_response
        {
            'callbackID': string,
            'data': {
                'form': {},
                'cmd': string,
                'token': string,
                'wf': string,
        }

    """

    def ogretim_elemani_listele(self):
        oe_zaman_plani = OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)
        ogretim_elemanlari = list()

        for oe in oe_zaman_plani:
            ogretim_elemani = dict()
            ogretim_elemani['name'] = oe.okutman.ad + ' ' + oe.okutman.soyad
            ogretim_elemani['key'] = oe.key
            ogretim_elemanlari.append(ogretim_elemani)

        return ogretim_elemanlari

    def ogretim_elemani_zaman_tablosu(self):

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

        item = {'avatar': self.current.ogretim_elemani.okutman.personel.user.get_avatar_url(),
                'oe_key': self.current.ogretim_elemani.key,
                'name': self.current.ogretim_elemani.okutman.ad + ' ' + self.current.ogretim_elemani.okutman.soyad,
                'toplam_ders_saati': self.current.ogretim_elemani.toplam_ders_saati,
                'uygunluk_durumu': uygunluk_durumu,
                'ogretim_elemanlari': self.ogretim_elemani_listele()}

        self.output['ogretim_elemani_zt'] = item

    def ogretim_gorevlisi_sec(self):
        """
        Switch lecturer or select default one
        .. code-block:: python
            # request:
            {
                'secili_og_elemani':{
                    'key': string   #  personel key,
                    'cmd': 'personel_sec'}
            }

            # response:
            {
                'ders_saati_durum': Boolean
            }

        """
        # default select first person
        try:
            if self.current.task_data['cmd'] == 'personel_sec':
                zaman_dilimleri = ZamanDilimleri.objects.filter(birim=self.current.role.unit)
                ogretim_elemani = OgElemaniZamanPlani.objects.get(self.current.task_data['ogretim_elemani_key'])
                zaman_cetveli = ZamanCetveli.objects.filter(ogretim_elemani_zaman_plani=ogretim_elemani, durum=3)

                toplam_ders_saat = 0
                for zd in zaman_dilimleri:
                    toplam_ders_saat += (zd.zaman_dilimi_suresi * 5)

                time = 0
                for zc in zaman_cetveli:
                    if zc.gun not in [6, 7]:
                        time += zc.zaman_dilimi.zaman_dilimi_suresi
                oe_ders_saati = int(ogretim_elemani.toplam_ders_saati + (ogretim_elemani.toplam_ders_saati/2))
                if time <= (toplam_ders_saat - oe_ders_saati):
                    self.current.task_data['ogretim_elemani_key'] = self.current.input['secili_og_elemani']['key']
                    self.current.output['ders_saati_durum'] = True
                else:
                    self.current.output['ders_saati_durum'] = False

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
        show & edit timetable for lecturer

        .. code-block:: python
            # response:
            {
                'ogretim_elemani_zt': {
                    'avatar': string,
                    'oe_key': string   # ogretim_elemani_key
                    'name': string,     # name surname,
                    'toplam_ders_saati': int,   # hours,
                    'uygunluk_durumu': [{
                        'key': string,     # zaman_cetveli_key
                        'saat': string,  # 10:00-12:00,
                        'gun': int,     # 1 = pazartesi,
                        'durum': int    # 2 = mumkunse uygun degil,
                        }],
                    'ogretim_elemanlari': [{
                        'name': string,
                        'key': string}]}
            }
        """
        try:
            if self.current.task_data['red_aciklamasi']:
                self.current.output['msgbox'] = {"type": "warning",
                                                 "title": "Talebiniz Bölüm Başkanı Tarafından Reddedildi",
                                                 "msg": self.current.task_data['red_aciklamasi']}
        except KeyError:
            pass

        self.ogretim_elemani_zaman_tablosu()

        _form = JsonForm()
        _form.gonder = fields.Button('Onaya Gönder', cmd='onaya_gonder')
        self.form_out(_form)

    def zaman_degisiklik_kaydet(self):
        """"
        save timetable state when user switches lecturer's availability  options

        .. code-block:: python
            # request:
            {
                'change':{
                    'key': string   # key,
                    'durum': int    # 1 = uygun,
                    'cmd': 'degistir'}
            }

            # response:
            {
                'kayit_durum': Boolean
            }

        """
        try:
            change = self.current.input['change']
            key = change['key']
            zc = ZamanCetveli.objects.get(key)
            zc.durum = change['durum']
            zc.save()
            kayit_durum = True
        except:
            kayit_durum = False

        self.current.output['kayit_durum'] = kayit_durum

    def onaya_gonder(self):
        _form = JsonForm(title='Öğretim Elemanı Ders Programını Bölüm Başkanına yollamak istiyor musunuz?')
        _form.evet = fields.Button('Evet', cmd='evet')
        _form.hayir = fields.Button('Hayır', cmd='hayir')
        self.form_out(_form)

    def mesaj(self):
        msg = {"title": 'Onay İçin Gonderildi!',
               "body": 'Talebiniz Başarıyla iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgilendirme(self):
        msg = {"type": "info",
               "title": 'Talebiniz Onaylandı!',
               "msg": 'Gönderdiğiniz öğretim elemanı zaman tablosu Bölüm Başkanı tarafından onaylandı.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.output['msgbox'] = msg

    # Lane Gecisi Bolum Baskani
    def onay_ekrani(self):
        """
        read only control and approve screen

        .. code-block:: python
            # response:
            {
                default_response,
                'ogretim_elemani_zt': {
                    'oe_key': string   # ogretim_elemani_key
                    'name': string,     # name surname,
                    'toplam_ders_saati': int,   # hours,
                    'uygunluk_durumu': [{
                        'key': string,     # zaman_cetveli_key
                        'saat': string,  # 10:00-12:00,
                        'gun': int,     # 1 = pazartesi,
                        'durum': int    # 2 = mumkunse uygun degil,
                        }],
                    'ogretim_elemanlari': [{
                        'name': string,
                        'key': string}]}
            }
        """

        self.ogretim_elemani_zaman_tablosu()
        self.output['ogretim_elemani_zt']['readonly'] = True

        _form = JsonForm()
        _form.onayla = fields.Button('Onayla', cmd='onay')
        _form.reddet = fields.Button('Reddet', cmd='reddet')
        self.form_out(_form)

    def kontrol_et(self):
        """
        Switch lecturer or select default one

        .. code-block:: python
            # request:
            {
                'secili_og_elemani':{
                    'key': string   #  personel key,
                    'cmd': string}
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
        _form.mesaj = fields.String('Açıklama')
        _form.gonder = fields.Button('gonder')
        self.form_out(_form)

    def red_aciklamasini_gonder(self):
        self.current.task_data['red_aciklamasi'] = self.current.input['form']['mesaj']
        msg = {"title": 'Red Açıklaması Gönderildi!',
               "body": 'İşleminiz başarıyla gerçekleşmiştir'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onayla(self):
        msg = {"title": 'Öğretim Elemani Zaman Tablosunu Onayladınız!',
               "body": 'Bölüm ders programı koordinatörüne onaylama iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg


class DerslikZamanTablosu(CrudView):
    """
    .. code-block:: python
        # default_response:
        {
            'callbackID': string,
            'client_cmd':['string',],
            'forms': {},
            'meta': {},
            'reload_cmd': string,
            'reply_timestamp': float
            'token': string
        },

        # default_request
        {
            'callbackID': string,
            'data': {
                'form': {},
                'cmd': string,
                'token': string,
                'wf': string,
        }

    """

    def derslik_listele(self):
        rooms = Room.objects.raw("room_departments.unit_id:" + self.current.role.unit.key)
        derslikler = list()
        for room in rooms:
            derslik = dict()
            derslik['name'] = room.name
            derslik['key'] = room.key
            derslikler.append(derslik)
        return derslikler

    def derslik_sec_kontrol(self, cmd=''):
        """
        Switch room or select default one

        .. code-block:: python
            # request:
            {
                'secili_derslik':{
                    'key': string   #  derslik key,
                    'cmd': 'derslik_degistir'}
            }

        """
        try:
            if self.current.task_data['cmd'] == cmd:
                self.current.task_data['room_key'] = self.current.input['secili_derslik']['key']
            elif self.current.task_data['cmd'] == 'hayir':
                pass
            else:
                self.current.task_data['room_key'] = Room.objects.raw("room_departments.unit_id:" +
                                                                      self.current.role.unit.key)[0].key
        except:
            self.current.task_data['room_key'] = Room.objects.raw("room_departments.unit_id:" +
                                                                  self.current.role.unit.key)[0].key

    def derslik_zaman_tablosu(self):
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
                'zaman_plani': zaman_plani,
                'derslikler': self.derslik_listele()}

        self.output['derslik_zaman_tablosu'] = item

    def derslik_sec(self):
        self.derslik_sec_kontrol('derslik_degistir')

    def listele(self):
        """
        show & edit timetable for room

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
                        }],
                    'derslikler': [{
                        'name': string,
                        'key': string}]}
            }
        """

        try:
            if self.current.task_data['red_aciklamasi']:
                self.current.output['msgbox'] = {"type": "warning",
                                                 "title": "Talebiniz Bölüm Başkanı Tarafından Reddedildi",
                                                 "msg": self.current.task_data['red_aciklamasi']}
        except KeyError:
            pass

        self.derslik_zaman_tablosu()

        _form = JsonForm()
        _form.gonder = fields.Button('Onaya Gönder', cmd='gonder')
        self.form_out(_form)

    def degisiklikleri_kaydet(self):
        """"
        save timetable state when user switches room's availability  options

        .. code-block:: python
            # request:
            {
                'change':{
                    'key': string   # key,
                    'durum': int    # 1 = Herkese Acik,
                    'cmd': 'kaydet'}
            }

             # response:
            {
                'kayit_durum': Boolean
            }

        """

        try:
            change = self.current.input['change']
            key = change['key']
            dz = DerslikZamanPlani.objects.get(key)
            dz.derslik_durum = change['durum']
            dz.save()
            kayit_durum = True
        except:
            kayit_durum = False

        self.current.output['kayit_durum'] = kayit_durum

    def onaya_gonder(self):
        _form = JsonForm(title='Derslik Ders Programını Bölüm Başkanına yollamak istiyor musunuz?')
        _form.evet = fields.Button('Evet', cmd='evet')
        _form.hayir = fields.Button('Hayir', cmd='hayir')
        self.form_out(_form)

    def mesaj(self):
        msg = {"title": 'Onay İçin Gönderildi!',
               "body": 'Talebiniz Başarıyla iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def kontrol_et(self):
        self.derslik_sec_kontrol('kontrol')

    def onay_ekrani(self):
        """
        read only control and approve screen

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
                        }],
                    'derslikler': [{
                        'name': string,
                        'key': string}]}
            }
        """


        self.derslik_zaman_tablosu()
        self.output['derslik_zaman_tablosu']['readonly'] = True

        _form = JsonForm()
        _form.onayla = fields.Button('Onayla', cmd='onay')
        _form.reddet = fields.Button('Reddet', cmd='reddet')
        self.form_out(_form)

    def red_aciklama_yaz(self):
        _form = JsonForm()
        _form.mesaj = fields.String('Açıklama')
        _form.gonder = fields.Button('gonder')
        self.form_out(_form)

    def geri_gonder(self):
        self.current.task_data['red_aciklamasi'] = self.current.input['form']['mesaj']
        msg = {"title": 'Red Açıklaması Gönderildi!',
               "body": 'İşleminiz başarıyla gerçeklesmistir'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def onayla(self):
        msg = {"title": 'Derslik Zaman Tablosunu Onayladınız!',
               "body": 'Bölüm ders programı koordinatörüne onaylama iletildi.'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgilendirme(self):
        msg = {"type": "info",
               "title": 'Talebiniz Onaylandı!',
               "msg": 'Gönderdiğiniz derslik zaman tablosu Bölüm Başkanı tarafından onaylandı'}
        # workflowun bu kullanıcı için bitişinde verilen mesajı ekrana bastırır

        self.current.output['msgbox'] = msg


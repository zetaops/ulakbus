# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from datetime import time
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, format_time, gettext_lazy
from ulakbus.models.ders_sinav_programi import OgElemaniZamanPlani, ZamanCetveli, DerslikZamanPlani, ZamanDilimleri
from ulakbus.models import Room, DerslikSinavPlani


class OnayForm(JsonForm):
    onayla = fields.Button(gettext_lazy(u'Onayla'), cmd='onay')
    reddet = fields.Button(gettext_lazy(u'Reddet'), cmd='reddet')


class ZamanTablosu(CrudView):
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

    def derslik_sec_kontrol(self, cmd='', obj=None):
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
                self.current.task_data['rooms'] = list(set(obj.objects.filter(
                                                        birim=self.current.role.unit).values_list('derslik_id')))
                self.current.task_data['room_key'] = self.current.task_data['rooms'][0]
        except:
            self.current.task_data['rooms'] = list(set(obj.objects.filter(
                                                        birim=self.current.role.unit).values_list('derslik_id')))
            self.current.task_data['room_key'] = self.current.task_data['rooms'][0]

    def derslik_sec(self):
        self.derslik_sec_kontrol('derslik_degistir', DerslikZamanPlani)

    def sinav_derslik_sec(self):
        self.derslik_sec_kontrol('derslik_degistir', DerslikSinavPlani)

    def ogretim_elemani_listele(self):
        oe_zaman_plani = OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)
        ogretim_elemanlari = list()
        for oe in oe_zaman_plani:
            ogretim_elemani = dict()
            ogretim_elemani['name'] = oe.okutman.ad + ' ' + oe.okutman.soyad
            ogretim_elemani['key'] = oe.key
            ogretim_elemanlari.append(ogretim_elemani)

        return ogretim_elemanlari

    def sinav_derslik_listele(self):
        rooms = self.current.task_data['rooms']
        return self.derslikler(rooms)

    def derslik_listele(self):
        rooms = self.current.task_data['rooms']
        return self.derslikler(rooms)

    def derslikler(self, rooms):
        derslikler_list = list()
        for room in rooms:
            r = Room.objects.get(room)
            derslik = dict()
            derslik['name'] = r.name
            derslik['key'] = r.key
            derslikler_list.append(derslik)
        return derslikler_list

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

        if 'red_aciklamasi' in self.current.task_data:
            self.current.output['msgbox'] = {"type": "warning",
                                             "title": _(u"Talebiniz Bölüm Başkanı Tarafından Reddedildi"),
                                             "msg": self.current.task_data['red_aciklamasi']}
        _form = JsonForm()
        _form.gonder = fields.Button(_(u'Onaya Gönder'), cmd='gonder')
        self.form_out(_form)

    def ogretim_elemani_zt(self):

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
        self.listele()

    def derslik_zt(self):
        self.current.room = Room.objects.get(self.current.task_data['room_key'])
        dzps = sorted(DerslikZamanPlani.objects.filter(derslik=self.current.room),
                      key=lambda d: (d.gun, d.baslangic_saat, d.baslangic_dakika))

        zaman_plani = list()

        for dz in dzps:
            durum = dict()
            durum['key'] = dz.key
            durum['saat'] = '{baslangic}-{bitis}'.format(
                baslangic=format_time(time(int(dz.baslangic_saat), int(dz.baslangic_dakika))),
                bitis=format_time(time(int(dz.bitis_saat), int(dz.bitis_dakika))),
            )
            durum['gun'] = dz.gun
            durum['durum'] = dz.durum
            zaman_plani.append(durum)

        item = {'derslik_key': self.current.room.key,
                'name': self.current.room.name,
                'kapasite': self.current.room.capacity,
                'zaman_plani': zaman_plani,
                'derslikler': self.derslik_listele()}

        self.output['derslik_zaman_tablosu'] = item
        self.listele()

    def sinav_derslik_zt(self):
        room = Room.objects.get(self.current.task_data['room_key'])
        dsp = DerslikSinavPlani.objects.filter(derslik=room)
        zaman_plani = list()

        for dz in dsp:
            durum = dict()
            durum['key'] = dz.key
            durum['saat'] = dz.zaman_dilimi.baslama_saat + ':' + dz.zaman_dilimi.baslama_dakika + '-' + \
                            dz.zaman_dilimi.bitis_saat + ':' + dz.zaman_dilimi.bitis_dakika
            durum['gun'] = dz.gun
            durum['durum'] = dz.durum
            zaman_plani.append(durum)

        item = {'derslik_key': room.key,
                'name': room.name,
                'kapasite': room.exam_capacity,
                'zaman_plani': zaman_plani,
                'derslikler': self.sinav_derslik_listele()}

        self.output['derslik_zaman_tablosu'] = item
        self.listele()


    def sinav_degisiklik_kaydet(self):
        self.save_changes(DerslikSinavPlani, self.current.input['change'])
        kayit_durum = True
        self.current.output['kayit_durum'] = kayit_durum

    def zaman_degisiklik_kaydet(self):
        self.save_changes(ZamanCetveli, self.current.input['change'])
        kayit_durum = True
        self.current.output['kayit_durum'] = kayit_durum

    def derslik_degisiklik_kaydet(self):
        self.save_changes(DerslikZamanPlani, self.current.input['change'])
        kayit_durum = True
        self.current.output['kayit_durum'] = kayit_durum

    def save_changes(self, model, change):
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
        obj = model.objects.get(change['key'])
        obj.durum = change['durum']
        obj.save()

    def onaya_gonder(self):
        _form = JsonForm(title=_(u'Programı Bölüm Başkanına yollamak istiyor musunuz?'))
        _form.evet = fields.Button(_(u'Evet'), cmd='evet')
        _form.hayir = fields.Button(_(u'Hayır'), cmd='hayir')
        self.form_out(_form)

    def mesaj(self):
        msg = {"title": _(u'Onay İçin Gönderildi!'),
               "body": _(u'Talebiniz Başarıyla iletildi.')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def ogretim_gorevlisi_kontrol_et(self):
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
        if 'cmd' in self.current.task_data and self.current.task_data['cmd'] == 'kontrol':
            self.current.task_data['ogretim_elemani_key'] = self.current.input['secili_og_elemani']['key']
        else:
            self.current.task_data['ogretim_elemani_key'] = \
                (OgElemaniZamanPlani.objects.filter(birim=self.current.role.unit)[0]).key

    def derslik_kontrol_et(self):
        self.derslik_sec_kontrol('kontrol', DerslikZamanPlani)

    def sinav_derslik_kontrol_et(self):
        self.derslik_sec_kontrol('kontrol', DerslikSinavPlani)

    def ogretim_elemani_onay_ekrani(self):
        if 'red_aciklamasi' in self.current.task_data:
            del(self.current.task_data['red_aciklamasi'])
        self.ogretim_elemani_zt()
        self.output['ogretim_elemani_zt']['readonly'] = True
        self.form_out(OnayForm())

    def derslik_onay_ekrani(self):
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

        if 'red_aciklamasi' in self.current.task_data:
            del(self.current.task_data['red_aciklamasi'])
        self.derslik_zt()
        self.output['derslik_zaman_tablosu']['readonly'] = True
        self.form_out(OnayForm())

    def sinav_derslik_onay_ekrani(self):
        if 'red_aciklamasi' in self.current.task_data:
            del(self.current.task_data['red_aciklamasi'])
        self.sinav_derslik_zt()
        self.output['derslik_zaman_tablosu']['readonly'] = True
        self.form_out(OnayForm())

    def red_aciklama_yaz(self):
        _form = JsonForm()
        _form.mesaj = fields.String(_(u'Açıklama'))
        _form.gonder = fields.Button(_(u'Gönder'))
        self.form_out(_form)

    def red_aciklamasini_gonder(self):
        self.current.task_data['red_aciklamasi'] = self.current.input['form']['mesaj']
        msg = {"title": _(u'Red Açıklaması Gönderildi!'),
               "body": _(u'İşleminiz başarıyla gerçeklesmistir')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg

    def bilgilendirme(self):
        msg = {"type": "info",
               "title": _(u'Talebiniz Onaylandı!'),
               "msg": _(u'Gönderdiğiniz zaman tablosu Bölüm Başkanı tarafından onaylandı.')}

        self.current.output['msgbox'] = msg

    def onayla(self):
        msg = {"title": _(u'Zaman Tablosunu Onayladınız!'),
               "body": _(u'Bölüm ders programı koordinatörüne onaylama iletildi.')}

        self.current.task_data['LANE_CHANGE_MSG'] = msg
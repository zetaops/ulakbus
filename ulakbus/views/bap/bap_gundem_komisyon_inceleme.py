# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.views.bap.bap_gundem import Gundem

from zengine.forms import JsonForm
from zengine.forms import fields
from .proje_talep.bap_ek_sure_talep import EkSureTalebi
from .proje_talep.bap_proje_iptal_talep import ProjeIptal
from .proje_talep.bap_ek_butce_talep import EkButceTalep
from .proje_talep.bap_yurutucu_degisikligi_talebi import YurutucuDegisikligi

from ulakbus.models import BAPGundem, BAPButcePlani

from zengine.views.crud import obj_filter, CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __

import json


class BitirForm(JsonForm):

    bitir = fields.Button(__(u"Bitir"))


class GundemIncele(EkSureTalebi, ProjeIptal, YurutucuDegisikligi):

    def gundemleri_listele(self):
        gundemler = BAPGundem.objects.all(sonuclandi=False)
        self.output['objects'] = [['Projenin Adı', 'Proje Yürütücüsü', 'Gündem Tipi']]
        for gundem in gundemler:
            item = {
                "fields": [gundem.proje.ad,
                           gundem.proje.yurutucu.__unicode__(),
                           gundem.get_gundem_tipi_display()],
                "actions": [{'name': _(u'Göster'), 'cmd': '', 'mode': 'normal',
                            'show_as': 'button'}],
                'key': gundem.key
            }
            self.output['objects'].append(item)

    def is_akisini_cagir(self):
        gundem_kararlari = {
            1: 'basvuru',
            2: 'ek_butce',
            3: 'fasil',
            4: 'ek_sure',
            5: 'sonuc_rapor',
            6: 'donem_rapor',
            7: 'iptal',
            8: 'yurutucu'
        }
        gundem = BAPGundem.objects.get(self.input['object_id'])
        self.current.task_data['object_id'] = self.input['object_id']
        self.current.task_data['bap_proje_id'] = gundem.proje.key
        self.current.task_data['cmd'] = gundem_kararlari[gundem.gundem_tipi]

    def iptal_talebini_goruntule(self):
        gundem = BAPGundem.objects.get(self.input['object_id'])
        self.current.task_data['proje_iptal_aciklama'] = gundem.gundem_aciklama
        self.object = gundem.proje
        ProjeIptal.iptal_talebini_goruntule(self)
        self.form_out(BitirForm(title=_(u"Proje iptal talebi : %s") %
                                gundem.proje.ad))

    def degisiklik_talebini_goruntule(self):
        gundem = BAPGundem.objects.get(self.current.task_data['object_id'])
        data = json.loads(gundem.gundem_ekstra_bilgiler)

        self.current.task_data['yeni_yurutucu_id'] = data['yeni_yurutucu_id']
        self.current.task_data['yurutucu_aciklama'] = gundem.gundem_aciklama

        YurutucuDegisikligi.degisiklik_talebini_goruntule(self)

        self.form_out(BitirForm(title=_(u"Proje: %s - Yürütücü Değişikliği Talebi") %
                                gundem.proje.ad))

    def ek_sure_talebi_goruntule(self):
        gundem = BAPGundem.objects.get(self.current.task_data['object_id'])
        data = json.loads(gundem.gundem_ekstra_bilgiler)
        self.current.task_data['ek_sure'] = data['ek_sure']
        self.current.task_data['aciklama'] = data['aciklama']
        EkSureTalebi.ek_sure_talebi_goruntule(self)
        self.form_out(BitirForm(title=_(u"Yürütücü: %s / Proje: %s - Ek süre talebi") % \
                                       (gundem.proje.yurutucu, gundem.proje.ad)))

    def ek_butce_talep_kontrol_goruntule(self):
        if 'gundem_object_id' not in self.current.task_data:
            self.current.task_data['gundem_object_id'] = self.current.task_data['object_id']

        gundem = BAPGundem.objects.get(self.current.task_data['object_id'])
        data = json.loads(gundem.gundem_ekstra_bilgiler)
        self.current.task_data['yeni_butceler'] = data['yeni_butceler']
        proje = gundem.proje
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s - Ek bütçe talebi") % \
                                       (proje.yurutucu, proje.ad)
        self.output['objects'] = [['Kod Adi', 'Ad', 'Eski Toplam Fiyati', 'Yeni Toplam Fiyati',
                                   'Durum']]
        for key, talep in data['yeni_butceler'].iteritems():
            item = {
                "fields": [talep['kod_ad'],
                           talep['ad'],
                           str(talep['eski_toplam_fiyat']),
                           str(talep['yeni_toplam_fiyat']),
                           talep['durum']],
                "actions": [{'name': _(u'Göster'), 'cmd': 'goster', 'mode': 'normal',
                             'show_as': 'button'}],
                'key': key
            }
            self.output['objects'].append(item)
        self.form_out(BitirForm(title=_(u"Yürütücü: %s / Proje: %s - Ek bütçe talebi") % \
                                       (gundem.proje.yurutucu, gundem.proje.ad), cmd='bitir'))

    def butce_detay_goster(self):
        obj = BAPButcePlani.objects.get(self.input['object_id'])
        self.object = obj
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s / Kalem: %s") % \
                                       (obj.ilgili_proje.yurutucu, obj.ilgili_proje.ad, self.object)

        data = self.current.task_data['yeni_butceler'][self.object.key]

        obj_data = {'Kalem Adı': data['ad'],
                    'Eski Adet': str(data['eski_adet']),
                    'Yeni Adet': str(data['yeni_adet']),
                    'Eski Birim Fiyat': str(data['eski_birim_fiyat']),
                    'Yeni Birim Fiyat': str(data['yeni_birim_fiyat']),
                    'Eski Toplam Fiyat': str(data['eski_toplam_fiyat']),
                    'Yeni Toplam Fiyat': str(data['yeni_toplam_fiyat']),
                    'Gerekçe': data['gerekce']}
        self.output['object'] = obj_data

        self.current.task_data['object_id'] = self.current.task_data['gundem_object_id']
        del self.current.task_data['gundem_object_id']
        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    @obj_filter
    def gundem_actions(self, obj, result, **kwargs):
        result['actions'] = ([{'name': _(u'Göster'),
                               'cmd': 'show',
                               'mode': 'normal',
                               'show_as': 'button'}])

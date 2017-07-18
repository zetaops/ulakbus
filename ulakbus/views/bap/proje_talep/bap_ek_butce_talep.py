# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import json

from collections import defaultdict
from ulakbus.models import BAPProje, BAPButcePlani, BAPGundem, Personel, Okutman
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _


talep_durum = [(1, 'Yeni'),
               (2, 'Silinecek'),
               (3, 'Düzenlendi'),
               (4, 'Düzenlenmedi')]


class EkButceTalep(CrudView):
    class Meta:
        model = 'BAPButcePlani'

    # ---------- Proje Yürütücüsü ----------
    def proje_id_kontrol(self):
        self.current.task_data['cmd'] = 'proje_id_var' if 'bap_proje_id' in self.current.task_data \
            else 'proje_id_yok'

    def kontrol(self):
        if 'bap_proje_id' in self.current.task_data and 'red_aciklama' not in \
                self.current.task_data and 'onay' not in self.current.task_data:
            self.current.task_data['onaylandi'] = 2
        else:
            personel = Personel.objects.get(user=self.current.user)
            okutman = Okutman.objects.get(personel=personel)
            if BAPProje.objects.filter(yurutucu=okutman).count() == 0:
                self.current.task_data['onaylandi'] = 1
                self.current.task_data['proje_yok'] = {'msg': 'Yürütücüsü olduğunuz herhangi bir proje '
                                                              'bulunamadı. Size bağlı olan proje '
                                                              'olmadığı için ek bütçe talebinde '
                                                              'bulunamazsınız.',
                                                       'title': 'Proje Bulunamadı'}
            elif 'red_aciklama' in self.current.task_data:
                self.current.task_data['onaylandi'] = 2
            elif 'onaylandi' not in self.current.task_data:
                self.current.task_data['onaylandi'] = 0

    def proje_sec(self):
        personel = Personel.objects.get(user=self.current.user)
        okutman = Okutman.objects.get(personel=personel)
        data = [(proje.key, proje.ad) for proje in BAPProje.objects.filter(yurutucu=okutman)]

        form = JsonForm(title=_(u"Proje Seçiniz"))
        form.proje = fields.String(choices=data)
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def list(self, custom_form=None, **kwargs):
        if 'yeni_butceler' not in self.current.task_data:
            self.current.task_data['yeni_butceler'] = defaultdict(dict)

        if 'form' in self.input and 'proje' in self.input['form']:
            self.current.task_data['bap_proje_id'] = self.input['form']['proje']

        self.output['objects'] = [['Muhasebe Kodu', 'Kod Adı', 'Alınacak Malzemenin Adı',
                                   'Birim Fiyat', 'Adet', 'Toplam Fiyat', 'Durum']]

        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        butce_planlari = BAPButcePlani.objects.all(ilgili_proje=proje)
        toplam = 0
        for butce in butce_planlari:
            if butce.key not in self.current.task_data['yeni_butceler']:
                self.current.task_data['yeni_butceler'][butce.key] = {
                    'durum': talep_durum[3][1],
                    'kod_ad': butce.kod_adi,
                    'ad': butce.ad,
                    'eski_adet': butce.adet,
                    'yeni_adet': '',
                    'eski_birim_fiyat': butce.birim_fiyat,
                    'yeni_birim_fiyat': '',
                    'eski_toplam_fiyat': butce.toplam_fiyat,
                    'yeni_toplam_fiyat': '',
                    'gerekce': butce.gerekce
                }
            durum = self.current.task_data['yeni_butceler'][butce.key]['durum']
            toplam_fiyat = self.current.task_data['yeni_butceler'][butce.key]['yeni_toplam_fiyat']
            kontrol_durum = [talep_durum[1][1], talep_durum[3][1]]
            item = {
                "fields": [
                    butce.muhasebe_kod,
                    butce.kod_adi,
                    butce.ad,
                    str(self.current.task_data['yeni_butceler'][butce.key]['yeni_birim_fiyat'])
                    if durum not in kontrol_durum else str(butce.birim_fiyat),
                    str(self.current.task_data['yeni_butceler'][butce.key]['yeni_adet'])
                    if durum not in kontrol_durum else str(butce.adet),
                    str(self.current.task_data['yeni_butceler'][butce.key]['yeni_toplam_fiyat'])
                    if durum not in kontrol_durum else str(butce.toplam_fiyat),
                    durum],
                "actions": [{'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal',
                            'show_as': 'button'},
                            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal',
                             'show_as': 'button'},
                            {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal',
                             'show_as': 'button'}],
                'key': butce.key
            }
            self.output['objects'].append(item)
            toplam += toplam_fiyat if toplam_fiyat else butce.toplam_fiyat

        self.output['objects'].append({'fields': ['TOPLAM', '', '', '', '', str(toplam), ''],
                                       'actions': ''})

        form = JsonForm(title=_(u"%s - Bap Ek Bütçe Talep") % proje.ad)
        form.tamam = fields.Button(_(u"Onaya Yolla"))
        form.ekle = fields.Button(_(u"Ekle"), cmd='add_edit_form')
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)
        if 'red_aciklama' in self.current.task_data:
            self.current.msg_box(msg=self.current.task_data['red_aciklama'],
                                 title=_(u"Talebiniz Reddedildi."),
                                 typ='warning')
            del self.current.task_data['red_aciklama']

    def kaydet(self):
        if 'yeni_butceler' not in self.current.task_data:
            self.current.task_data['yeni_butceler'] = defaultdict(dict)

        if not self.object.key:
            self.object.ilgili_proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
            self.object.muhasebe_kod = self.current.task_data['muhasebe_kod']
            self.object.kod_adi = self.current.task_data['kod_adi']
            self.set_form_data_to_object()
            durum = talep_durum[0][1]
        else:
            durum = talep_durum[2][1]

        self.object.blocking_save()

        self.current.task_data['yeni_butceler'][self.object.key] = \
            {'durum': durum,
             'kod_ad': self.current.task_data['kod_adi'],
             'ad': self.object.ad,
             'eski_adet': self.object.adet if not durum == talep_durum[0][1] else '',
             'yeni_adet': self.input['form']['adet'],
             'eski_birim_fiyat': self.object.birim_fiyat if not durum == talep_durum[0][1] else '',
             'yeni_birim_fiyat': self.input['form']['birim_fiyat'],
             'eski_toplam_fiyat': self.object.toplam_fiyat if not durum == talep_durum[0][1] else '',
             'yeni_toplam_fiyat': self.input['form']['toplam_fiyat'],
             'gerekce': self.input['form']['gerekce']}

    def butce_kalemini_sil(self):
        if 'yeni_butceler' not in self.current.task_data:
            self.current.task_data['yeni_butceler'] = defaultdict(dict)

        durum = talep_durum[1][1]

        self.current.task_data['yeni_butceler'][self.object.key] = \
            {'durum': durum,
             'kod_ad': self.object.kod_adi,
             'ad': self.object.ad,
             'eski_adet': self.object.adet,
             'yeni_adet': '',
             'eski_birim_fiyat': self.object.birim_fiyat,
             'yeni_birim_fiyat': '',
             'eski_toplam_fiyat': self.object.toplam_fiyat,
             'yeni_toplam_fiyat': '',
             'gerekce': self.object.gerekce}

    def onaya_yolla(self):
        duzenlenen = False
        for key, talep in self.current.task_data['yeni_butceler'].iteritems():
            if not talep['durum'] == 'Düzenlenmedi':
                duzenlenen = True
                break

        if 'yeni_butceler' not in self.current.task_data or not duzenlenen:
            self.current.task_data['cmd'] = 'talep_yok'
            self.current.output['msgbox'] = {
                'type': 'warning', "title": _(u'Ek Bütçe Talebi'),
                "msg": _(u'Ek bütçe talebinde bulunmanız için var olan kalemlerinizde '
                         u'değişiklikler yapmalısınız.')}

    def sonuc(self):
        if 'proje_yok' in self.current.task_data:
            self.current.msg_box(msg=self.current.task_data['proje_yok']['msg'],
                                 title=self.current.task_data['proje_yok']['title'])
        else:
            self.current.msg_box(msg=self.current.task_data['onay'], title=_(u"Talebiniz Kabul "
                                                                             u"Edildi."))

    # ---------------------------------------

    # ---------- Koordinasyon Birimi --------
    def ek_butce_talep_kontrol(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s - Ek bütçe talebi") % \
                                       (proje.yurutucu, proje.ad)
        self.output['objects'] = [['Kod Adi', 'Ad', 'Eski Toplam Fiyati', 'Yeni Toplam Fiyati',
                                   'Durum']]
        for key, talep in self.current.task_data['yeni_butceler'].iteritems():
            
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

        form = JsonForm()
        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='kabul')
        form.reddet = fields.Button(_(u"Reddet"), cmd='iptal')
        self.form_out(form)

    def butce_talep_detay_goster(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s / Kalem: %s") % \
                                       (proje.yurutucu, proje.ad, self.object)

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

        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def komisyon_aciklamasi(self):
        form = JsonForm(title=_(u"Komisyon Açıklaması"))
        form.komisyon_aciklama = fields.Text(_(u"Açıklama Yazınız"))
        form.yolla = fields.Button(_(u"Yolla"))
        self.form_out(form)

    def kabul_et_ve_komisyona_yolla(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        gundem = BAPGundem()
        gundem.proje = proje
        gundem.gundem_tipi = 2
        gundem.gundem_aciklama = self.input['form']['komisyon_aciklama']
        gundem.gundem_ekstra_bilgiler = json.dumps(
            {'yeni_butceler': self.current.task_data['yeni_butceler']})
        gundem.save()
        proje.save()
        self.current.task_data['onaylandi'] = 1

    def reddet_ve_aciklama_yaz(self):
        form = JsonForm(title=_(u"Red Açıklaması Yazınız"))
        form.red_aciklama = fields.Text(_(u"Red Açıklaması"))
        form.red_gonder = fields.Button(_(u"Gönder"))
        self.form_out(form)

    def bilgilendir(self):
        if 'red_aciklama' in self.input['form']:
            proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
            proje.save()
            self.current.task_data['red_aciklama'] = self.input['form']['red_aciklama']
            del self.current.task_data['yeni_butceler']
        else:
            self.current.task_data['onay'] = "Ek bütçe için bulunduğunuz talep kabul edilmiş " \
                                             "olup, komisyonun gündemine alınmıştır."

    def nesne_id_sil(self):
        self.current.task_data.pop('object_id', None)

    # ---------------------------------------

    @obj_filter
    def proje_turu_islem(self, obj, result):
        result['actions'] = [
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'}]

    @list_query
    def list_by_bap_proje_id(self, queryset):
        return queryset.filter(ilgili_proje_id=self.current.task_data['bap_proje_id'])

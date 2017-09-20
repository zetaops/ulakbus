# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import defaultdict
from ulakbus.models import BAPProje, BAPButcePlani, BAPGundem
from zengine.views.crud import CrudView
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _
from ulakbus.views.bap.proje_talep.bap_ek_butce_talep import ButcePlaniForm
import json

talep_durum = {1: 'Düzenlendi',
               2: 'Düzenlenmedi'}


class OnaylaForm(JsonForm):
    class Meta:
        title = _(u"Fasıl Aktarım Talebi Onaylama Ekranı")

    onayla = fields.Button("Onayla", cmd='onayla')
    geri_don = fields.Button("Geri Dön", cmd='geri_don')


class FasilAktarimTalep(CrudView):
    class Meta:
        model = 'BAPButcePlani'

    # ---------- Proje Yürütücüsü ----------

    def list(self, custom_form=None):
        if 'fasil_islemleri' not in self.current.task_data:
            self.current.task_data['fasil_islemleri'] = defaultdict(dict)

        self.output['objects'] = [['Muhasebe Kodu', 'Kod Adı', 'Alınacak Malzemenin Adı',
                                   'Birim Fiyat', 'Adet', 'Toplam Fiyat', 'Durum']]

        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        butce_planlari = BAPButcePlani.objects.filter(ilgili_proje=proje,
                                                      satin_alma_durum=5,
                                                      proje_durum=2).order_by()
        toplam = 0
        for butce in butce_planlari:
            if butce.key not in self.current.task_data['fasil_islemleri']:
                self.current.task_data['fasil_islemleri'][butce.key] = {
                    'durum': 2,
                    'muhasebe_kod_genel': butce.muhasebe_kod_genel,
                    'kod_ad': butce.kod_adi,
                    'ad': butce.ad,
                    'eski_adet': butce.adet,
                    'yeni_adet': '',
                    'eski_birim_fiyat': butce.birim_fiyat,
                    'yeni_birim_fiyat': '',
                    'eski_toplam_fiyat': butce.toplam_fiyat,
                    'yeni_toplam_fiyat': '',
                    'gerekce': butce.gerekce,
                    'degisiklik': False
                }
            birim_fiyat = self.current.task_data['fasil_islemleri'][butce.key]['yeni_birim_fiyat']
            adet = self.current.task_data['fasil_islemleri'][butce.key]['yeni_adet']
            toplam_fiyat = self.current.task_data['fasil_islemleri'][butce.key]['yeni_toplam_fiyat']
            item = {
                "fields": [butce.muhasebe_kod,
                           butce.kod_adi,
                           butce.ad,
                           str(birim_fiyat) if birim_fiyat else str(butce.birim_fiyat),
                           str(adet) if adet else str(butce.adet),
                           str(toplam_fiyat) if toplam_fiyat else str(butce.toplam_fiyat),
                           talep_durum[
                               self.current.task_data['fasil_islemleri'][butce.key]['durum']]],
                "actions": [{'name': _(u'Ayrıntı Göster'), 'cmd': 'show', 'mode': 'normal',
                             'show_as': 'button'},
                            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal',
                             'show_as': 'button'} if 'onay' not in self.current.task_data else {}],
                'key': butce.key
            }
            self.output['objects'].append(item)
            toplam += toplam_fiyat if toplam_fiyat else butce.toplam_fiyat

        mevcut_toplam = self.current.task_data.get('mevcut_toplam',
                                                   None) or BAPButcePlani.mevcut_butce(proje)
        self.current.task_data['mevcut_toplam'] = mevcut_toplam
        self.current.task_data['toplam_butce'] = toplam

        kullanilabilir_butce = (mevcut_toplam - toplam) + proje.butce_fazlaligi
        self.output['objects'].append({'fields': ['YENİ TOPLAM :', '', '', '', '', str(toplam)],
                                       'actions': ''})
        self.output['objects'].append({'fields': ['---', '---', '---', '---', '---', '---'],
                                       'actions': ''})
        self.output['objects'].append({'fields': ['MEVCUT TOPLAM BÜTÇE :',
                                                  str(mevcut_toplam),
                                                  '', '', 'KULLANILABİLİR BÜTÇE :',
                                                  str(kullanilabilir_butce), ''],
                                       'actions': ''})

        form = JsonForm(title=_(u"%s için Fasıl Aktarım Talebi") % proje.ad)
        if proje.butce_fazlaligi:
            form.help_text = _(
                u"Kullanabileceğiniz {} TL tutarında bütçe fazlalığınız bulunmaktadır. "
                u"KULLANILABİLİR BÜTÇE tutarı bu bütçe fazlalığının da eklenmiş halidir.".format(
                    proje.butce_fazlaligi))
        form.tamam = fields.Button(_(u"Onaya Yolla"), cmd='yolla')
        form.bitir = fields.Button(_(u"Vazgeç"), cmd='bitir')
        self.form_out(form)

    def add_edit_form(self):
        keys = ['ad', 'muhasebe_kod_genel', 'gerekce']
        form = ButcePlaniForm(current=self.current)
        yeni_data = self.current.task_data['fasil_islemleri'][self.object.key]
        for key in keys:
            setattr(form, key, yeni_data[key])

        adet, birim_fiyat = (yeni_data['yeni_adet'], yeni_data['yeni_birim_fiyat']) if \
            yeni_data['durum'] == 1 else (self.object.adet, self.object.birim_fiyat)
        form.adet = adet
        form.birim_fiyat = birim_fiyat
        self.form_out(form)

    def butce_kalem_kontrol(self):
        kalem_toplam_fiyat = self.input['form']['birim_fiyat'] * self.input['form']['adet']
        toplam_fiyat = sum(BAPButcePlani.objects.exclude(key=self.object.key).filter(
            ilgili_proje_id=self.current.task_data['bap_proje_id'],
            satin_alma_durum=2,
            proje_durum=2).values_list('toplam_fiyat'))

        if self.current.task_data['toplam_butce'] < (kalem_toplam_fiyat + toplam_fiyat):
            self.current.output['msgbox'] = {'type': 'warning',
                                             'title': 'Bütçe Fazlası!',
                                             'msg': 'Kabul edilen toplam bütçeden fazlasını talep '
                                                    'edemezsiniz.'}
            self.current.task_data['cmd'] = 'iptal'
        else:
            self.current.task_data['duzenlenmis_data'] = self.input['form']

    def aciklama_yaz(self):
        form = JsonForm(title=_(u"Açıklama Yazınız"))
        form.aciklama = fields.Text(_(u"Açıklama"))
        form.kaydet = fields.Button(_(u"Kaydet"))
        self.form_out(form)

    def kaydet(self):
        kalem = BAPButcePlani.objects.get(self.object.key)
        for key, value in self.current.task_data['ButcePlaniForm'].items():
            if hasattr(self.object, key):
                self.object.setattr(key, value)

        self.current.task_data['fasil_islemleri'][self.object.key] = \
            {'ad': self.object.ad,
             'durum': 1,
             'muhasebe_kod_genel': self.object.muhasebe_kod_genel,
             'kod_ad': self.object.kod_adi,
             'eski_adet': kalem.adet,
             'yeni_adet': self.object.adet,
             'eski_birim_fiyat': kalem.birim_fiyat,
             'yeni_birim_fiyat': self.object.birim_fiyat,
             'eski_toplam_fiyat': kalem.toplam_fiyat,
             'yeni_toplam_fiyat': self.object.adet * self.object.birim_fiyat,
             'gerekce': self.object.gerekce,
             'aciklama': self.input['form']['aciklama'],
             'degisiklik': True}

    def onaya_yolla(self):
        td = self.current.task_data
        td['degisiklik'] = any(x['durum'] != 2 for x in td['fasil_islemleri'].values())

    def hata_mesaji_goster(self):
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Fasıl Aktarım Talebi'),
            "msg": _(u'Fasıl aktarım talebinde bulunmanız için var olan kalemlerinizde '
                     u'değişiklikler yapmalısınız.')}

    def onaylama_karari(self):
        td = self.current.task_data
        proje = BAPProje.objects.get(td['bap_proje_id'])
        form = OnaylaForm(current=self.current)
        form.help_text = _(
u"""YENi TOPLAM BÜTÇE: **{}**,  

MEVCUT TOPLAM BÜTÇE: **{}**

""".format(td['toplam_butce'], td['mevcut_toplam']))

        if proje.butce_fazlaligi:
            form.help_text = _(
u"""{}

NOT: {} tutarında bütçe fazlalığınız bulunmaktadır. Fasıl aktarım talebiniz değerlendirilirken 
bütçe fazlası miktarınız dikkate alınacaktır.
""".format(form.help_text, str(proje.butce_fazlaligi)))
        self.form_out(form)

    def onayla(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.talep_uygunlugu = False
        proje.save()
        msg = {"title": _(u'İşlem Bilgilendirme'),
               "body": _(
                   u'Fasıl aktarım talebiniz koordinasyon birimine iletilmiştir. Koordinasyon '
                   u'biriminin değerlendirmesi sonrasında tekrar bilgilendirme '
                   u'yapılacaktır.')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['degisenleri_goster'] = True
        self.current.task_data['INVITATION_TITLE'] = "{} | {} | Fasıl Aktarım Talebi".format(
            proje.yurutucu.__unicode__(),
            proje.ad)

    # ---------------------------------------

    # ---------- Koordinasyon Birimi --------

    def talep_kontrol(self):
        td = self.current.task_data
        proje = BAPProje.objects.get(td['bap_proje_id'])
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s - Fasıl Aktarım Talebi") % \
                                      (proje.yurutucu, proje.ad)
        self.output['objects'] = [['Kalem Adı', 'Eski Birim Fiyat', 'Yeni Birim Fiyat',
                                   'Eski Toplam Fiyat', 'Yeni Toplam Fiyat', 'Durum']]
        for key, talep in td['fasil_islemleri'].items():
            if td['degisenleri_goster'] and talep['durum'] == 2:
                continue
            item = {
                "fields": [talep['ad'],
                           str(talep['eski_birim_fiyat']),
                           str(talep['yeni_birim_fiyat']),
                           str(talep['eski_toplam_fiyat']),
                           str(talep['yeni_toplam_fiyat']),
                           talep_durum[talep['durum']]],
                "actions": [{'name': _(u'Ayrıntı Göster'), 'cmd': 'show', 'mode': 'normal',
                             'show_as': 'button'}],
                'key': key
            }
            self.output['objects'].append(item)

        form = JsonForm()
        form.help_text = _(
u"""YENi TOPLAM BÜTÇE: **{}**,  

MEVCUT TOPLAM BÜTÇE: **{}**

""".format(td['toplam_butce'], td['mevcut_toplam']))
        if proje.butce_fazlaligi:
            form.help_text = _(
u"""{}

BÜTÇE FAZLALIĞI: **{}**""".format(form.help_text, proje.butce_fazlaligi))

        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='kabul')
        form.reddet = fields.Button(_(u"Reddet"), cmd='red')
        form.butun = fields.Button(_(u"Bütün Kalemleri Gör"), cmd='butun')
        form.degisiklik = fields.Button(_(u"Değişen Kalemleri Gör"), cmd='degisiklik')
        self.form_out(form)

    def talep_detay_goster(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s / Kalem: %s") % \
                                      (proje.yurutucu, proje.ad, self.object)

        data = self.current.task_data['fasil_islemleri'][self.object.key]

        obj_data = {'Kalem Adı': data['ad'],
                    'Eski Adet': str(data['eski_adet']),
                    'Yeni Adet': str(data['yeni_adet']),
                    'Eski Birim Fiyat': str(data['eski_birim_fiyat']),
                    'Yeni Birim Fiyat': str(data['yeni_birim_fiyat']),
                    'Eski Toplam Fiyat': str(data['eski_toplam_fiyat']),
                    'Yeni Toplam Fiyat': str(data['yeni_toplam_fiyat']),
                    'Açıklama': data['aciklama'] if 'aciklama' in data else ''}
        self.output['object'] = obj_data

        form = JsonForm()
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def onay_mesaji_hazirla(self):
        mesaj = "Fasıl aktarımı için bulunduğunuz talep koordinasyon birimi tarafından kabul edilmiş " \
                "olup, komisyonun gündemine alınmıştır. Komisyon değerlendirmesinden sonra " \
                "karar hakkında tekrar bilgilendirilme yapılacaktır."
        self.current.task_data['bildirim_mesaji'] = mesaj

    def red_mesaji_hazirla(self):
        gerekce = self.input['form']['gerekce']
        mesaj = "Fasıl aktarımı için bulunduğunuz talep reddedilmiştir. Red Gerekçesi: {}".format(
            gerekce)
        self.current.task_data['bildirim_mesaji'] = mesaj

    def komisyona_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        BAPGundem(proje=proje, gundem_tipi=3,
                  gundem_aciklama=self.input['form']['aciklama'],
                  gundem_ekstra_bilgiler=json.dumps(
                      {'fasil_islemleri': self.current.task_data['fasil_islemleri'],
                       'mevcut_toplam': self.current.task_data['mevcut_toplam'],
                       'yeni_toplam': self.current.task_data['toplam_butce'],
                       'butce_fazlaligi': proje.butce_fazlaligi})).save()

    def nesne_id_sil(self):
        self.current.task_data.pop('object_id', None)
        del self.current.task_data['fasil_islemleri']

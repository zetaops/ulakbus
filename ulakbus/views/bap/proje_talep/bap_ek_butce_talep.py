# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import json
from collections import defaultdict
from ulakbus.models import BAPProje, BAPButcePlani, BAPGundem, User
from zengine.models import TaskInvitation, WFInstance
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _

talep_durum = {1: 'Yeni',
               2: 'Silinecek',
               3: 'Düzenlendi',
               4: 'Düzenlenmedi'}


class OnaylaForm(JsonForm):
    class Meta:
        title = _(u"Ek Bütçe Talebi Onaylama Ekranı")

    onayla = fields.Button("Onayla", cmd='onayla')
    geri_don = fields.Button("Geri Dön", cmd='geri_don')


class EkButceTalepForm(JsonForm):
    class Meta:
        title = _(u"{} - Bap Ek Bütçe Talep")

    tamam = fields.Button(_(u"Onaya Yolla"))
    ekle = fields.Button(_(u"Yeni Bütçe Kalemi Ekle"), cmd='add_edit_form')
    iptal = fields.Button(_(u"İptal"), cmd='iptal')


class KomisyonAciklamaForm(JsonForm):
    class Meta:
        title = _(u"Komisyon Açıklama")
        always_blank = False

    aciklama = fields.Text(_(u"Komisyon Değerlendirmesi İçin Açıklama Yazınız"))
    gonder = fields.Button(_(u"Gönder"), cmd='komisyon_gonder')
    geri = fields.Button(_(u"Tabloya Geri Dön"), cmd='geri_don', form_validation=False)


class RedAciklamaForm(JsonForm):
    class Meta:
        title = _(u"Talep Reddi Açıklama")
        always_blank = False

    gerekce = fields.Text(_(u"Reddetme Gerekçenizi Yazınız"))
    gonder = fields.Button(_(u"Gönder"), cmd='red_gonder')
    geri = fields.Button(_(u"Tabloya Geri Dön"), cmd='geri_don', form_validation=False)


class EkButceTalep(CrudView):
    class Meta:
        model = 'BAPButcePlani'

    # ---------- Proje Yürütücüsü ----------
    def list(self, custom_form=None):
        if 'yeni_butceler' not in self.current.task_data:
            self.current.task_data['yeni_butceler'] = defaultdict(dict)

        self.output['objects'] = [['Muhasebe Kodu', 'Kod Adı', 'Alınacak Malzemenin Adı',
                                   'Birim Fiyat', 'Adet', 'Toplam Fiyat', 'Durum']]

        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        butce_planlari = BAPButcePlani.objects.filter(ilgili_proje=proje,
                                                      satin_alma_durum=5,
                                                      proje_durum__in=[1, 2]
                                                      ).order_by()
        toplam = 0
        for butce in butce_planlari:
            if butce.key not in self.current.task_data['yeni_butceler']:
                self.current.task_data['yeni_butceler'][butce.key] = {
                    'durum': 4,
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
            butce_bilgileri = self.current.task_data['yeni_butceler'][butce.key]
            yeni_birim, yeni_adet, yeni_toplam = \
                (str(butce_bilgileri['yeni_birim_fiyat']),
                 str(butce_bilgileri['yeni_adet']),
                 str(butce_bilgileri['yeni_toplam_fiyat'])) if durum not in [2, 4] else \
                    (str(butce.birim_fiyat), str(butce.adet), str(butce.toplam_fiyat))
            item = {
                "fields": [
                    butce.muhasebe_kod,
                    butce.kod_adi,
                    butce.ad,
                    yeni_birim,
                    yeni_adet,
                    yeni_toplam,
                    talep_durum[durum]],
                "actions": [{'name': _(u'Ayrıntı Göster'), 'cmd': 'show', 'mode': 'normal',
                             'show_as': 'button'},
                            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal',
                             'show_as': 'button'},
                            {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal',
                             'show_as': 'button'}],
                'key': butce.key
            }
            self.output['objects'].append(item)

            fiyat = toplam_fiyat if toplam_fiyat else butce.toplam_fiyat
            toplam += -fiyat if durum == 2 else fiyat

        mevcut_toplam = self.current.task_data.get('mevcut_toplam',
                                                   None) or BAPButcePlani.mevcut_butce(proje)
        self.current.task_data['mevcut_toplam'] = mevcut_toplam
        self.current.task_data['toplam'] = toplam

        self.output['objects'].extend(
            [{'fields': ['YENİ TOPLAM', '', '', '', '',
                         str(self.current.task_data['toplam']), ''],
              'actions': ''},
             {'fields': ['MEVCUT TOPLAM', '', '', '', '',
                         str(self.current.task_data['mevcut_toplam']), ''],
              'actions': ''}]
        )

        form = EkButceTalepForm(current=self.current)
        form.title = form.title.format(proje.ad)
        if proje.butce_fazlaligi:
            form.help_text = _(
                u"Kullanabileceğiniz {} TL tutarında bütçe fazlalığınız bulunmaktadır.".format(
                    proje.butce_fazlaligi))
        self.form_out(form)

    def kaydet(self):
        if 'yeni_butceler' not in self.current.task_data:
            self.current.task_data['yeni_butceler'] = defaultdict(dict)

        if not self.object.key:
            self.object.ilgili_proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
            self.object.muhasebe_kod_genel = self.current.task_data['muhasebe_kod_genel']
            self.object.kod_adi = self.current.task_data['kod_adi']
            durum = 1
            self.object.toplam_fiyat = self.input['form']['birim_fiyat'] * self.input['form'][
                'adet']
            self.set_form_data_to_object()
            self.object.blocking_save()
        else:
            durum = 3 if self.current.task_data['yeni_butceler'][self.object.key][
                             'durum'] in [2, 3, 4] else 1

        self.current.task_data['yeni_butceler'][self.object.key] = \
            {'durum': durum,
             'kod_ad': self.current.task_data['kod_adi'],
             'ad': self.object.ad,
             'eski_adet': self.object.adet if not durum == 1 else '',
             'yeni_adet': self.input['form']['adet'],
             'eski_birim_fiyat': self.object.birim_fiyat if not durum == 1 else '',
             'yeni_birim_fiyat': self.input['form']['birim_fiyat'],
             'eski_toplam_fiyat': self.object.toplam_fiyat if not durum == 1 else '',
             'yeni_toplam_fiyat': self.input['form']['adet'] * self.input['form']['birim_fiyat'],
             'gerekce': self.input['form']['gerekce']}

    def yeni_kalem_sil(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        for kalem in BAPButcePlani.objects.filter(ilgili_proje=proje,
                                                  proje_durum=1):
            kalem.blocking_delete()

    def butce_kalemini_sil(self):

        if self.current.task_data['yeni_butceler'][self.object.key]['durum'] == 1:
            self.object.blocking_delete()
            del self.current.task_data['object_id']
        else:
            self.current.task_data['yeni_butceler'][self.object.key] = \
                {'durum': 2,
                 'kod_ad': self.object.kod_adi,
                 'ad': self.object.ad,
                 'eski_adet': self.object.adet,
                 'yeni_adet': '',
                 'eski_birim_fiyat': self.object.birim_fiyat,
                 'yeni_birim_fiyat': '',
                 'eski_toplam_fiyat': self.object.toplam_fiyat,
                 'yeni_toplam_fiyat': '',
                 'gerekce': self.object.gerekce}

    def onaylama_kontrol(self):
        td = self.current.task_data
        td['talep_varmi'] = any(x['durum'] != 4 for x in td['yeni_butceler'].values())

    def hata_mesaji_olustur(self):
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Ek Bütçe Talebi'),
            "msg": _(u'Ek bütçe talebinde bulunmanız için var olan kalemlerinizde '
                     u'değişiklikler yapmanız ya da yeni kalem eklemeniz gerekmektedir.')}

    def onaylama_karari(self):
        td = self.current.task_data
        proje = BAPProje.objects.get(td['bap_proje_id'])
        form = OnaylaForm(current=self.current)
        form.help_text = _(
u"""YENi TOPLAM BÜTÇE: **{}**,  

MEVCUT TOPLAM BÜTÇE: **{}**

""".format(td['toplam'], td['mevcut_toplam']))

        if proje.butce_fazlaligi:
            form.help_text = _(
u"""{}

NOT: {} tutarında bütçe fazlalığınız bulunmaktadır. Bütçe talebiniz değerlendirilirken 
bütçe fazlası miktarınız dikkate alınacaktır.
""".format(form.help_text, str(proje.butce_fazlaligi)))

        self.form_out(form)

    def onayla(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        proje.talep_uygunlugu = False
        proje.save()
        msg = {"title": _(u'İşlem Bilgilendirme'),
               "body": _(u'Ek bütçe talebiniz koordinasyon birimine iletilmiştir. Koordinasyon '
                         u'biriminin değerlendirmesi sonrasında tekrar bilgilendirme '
                         u'yapılacaktır.')}
        self.current.task_data['LANE_CHANGE_MSG'] = msg
        self.current.task_data['degisenleri_goster'] = True
        self.current.task_data['INVITATION_TITLE'] = "{} | {} | Ek Bütçe Talebi".format(
            proje.yurutucu.__unicode__(),
            proje.ad)

        # ---------- Koordinasyon Birimi --------

    def ek_butce_talep_kontrol(self):
        td = self.current.task_data
        proje = BAPProje.objects.get(td['bap_proje_id'])
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s - Ek bütçe talebi") % \
                                      (proje.yurutucu, proje.ad)
        self.output['objects'] = [['Kod Adı', 'Ad', 'Eski Toplam Fiyatı', 'Yeni Toplam Fiyatı',
                                   'Durum']]
        for key, talep in td['yeni_butceler'].items():
            if td['degisenleri_goster'] and talep['durum'] == 4:
                continue
            item = {
                "fields": [talep['kod_ad'],
                           talep['ad'],
                           str(talep['eski_toplam_fiyat']) if talep['durum'] != 1 else '-',
                           str(talep['yeni_toplam_fiyat']) if talep['durum'] not in [2, 4] else '-',
                           talep_durum[talep['durum']]],
                "actions": [{'name': _(u'Ayrıntı Göster'), 'cmd': 'goster', 'mode': 'normal',
                             'show_as': 'button'}],
                'key': key
            }
            self.output['objects'].append(item)

        form = JsonForm()
        form.help_text = _(
u"""YENi TOPLAM BÜTÇE: **{}**,  

MEVCUT TOPLAM BÜTÇE: **{}**

""".format(td['toplam'], td['mevcut_toplam']))
        if proje.butce_fazlaligi:
            form.help_text=_(
u"""{}

BÜTÇE FAZLALIĞI: **{}**""".format(form.help_text, proje.butce_fazlaligi))

        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='kabul')
        form.reddet = fields.Button(_(u"Reddet"), cmd='iptal')
        form.butun = fields.Button(_(u"Bütün Kalemleri Gör"), cmd='butun')
        form.degisiklik = fields.Button(_(u"Değişen Kalemleri Gör"), cmd='degisiklik')
        self.form_out(form)

    def kalem_gosterme_secenegi_belirle(self):
        td = self.current.task_data
        td['degisenleri_goster'] = True if self.input['form']['degisiklik'] else False

    def talep_detay_goster(self):
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

        form = JsonForm(current=self.current)
        form.tamam = fields.Button(_(u"Tamam"))
        self.form_out(form)

    def komisyon_aciklamasi(self):
        self.form_out(KomisyonAciklamaForm(current=self.current))

    def kabul_et_ve_komisyona_yolla(self):
        BAPGundem(proje_id=self.current.task_data['bap_proje_id'],
                  gundem_tipi=2,
                  gundem_aciklama=self.input['form']['aciklama'],
                  gundem_ekstra_bilgiler=json.dumps(
                      {'ek_butce': self.current.task_data['yeni_butceler']})
                  ).save()

    def onay_mesaji_hazirla(self):
        mesaj = "Ek bütçe için bulunduğunuz talep koordinasyon birimi tarafından kabul edilmiş " \
                "olup, komisyonun gündemine alınmıştır. Komisyon değerlendirmesinden sonra " \
                "karar hakkında tekrar bilgilendirilme yapılacaktır."
        self.current.task_data['bildirim_mesaji'] = mesaj

    def reddet_ve_aciklama_yaz(self):
        self.form_out(RedAciklamaForm(current=self.current))

    def red_mesaji_hazirla(self):
        gerekce = self.input['form']['gerekce']
        mesaj = "Ek bütçe için bulunduğunuz talep reddedilmiştir. Red Gerekçesi: {}".format(gerekce)
        self.current.task_data['bildirim_mesaji'] = mesaj

    def bilgilendir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        basvuru_rol = proje.basvuru_rolu
        sistem_kullanicisi = User.objects.get(username='sistem_bilgilendirme')
        basvuru_rol.send_notification(message=self.current.task_data['bildirim_mesaji'],
                                      title=_(
                                          u"Talep Koordinasyon Birimi Değerlendirmesi"),
                                      sender=sistem_kullanicisi)
        proje.talep_uygunlugu = True
        proje.blocking_save({'talep_uygunlugu': True})
        self.current.output['msgbox'] = {
            'type': 'info',
            "title": _(u"İşlem Mesajı"),
            "msg": "Talep değerlendirmeniz başarılı ile gerçekleştirilmiştir. Proje yürütücüsü "
                   "{} değerlendirmeniz hakkında bilgilendirilmiştir.".format(
                proje.yurutucu.__unicode__())}
        wfi = WFInstance.objects.get(self.current.token)
        TaskInvitation.objects.filter(instance = wfi,
                                      role = self.current.role).delete()

    def nesne_id_sil(self):
        self.yeni_kalem_sil()
        del self.current.task_data['yeni_butceler']
        self.current.task_data.pop('object_id', None)

    # ---------------------------------------

    @obj_filter
    def proje_turu_islem(self, obj, result):
        result['actions'] = [
            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Ayrıntı Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Sil'), 'cmd': 'delete', 'mode': 'normal', 'show_as': 'button'}]

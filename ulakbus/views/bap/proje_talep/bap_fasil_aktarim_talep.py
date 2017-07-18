# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from collections import defaultdict

from ulakbus.models import BAPProje, BAPButcePlani, BAPGundem, Personel, Okutman

from zengine.views.crud import CrudView, list_query, obj_filter
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _


class FasilAktarimTalep(CrudView):
    class Meta:
        model = 'BAPButcePlani'

    # ---------- Proje Yürütücüsü ----------
    def proje_id_kontrol(self):
        self.current.task_data['cmd'] = 'proje_id_var' if 'bap_proje_id' in self.current.task_data \
            else 'proje_id_yok'

    def kontrol(self):
        personel = Personel.objects.get(user=self.current.user)
        okutman = Okutman.objects.get(personel=personel)
        projeler = BAPProje.objects.filter(yurutucu=okutman, kabul_edilen_butce__gt=0)
        if projeler.count() == 0:
            self.current.task_data['cmd'] = 'bulunamadi'
            self.current.task_data['proje_yok'] = {'msg': 'Yürütücüsü olduğunuz herhangi bir proje '
                                                          'bulunamadı. Size bağlı olan proje '
                                                          'olmadığı için fasıl talebinde '
                                                          'bulunamazsınız.',
                                                   'title': 'Proje Bulunamadı'}
        if 'bap_proje_id' in self.current.task_data:
            self.current.task_data['cmd'] = 'red_mesaj'

    def proje_sec(self):
        personel = Personel.objects.get(user=self.current.user)
        okutman = Okutman.objects.get(personel=personel)
        data = [(proje.key, proje.ad) for proje in BAPProje.objects.filter(yurutucu=okutman)]

        form = JsonForm(title=_(u"Proje Seçiniz"))
        form.proje = fields.String(choices=data, default=data[0][0])
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def list(self, custom_form=None, **kwargs):
        if 'form' in self.input and 'proje' in self.input['form']:
            self.current.task_data['bap_proje_id'] = self.input['form']['proje']

        if 'fasil_islemleri' not in self.current.task_data:
            self.current.task_data['fasil_islemleri'] = defaultdict(dict)

        self.output['objects'] = [['Muhasebe Kodu', 'Kod Adı', 'Alınacak Malzemenin Adı',
                                   'Birim Fiyat', 'Adet', 'Toplam Fiyat', 'Durum']]

        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        butce_planlari = BAPButcePlani.objects.all(ilgili_proje=proje)
        toplam = 0
        for butce in butce_planlari:
            if butce.key not in self.current.task_data['fasil_islemleri']:
                butce.durum = 4
                butce.save()
                self.current.task_data['fasil_islemleri'][butce.key] = {
                    'durum': butce.get_durum_display(),
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
                           self.current.task_data['fasil_islemleri'][butce.key]['durum']],
                "actions": [{'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal',
                            'show_as': 'button'},
                            {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal',
                             'show_as': 'button'} if 'onay' not in self.current.task_data else {}],
                'key': butce.key
            }
            self.output['objects'].append(item)
            toplam += toplam_fiyat if toplam_fiyat else butce.toplam_fiyat
        self.current.task_data['toplam_butce'] = proje.kabul_edilen_butce

        kullanilabilir_butce = proje.kabul_edilen_butce - toplam
        self.output['objects'].append({'fields': ['TOPLAM :', '', '', '', '', str(toplam)],
                                       'actions': ''})
        self.output['objects'].append({'fields': ['---', '---', '---', '---', '---', '---'],
                                       'actions': ''})
        self.output['objects'].append({'fields': ['TOPLAM KABUL EDİLEN BÜTÇE :',
                                                  str(proje.kabul_edilen_butce),
                                                  '', '', 'KULLANILABİLİR BÜTÇE :',
                                                  str(kullanilabilir_butce), ''],
                                       'actions': ''})
        if 'red_aciklama' in self.current.task_data:
            self.current.msg_box(msg=self.current.task_data['red_aciklama'],
                                 title=_(u"Talebiniz Reddedildi."),
                                 typ='warning')
            del self.current.task_data['red_aciklama']
        elif 'hata_fazla_butce' in self.current.task_data:
            self.current.msg_box(msg=self.current.task_data['hata_fazla_butce']['msg'],
                                 title=self.current.task_data['hata_fazla_butce']['title'],
                                 typ='warning')
            del self.current.task_data['hata_fazla_butce']
        elif 'onay' in self.current.task_data:
            self.current.msg_box(msg=self.current.task_data['onay'],
                                 title=_(u"Talebiniz Komisyon Gündemine Alınmıştır"),
                                 typ='info')

        form = JsonForm(title=_(u"%s için Fasıl Aktarım Talebi") % proje.ad)
        if 'onay' not in self.current.task_data:
            form.tamam = fields.Button(_(u"Onaya Yolla"), cmd='yolla')
        form.bitir = fields.Button(_(u"Vazgeç"), cmd='bitir')
        self.form_out(form)

    def add_edit_form(self):
        form = JsonForm(self.object, current=self.current)
        form.exclude = ['muhasebe_kod', 'kod_adi', 'ad', 'onay_tarihi', 'ilgili_proje', 'durum']
        form.title = "%s Kodlu / %s / Kalem Adı: %s" % (
            self.object.muhasebe_kod, self.object.kod_adi, self.object.ad)
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def butce_kalem_kontrol(self):
        kalem_toplam_fiyat = self.input['form']['toplam_fiyat']
        toplam_fiyat = sum(BAPButcePlani.objects.exclude(key=self.object.key).filter(
            ilgili_proje_id=self.current.task_data['bap_proje_id']).values_list('toplam_fiyat'))

        if self.current.task_data['toplam_butce'] < (kalem_toplam_fiyat + toplam_fiyat):
            self.current.task_data['hata_fazla_butce'] = {'title': 'Bütçe Fazlası!',
                                                          'msg': 'Kabul edilen toplam bütçeden '
                                                                 'fazlasını talep edemezsiniz.'}
            self.current.task_data['cmd'] = 'iptal'
        else:
            self.current.task_data['duzenlenmis_data'] = self.input['form']

    def aciklama_yaz(self):
        form = JsonForm(title=_(u"Açıklama Yazınız"))
        form.aciklama = fields.Text(_(u"Açıklama"))
        form.kaydet = fields.Button(_(u"Kaydet"))
        self.form_out(form)

    def kaydet(self):
        if 'fasil_islemleri' not in self.current.task_data:
            self.current.task_data['fasil_islemleri'] = defaultdict(dict)

        kalem = BAPButcePlani.objects.get(self.object.key)
        for key, value in self.current.task_data['duzenlenmis_data'].iteritems():
            if hasattr(self.object, key):
                self.object.setattr(key, value)

        self.object.durum = 3
        self.current.task_data['fasil_islemleri'][self.object.key] = \
            {'ad': self.object.ad,
             'durum': self.object.get_durum_display(),
             'kod_ad': self.object.kod_adi,
             'eski_adet': kalem.adet,
             'yeni_adet': self.object.adet,
             'eski_birim_fiyat': kalem.birim_fiyat,
             'yeni_birim_fiyat': self.object.birim_fiyat,
             'eski_toplam_fiyat': kalem.toplam_fiyat,
             'yeni_toplam_fiyat': self.object.toplam_fiyat,
             'gerekce': self.object.gerekce,
             'aciklama': self.input['form']['aciklama'],
             'degisiklik': True}

    def onaya_yolla(self):
        degisiklik = False
        if 'fasil_islemleri' in self.current.task_data:
            for k, islem in self.current.task_data['fasil_islemleri'].iteritems():
                if islem['degisiklik']:
                    degisiklik = True

        if degisiklik:
            proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
            proje.durum = 2  # koordinasyon birimi onayi bekleniyor.
            proje.save()
        else:
            self.current.task_data['cmd'] = 'talep_yok'
            self.current.output['msgbox'] = {
                'type': 'warning', "title": _(u'Fasıl Aktarım Talebi'),
                "msg": _(u'Fasıl aktarım talebinde bulunmanız için var olan kalemlerinizde '
                         u'değişiklikler yapmalısınız.')}

    def proje_bulunamadi(self):
        self.current.msg_box(msg=self.current.task_data['proje_yok']['msg'],
                             title=self.current.task_data['proje_yok']['title'])

    # ---------------------------------------

    # ---------- Koordinasyon Birimi --------

    def talep_kontrol(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.output['object_title'] = _(u"Yürütücü: %s / Proje: %s - Ek bütçe talebi") % \
                                       (proje.yurutucu, proje.ad)
        self.output['objects'] = [['Kalem Adı', 'Eski Birim Fiyat', 'Yeni Birim Fiyat',
                                   'Eski Toplam Fiyat', 'Yeni Toplam Fiyat']]
        for key, talep in self.current.task_data['fasil_islemleri'].iteritems():
            item = {
                "fields": [talep['ad'],
                           str(talep['eski_birim_fiyat']),
                           str(talep['yeni_birim_fiyat']),
                           str(talep['eski_toplam_fiyat']),
                           str(talep['yeni_toplam_fiyat'])],
                "actions": [{'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal',
                            'show_as': 'button'}],
                'key': key
            }
            self.output['objects'].append(item)

        form = JsonForm()
        form.onayla = fields.Button(_(u"Komisyona Yolla"), cmd='kabul')
        form.reddet = fields.Button(_(u"Reddet"), cmd='red')
        form.iptal = fields.Button(_(u"İptal"), cmd='iptal')
        self.form_out(form)

    def fasil_talep_detay_goster(self):
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

    def reddet_ve_aciklama_yaz(self):
        form = JsonForm(title=_(u"Red Açıklaması Yazınız"))
        form.red_aciklama = fields.Text(_(u"Red Açıklaması"))
        form.red_gonder = fields.Button(_(u"Gönder"))
        self.form_out(form)

    def komisyon_aciklamasi(self):
        form = JsonForm(title=_(u"Komisyon Açıklaması"))
        form.komisyon_aciklama = fields.Text(_(u"Açıklama Yazınız"))
        form.yolla = fields.Button(_(u"Yolla"))
        self.form_out(form)

    def komisyona_gonder(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        gundem = BAPGundem()
        gundem.proje = proje
        gundem.gundem_tipi = 3
        gundem.gundem_aciklama = self.input['form']['komisyon_aciklama']
        gundem.save()
        proje.durum = 4     # Komisyon Onayı Bekliyor
        proje.save()
        self.current.task_data['onaylandi'] = 1

    def bilgilendir(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        if 'red_aciklama' in self.input['form']:
            proje.durum = 3
            proje.save()
            self.current.task_data['red_aciklama'] = self.input['form']['red_aciklama']
            self.current.task_data['cmd'] = 'red_aciklama'
            del self.current.task_data['fasil_islemleri']
        else:
            self.current.task_data['onay'] = "Fasıl aktarımı için bulunduğunuz talep kabul " \
                                             "edilmiş olup, komisyonun gündemine alınmıştır."

    def iptal_et(self):
        pass

    def nesne_id_sil(self):
        self.current.task_data.pop('object_id', None)

    # ---------------------------------------

    @obj_filter
    def proje_turu_islem(self, obj, result):

        result['actions'] = []
        if 'onay' not in self.current.task_data:
            duzenle = {'name': _(u'Düzenle'), 'cmd': 'add_edit_form', 'mode': 'normal',
                       'show_as': 'button'}
            result['actions'].append(duzenle)

        goster = {'name': _(u'Göster'), 'cmd': 'show', 'mode': 'normal', 'show_as': 'button'}
        result['actions'].append(goster)

    @list_query
    def list_by_bap_proje_id(self, queryset):
        return queryset.filter(ilgili_proje_id=self.current.task_data['bap_proje_id'])

# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from collections import defaultdict

from ulakbus.models import BAPProje, BAPGundem, Personel

from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __

obje_tipleri = ['Yeni', 'Düzenlendi', 'Silindi']


class EkButceTalep(CrudView):
    class Meta:
        model = 'BAPButcePlani'

    # ---------- Proje Yürütücüsü ----------
    def kontrol(self):
        personel = Personel.objects.get(user=self.current.user)
        if BAPProje.objects.filter(yurutucu=personel).count() == 0:
            self.current.task_data['onaylandi'] = 1
            self.current.task_data['proje_yok'] = {'msg': 'Yürütücüsü olduğunuz herhangi bir proje '
                                                          'bulunamadı. Size bağlı olan proje '
                                                          'olmadığı için ek bütçe talebinde '
                                                          'bulunamazsınız.',
                                                   'title': 'Proje Bulunamadı'}
        elif 'onaylandi' not in self.current.task_data:
                self.current.task_data['onaylandi'] = 0

    def proje_sec(self):
        personel = Personel.objects.get(user=self.current.user)
        data = [(proje.key, proje.ad) for proje in BAPProje.objects.filter(yurutucu=personel)]

        form = JsonForm(title=_(u"Proje Seçiniz"))
        form.proje = fields.String(choices=data)
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def list(self, custom_form=None):
        if 'form' in self.input and 'proje' in self.input['form']:
            self.current.task_data['bap_proje_id'] = self.input['form']['proje']
        CrudView.list(self)
        toplam = sum(float(obj['fields'][5]) for obj in self.output['objects'][1:])
        self.output['objects'].append({'fields': ['TOPLAM', '', '', '', '', str(toplam)],
                                       'actions': ''})

        form = JsonForm(title=_(u"Bap Ek Bütçe Talep"))
        form.tamam = fields.Button(_(u"Onaya Yolla"))
        form.ekle = fields.Button(_(u"Ekle"), cmd='add_edit_form')
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
            obje_durum = obje_tipleri[0]
            self.set_form_data_to_object()
            self.object.save()
            toplam_fiyat = 0
        else:
            obje_durum = obje_tipleri[1]
            toplam_fiyat = self.object.toplam_fiyat
            self.set_form_data_to_object()

        self.current.task_data['yeni_butceler'][self.object.key] = \
            {'durum': obje_durum,
             'kod_ad': self.current.task_data['kod_adi'],
             'ad': self.input['form']['ad'],
             'eski_toplam_fiyat': toplam_fiyat,
             'yeni_toplam_fiyat': self.input['form']['toplam_fiyat'],
             'gerekce': self.input['form']['gerekce']}

        self.object.muhasebe_kod = self.current.task_data['muhasebe_kod']
        self.object.kod_adi = self.current.task_data['kod_adi']
        if 'bap_proje_id' in self.current.task_data:
            self.object.ilgili_proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        self.object.blocking_save()

    def butce_kalemini_sil(self):
        if 'yeni_butceler' not in self.current.task_data:
            self.current.task_data['yeni_butceler'] = defaultdict(dict)

        self.current.task_data['yeni_butceler'][self.object.key] = \
            {'durum': obje_tipleri[2],
             'kod_ad': self.object.kod_adi,
             'ad': self.object.ad,
             'eski_toplam_fiyat': self.object.toplam_fiyat,
             'yeni_toplam_fiyat': 0,
             'gerekce': ''}

        self.object.blocking_delete()
        del self.current.task_data['object_id']

    def onaya_yolla(self):
        if 'yeni_butceler' not in self.current.task_data:
            self.current.task_data['cmd'] = 'talep_yok'
            self.current.output['msgbox'] = {
                'type': 'warning', "title": _(u'Ek Bütçe Talebi'),
                "msg": _(u'Ek bütçe talebinde bulunmanız için var olan kalemlerinizde '
                         u'değişiklikler yapmalısınız.')}
        else:
            proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
            proje.durum = 2     # koordinasyon birimi onayi bekleniyor.
            proje.save()

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
        self.output['objects'] = [['Kod Adi', 'Ad', 'Eski Fiyati', 'Yeni Fiyati',
                                   'Gerekce', 'Durum']]
        for talep in self.current.task_data['yeni_butceler'].values():
            
            item = {
                "fields": [talep['kod_ad'],
                           talep['ad'],
                           str(talep['eski_toplam_fiyat']),
                           str(talep['yeni_toplam_fiyat']),
                           talep['gerekce'],
                           talep['durum']],
                "actions": False,
            }
            self.output['objects'].append(item)

        form = JsonForm()
        form.onayla = fields.Button(_(u"Onayla"), cmd='kabul')
        form.reddet = fields.Button(_(u"Reddet"), cmd='iptal')
        self.form_out(form)

    def kabul_et_ve_komisyona_yolla(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        gundem = BAPGundem()
        gundem.proje = proje
        gundem.gundem_tipi = 2
        gundem.save()
        proje.durum = 4     # Komisyon Onayı Bekliyor
        proje.save()
        self.current.task_data['onaylandi'] = 1

    def reddet_ve_aciklama_yaz(self):
        form = JsonForm(title=_(u"Red Açıklaması Yazınız"))
        form.red_aciklama = fields.Text(_(u"Red Açıklaması"))
        form.red_gonder = fields.Button(_(u"Gönder"))
        self.form_out(form)

    def bilgilendir(self):
        if 'red_aciklama' in self.input['form']:
            self.current.task_data['red_aciklama'] = self.input['form']['red_aciklama']
        else:
            self.current.task_data['onay'] = "Ek bütçe için bulunduğunuz talep kabul edilmiş " \
                                             "olup, komisyonun gündemine alınmıştır."

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

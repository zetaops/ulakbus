# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPTeklif, BAPFirma
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from ulakbus.lib.common import get_file_url


class FirmaTeklifForm(JsonForm):
    class Meta:
        include = ['Belgeler']

    kaydet = fields.Button(__(u"Teklifi Kaydet"), cmd='kaydet')
    geri = fields.Button(__(u"Geri Dön"), cmd='geri_don')


class BapFirmaTeklif(CrudView):
    class Meta:
        model = 'BAPButcePlani'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = fields.Button(__(u"Mevcut Tekliflerim"), cmd='mevcut_teklif')
        self.model_class.Meta.verbose_name_plural = __(u"Teklife Açık Bütçe Kalemleri")
        self.firma = BAPFirma.objects.get('DulDXqOk6HeHVnKG4Mvwo5hU1TE')
        # self.firma = self.current.user.bap_firma_set[0].bap_firma

    def ayni_butce_kalemi_teklif_kontrol(self):
        teklif_sayisi = BAPTeklif.objects.filter(butce=self.object, firma=self.firma).count()
        self.current.task_data['ayni_teklif'] = True if teklif_sayisi else False

    def ayni_teklif_var_mesaji(self):
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Mevcut Teklif Uyarısı'),
                                         "msg": __(u"%s adlı bütçe kalemine ait teklifiniz "
                                                   u"bulunmaktadır. Mevcut Tekliflerim'den ilgili "
                                                   u"teklife ulaşabilir, değişiklikler "
                                                   u"yapabilirsiniz." % self.object.ad)}

    def mevcut_teklifler_kontrol(self):
        teklif_sayisi = BAPTeklif.objects.filter(firma=self.firma, durum=1).count()
        self.current.task_data['mevcut_teklifler'] = True if teklif_sayisi else False

    def mevcut_teklif_yok_mesaji(self):
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Firma Teklifleri'),
                                         "msg": __(u"Sistemde kayıtlı teklifiniz bulunmamaktadır.")}

    def mevcut_teklifleri_goster(self):
        form = JsonForm(title=_(u'Firmanın Mevcut Teklifleri'))
        form.tamam = fields.Button(__(u"Geri Dön"), cmd='tamam')
        teklifler = BAPTeklif.objects.filter(firma=self.firma, durum=1).order_by()
        self.output['objects'] = [[_(u'Bütçe Kalemi')]]
        for teklif in teklifler:
            butce = teklif.butce.ad

            list_item = {
                "fields": [butce],
                "actions": [
                    {'name': _(u'Belgeleri İndir'), 'cmd': 'belge_indir', 'show_as': 'button',
                     'object_key': 'data_key'},
                    {'name': _(u'Belgeleri Düzenle'), 'cmd': 'belge_duzenle', 'show_as': 'button',
                     'object_key': 'data_key'}
                ],
                'key': teklif.key}
            self.output['objects'].append(list_item)
        self.form_out(form)

    def teklif_belgeleri_indir(self):
        teklif = BAPTeklif.objects.get(self.current.input['data_key'])
        belge_urls = [get_file_url(belge.belge) for belge in teklif.Belgeler]
        self.set_client_cmd('download')
        self.current.output['download_url'] = belge_urls[0]

    def teklif_belgeleri_duzenle(self):
        self.current.task_data['new'] = False
        self.current.task_data['data_key'] = self.current.input['data_key']
        teklif = BAPTeklif.objects.get(self.current.input['data_key'])
        self.form_out(
            FirmaTeklifForm(teklif, current=self.current, title=__(u"Teklif Belgeleri Düzenleme")))

    def islem_sonrasi_mesaj(self):
        self.current.output['msgbox'] = {"type": "info",
                                         "title": __(u'Firma Teklifleri'),
                                         "msg": __(u"Teklif belgeleriniz sisteme başarıyla"
                                                   u" yüklenmiştir. Mevcut Tekliflerim altından"
                                                   u" teklif belgelerinize ulaşabilir ve "
                                                   u"belgelerinizde değişiklikler yapabilirsiniz.")}

    def teklif_ver(self):
        self.current.task_data['new'] = True
        form = FirmaTeklifForm(BAPTeklif(), current=self.current, title=__(u"Bütçe Kalemi Teklifi"))
        form.help_text = __(
            u"Lütfen %s adlı bütçe kalemine yaptığınız teklife "
            u"ilişkin belgeleri sisteme yükleyiniz.") % self.object.ad
        self.form_out(form)

    def teklif_belge_kontrol(self):
        self.current.task_data['belge'] = True if len(self.input['form']['Belgeler']) else False

    def belge_eksikligi_mesaj(self):
        self.current.output['msgbox'] = {"type": "warning",
                                         "title": __(u'Belge Eksikliği'),
                                         "msg": __(u"Teklifinize ilişkin belge ya da belgeleri"
                                                   u" yüklemeniz gerekmektedir. Lütfen kontrol edip"
                                                   u" tekrar deneyiniz. ")}

    def teklif_kaydet(self):
        teklif = BAPTeklif(butce=self.object, firma=self.firma)
        form_belgeler = [(belge['belge'], belge['aciklama']) for belge in
                         self.input['form']['Belgeler']]
        [teklif.Belgeler(belge=belge, aciklama=aciklama) for belge, aciklama in form_belgeler]
        teklif.durum = 1
        teklif.blocking_save()

    def teklif_duzenle_kaydet(self):
        teklif = BAPTeklif.objects.get(self.current.task_data['data_key'])
        form_belgeler = [belge['belge'] for belge in self.input['form']['Belgeler']]

        mevcut = []
        yeni = []
        for belge in form_belgeler:
            yeni.append(belge) if isinstance(belge, dict) else mevcut.append(belge)

        [belge.remove() for belge in teklif.Belgeler if belge.belge not in mevcut]
        [teklif.Belgeler(belge=belge) for belge in yeni]
        teklif.blocking_save()

    @obj_filter
    def firma_kayit_actions(self, obj, result):
        result['actions'] = [
            {'name': _(u'Teklifte Bulun'), 'cmd': 'teklif_ver', 'mode': 'normal',
             'show_as': 'button'},
        ]

    @list_query
    def onaylanmis_butce_kalemleri_listele(self, queryset):
        return queryset.filter(teklif_durum=1)

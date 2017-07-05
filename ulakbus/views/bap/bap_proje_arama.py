# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from datetime import datetime

from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import BAPProje
from ulakbus.models import BAPProjeTurleri
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _
from ulakbus.settings import DATE_DEFAULT_FORMAT


class BAPProjeListeleFiltreleForm(JsonForm):
    class Meta:
        title = _(u"Proje Ara")
        always_blank = False
    proje_turu = fields.String(_(u"Proje Türü"), required=False)
    bitis_tarihi_baslangic = fields.Date(_(u"Bitiş Tarihi Başlangıç"), required=False)
    bitis_tarihi_bitis = fields.Date(_(u"Bitiş Tarihi Bitiş"), required=False)
    aranacak_metin = fields.String(_(u"Aranacak Metin"), required=False)
    ara = fields.Button(_(u"Ara"), cmd='ara')


class BAPProjeArama(CrudView):
    class Meta:
        model = "BAPProje"

    def proje_filtrele_listele(self):
        form = BAPProjeListeleFiltreleForm(current=self.current)
        form.set_choices_of('proje_turu', prepare_choices_for_model(BAPProjeTurleri))
        self.form_out(form)
        hata_mesaji = self.current.task_data.pop('hata_mesaji', None)
        if hata_mesaji:
            self.current.output['msgbox'] = {
                'type': 'error',
                "title": _(u"Yanlış ya da Eksik Filtre"),
                "msg": hata_mesaji}
        query_result = self.current.task_data.pop('query_result', None)
        if query_result:
            self.current.output["meta"]["allow_search"] = False
            self.output['objects'] = [
                [_(u'Proje Kodu'), _(u'Proje Türü'), _(u'Proje Adı'), _(u'Yürütücü'),
                 _(u'Bitiş Tarihi')]
            ]
            for qr in query_result:
                proje = BAPProje.objects.get(qr['key'])
                kod = proje.proje_no
                tur = proje.tur().__unicode__()
                ad = proje.ad
                yurutucu = proje.yurutucu().__unicode__()
                bitis_tarihi = proje.bitis_tarihi

                list_item = {
                    "fields": [kod, tur, ad, yurutucu, bitis_tarihi],
                    "actions": [{
                            'name': _(u'Detay'),
                            'cmd': 'detay',
                            'mode': 'normal',
                            'show_as': 'button'
                        }],
                    "key": qr['key']
                }
                self.output['objects'].append(list_item)

    def filtreleri_kontrol_et(self):
        f = self.input['form']
        if f['aranacak_metin'] or f['proje_turu'] or (
                    f['bitis_tarihi_baslangic'] and f['bitis_tarihi_bitis']):
            self.current.task_data['cmd'] = 'gecerli_filtre'
        else:
            self.current.task_data['cmd'] = 'gecersiz_filtre'
            self.current.task_data['hata_mesaji'] = _(u"""En az bir filtre girmelisiniz. Lütfen
            filtrelerinizi kontrol ediniz.""")

    def filtreleri_uygula(self):
        f = self.current.task_data['BAPProjeListeleFiltreleForm']
        qs = BAPProje.objects
        query_params = dict()
        aranacak_metin = f.get('aranacak_metin', None)
        proje_turu = f.get('proje_turu', None)
        bitis_tarihi_baslangic = f.get('bitis_tarihi_baslangic', None)
        bitis_tarihi_bitis = f.get('bitis_tarihi_bitis', None)

        if proje_turu:
            query_params['tur_id'] = proje_turu
        if bitis_tarihi_baslangic is not None and bitis_tarihi_bitis is not None:
            bitis_tarihi_baslangic = datetime.strptime(bitis_tarihi_baslangic, DATE_DEFAULT_FORMAT)
            bitis_tarihi_bitis = datetime.strptime(bitis_tarihi_bitis, DATE_DEFAULT_FORMAT)
            query_params['bitis_tarihi__range'] = [bitis_tarihi_baslangic, bitis_tarihi_bitis]

        qs = qs.all(**query_params)
        if aranacak_metin:
            qs = qs.search_on('ad', 'anahtar_kelimeler', 'konu_ve_kapsam', contains=aranacak_metin)

        qs = qs.values('key')

        self.current.task_data['query_result'] = qs

    def detay_goster(self):
        self.show()
        form = JsonForm(title=self.object.__unicode__())
        form.geri = fields.Button(_(u"Geri"))
        obj = {
            _(u"Konu ve Kapsam"): self.object.konu_ve_kapsam,
            _(u"Literatür Özeti"): self.object.literatur_ozeti,
            _(u"Özgün Değer"): self.object.ozgun_deger,
            _(u"Hedef ve Amaç"): self.object.hedef_ve_amac,
            _(u"Yöntem"): self.object.yontem,
            _(u"Başarı Ölçütleri"): self.object.basari_olcutleri,
            _(u"B Planı"): self.object.b_plani
        }

        self.output['object'] = obj
        self.form_out(form)
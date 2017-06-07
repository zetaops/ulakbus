# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.view_helpers import prepare_choices_for_model
from ulakbus.models import BAPProje
from ulakbus.models import BAPProjeTurleri
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class BAPProjeListeleFiltreleForm(JsonForm):
    proje_turu = fields.String(_(u"Proje Türü"), required=False)
    bitis_tarihi_baslangic = fields.Date(_(u"Bitiş Tarihi Başlangıç"), required=False)
    bitis_tarihi_bitis = fields.Date(_(u"Bitiş Tarihi Bitiş"), required=False)
    aranacak_metin = fields.String(_(u"Aranacak Metin"), required=False)
    ara = fields.Button(_(u"Ara"), cmd='ara')


class BAPProjeArama(CrudView):
    def proje_filtrele_listele(self):
        form = BAPProjeListeleFiltreleForm(title=_(u"Proje Ara"))
        form.set_choices_of('proje_turu', prepare_choices_for_model(BAPProjeTurleri))
        self.form_out(form)
        hata_mesaji = self.current.task_data.pop('hata_mesaji', None)
        if hata_mesaji:
            self.current.output['msgbox'] = {
                'type': 'error',
                "title": _(u"Yanlış ya da Eksik Filtre"),
                "msg": hata_mesaji}

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
        if bitis_tarihi_baslangic and bitis_tarihi_bitis:
            # Date 'e çevir todo
            query_params['bitis_tarihi__range'] = [bitis_tarihi_baslangic, bitis_tarihi_bitis]

        qs = qs.all(**query_params)
        if aranacak_metin:
            qs = qs.search_on('ad', 'anahtar_kelimeler', 'konu_ve_kapsam', contains=aranacak_metin)

        qs = qs.values('proje_no', 'tur_id', 'ad', 'yurutucu_id', 'bitis_tarihi', 'key')

        self.current.task_data['query_result'] = qs

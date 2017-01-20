# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import OrderedDict

import six

from ulakbus.lib.cache import AkademikPerformans
from ulakbus.models.akademik_faaliyet import AkademikFaaliyetTuru

__author__ = 'Ali Riza Keles'

from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.lib.translation import gettext_lazy as __
from zengine.lib.translation import gettext as _
from ulakbus.models.akademik_faaliyet import AkademikFaaliyetTuru as Aft
from ulakbus.models.akademik_faaliyet import AkademikFaaliyet as Af


def faaliyet_gorev_secenekler(faaliyet):
    faaliyet_gorev_map = {
        "Proje": [
            "Yürütücü",
            "Araştırmacı öğretim üyesi",
            "Araştırmacı; araştırma görevlisi, öğretim görevlisi, okutman ve uzman",
            "Danışman; kamu kurum ve kuruluşları ile tüzel kişilerin yürütmüş olduğu projelerde",
            "Danışman; yürütücünün gerçek kişi olduğu projelerde"],
        "Yayın": [
            "1. İsim",
            "2. İsim",
            "3. İsim",
            "4. ve sonrası",
            "Senior isim (makaledeki son isim) (yayının yapıldığı alanda daha önce en az on adet uluslararası yayın yapmış olmak şartıyla)"
        ],
        "Ödül": [
            "1. İsim",
            "2. İsim",
            "3. İsim",
            "4. ve sonrası",
            "Senior isim (makaledeki son isim) (yayının yapıldığı alanda daha önce en az on adet uluslararası yayın yapmış olmak şartıyla)"
        ]
    }
    if faaliyet in faaliyet_gorev_map:
        return [(g, g) for g in faaliyet_gorev_map[faaliyet]]
    else:
        return []


def faaliyet_secenekler():
    turler = Aft.objects.distinct_values_of("faaliyet")
    return [(tur.title(), tur.title()) for tur in turler.keys()]


def alt_faaliyet_secenekler(faaliyet):
    return [(s, s) for s in
            set(Aft.objects.filter(faaliyet=faaliyet).values_list('alt_faaliyet')) if s is not None]


class FaaliyetSec(JsonForm):
    faaliyetler = faaliyet_secenekler()
    faaliyet = fields.String(__(u"Faaliyet Seçiniz"),
                             choices=faaliyetler, default=faaliyetler[0][0])
    ileri = fields.Button(__(u"Ileri"))


class AltFaaliyetSec(JsonForm):
    ileri = fields.Button(__(u"Ileri"))


class AkademikFaaliyetForm(JsonForm):
    class Meta:
        exclude = ['personel', 'gorev', 'tur']

    kaydet = fields.Button(__(u"Kaydet"))


class AkademikFaaliyet(CrudView):
    class Meta:

        allow_search = False
        model = "AkademikFaaliyet"
        object_actions = []

    def listele(self):
        personel_id = self.current.user.personel.key
        self.current.task_data['personel_id'] = personel_id
        self.list()

    def goruntule(self):
        self.show()
        self.output['object'].update({
            "Faaliyet": self.object.tur.faaliyet,
            "Alt Faaliyet": self.object.tur.alt_faaliyet,
            "Detay": self.object.tur.detay,
            "Puan": six.text_type(self.object.tur.puan),
            "Oran": six.text_type(self.object.tur.oran),
        })

        form = JsonForm()
        form.geri = fields.Button(__(u"Listeye Dön"), cmd='iptal')
        self.form_out(form)

    def faaliyet_sec(self):
        _form = FaaliyetSec(title=_("Faaliyet Türünü Seçiniz"))
        self.form_out(_form)

    def faaliyet_kaydet(self):
        self.current.task_data['faaliyet'] = self.current.input['form']['faaliyet']
        self.current.task_data['alt_faaliyetler'] = alt_faaliyet_secenekler(
            self.current.task_data['faaliyet'])

    def alt_faaliyet_sec(self):
        alt_faaliyetler = alt_faaliyet_secenekler(self.current.task_data['faaliyet'])
        _form = AltFaaliyetSec(title=_(u"Alt Faaliyet Seçiniz"))
        _form.alt_faaliyet = fields.String(_(u"Alt Faaliyet Seçiniz"),
                                           choices=alt_faaliyetler, default=alt_faaliyetler[0][0])
        self.form_out(_form)

    def alt_faaliyet_kaydet(self):
        self.current.task_data['alt_faaliyet'] = self.current.input['form']['alt_faaliyet']

    def detay_sec(self):
        _form = JsonForm(title=_("Detay Seçiniz"))

        if 'alt_faaliyet' in self.current.task_data:
            q = Aft.objects.filter(
                alt_faaliyet=self.current.task_data['alt_faaliyet'])
        else:
            q = Aft.objects.filter(
                faaliyet=self.current.task_data['faaliyet'])

        turler = q.values("key", "detay")

        detaylar = [(tur['key'], tur['detay']) for tur in turler]

        _form.detay = fields.String(choices=detaylar, default=detaylar[0][0])
        _form.ileri = fields.Button(__(u"Ileri"))
        self.form_out(_form)

    def detay_kaydet(self):
        self.current.task_data['detay'] = self.current.input['form']['detay']
        self.current.task_data['gorevler'] = faaliyet_gorev_secenekler(
            self.current.task_data['faaliyet'])

    def gorev_sec(self):
        _form = JsonForm(title=_("Görev Seçiniz"))
        gorevler = self.current.task_data['gorevler']
        _form.gorev = fields.String(choices=gorevler, default=gorevler[0][0])
        _form.ileri = fields.Button(__(u"Ileri"))
        self.form_out(_form)

    def gorev_kaydet(self):
        self.current.task_data['gorev'] = self.current.input['form']['gorev']

    def proje_bilgileri(self):
        _form = AkademikFaaliyetForm(Af(),
                                     current=self.current, title=_(u"Faaliyet bilgilerini giriniz"))
        self.form_out(_form)

    def kaydet(self):
        fd = self.current.input['form']
        faaliyet = Af(
            ad=fd['ad'],
            baslama=fd['baslama'],
            bitis=fd['bitis'],
            durum=fd['durum'],
            gorev=self.current.task_data['gorev'],
            kac_kisiyle_yapildi=fd['kac_kisiyle_yapildi'],
            tur_id=self.current.task_data['detay'],
            personel=self.current.role.user.personel
        )

        faaliyet.blocking_save()

        if 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']

    def kayit_bilgisi_ver(self):
        # self.current.output['msgbox'] = {
        #     "type": "info",
        #     "title": _(u"Başarılı"),
        #     "msg": "Yeni faaliyet başarıyla kaydedilmiştir"}
        _form = JsonForm(title=__(u"Akademik Faaliyet Kayit"))
        _form.help_text = "Yeni faaliyet başarıyla kaydedilmiştir."
        _form.geri = fields.Button(__(u"Listeye Geri Don"), cmd='iptal')
        self.form_out(_form)

    @obj_filter
    def saglik_raporu_islem(self, obj, result):
        result['actions'].extend([
            {'name': _(u'Sil'), 'cmd': 'sil', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Görüntüle'), 'cmd': 'goster', 'mode': 'normal', 'show_as': 'button'},
        ])

    @list_query
    def list_by_personel_id(self, queryset):
        return queryset.filter(personel_id=self.current.task_data['personel_id'])


class HesaplamaSonucuGoster(CrudView):

    def hesapla(self):
        self.current.task_data['performans'] = AkademikPerformans().get_or_set()

    def goster(self):
        cached_data_with_db_keys = self.current.task_data['performans']
        data_with_showable_keys = []
        for d in cached_data_with_db_keys.items():
            key = AkademikFaaliyetTuru.objects.get(key=d[0]).__unicode__()
            value = d[1]
            line = OrderedDict({})
            line["Faaliyet"] = key
            line["Toplam Sayı"] = value
            data_with_showable_keys.append(line)

        self.set_client_cmd('show')

        self.output['object_title'] = 'Akademik Performans Sayıları'
        self.output['object_key'] = self.object.key
        self.output['object'] = {
            "type": "table-multiRow",
            "fields": data_with_showable_keys,
            "actions": ""}

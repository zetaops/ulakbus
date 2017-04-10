# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import BAPIsPaketi, BAPIs
from ulakbus.lib.date_time_helper import iki_tarih_arasinda_mi

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __

from pyoko import ListNode

from datetime import datetime


class IsPaketiHazirlaForm(JsonForm):
    ad = fields.String(__(u"İş Paketinin Adı"))
    baslama_tarihi = fields.Date(__(u"Başlama Tarihi"), format="%d.%m.%Y")
    bitis_tarihi = fields.Date(__(u"Bitiş Tarihi"), format="%d.%m.%Y")

    class Isler(ListNode):
        class Meta:
            title = __(u"İş Ekle")

        ad = fields.String(__(u"Bap İş"))
        baslama_tarihi = fields.Date(__(u"Başlama Tarihi"), format="%d.%m.%Y")
        bitis_tarihi = fields.Date(__(u"Bitiş Tarihi"), format="%d.%m.%Y")

    kaydet = fields.Button(__(u"Kaydet"))
    iptal = fields.Button(__(u"İptal"), cmd='iptal', form_validation=False)


class IsPaketiHazirlama(CrudView):
    class Meta:
        model = 'BAPIsPaketi'

    def __init__(self, current):
        CrudView.__init__(self, current)
        if 'object_id' in self.current.task_data and self.cmd == 'add_edit_form' and \
                'object_id' not in self.input:
            del self.current.task_data['object_id']
            self.object = BAPIsPaketi()

    def zaman_cizelgesi(self):
        """
        .. code-block:: python
            # response:
            {
                'is_paketi_takvimi': {
                    'tarih': [{
                        'yil': int,
                        'ay': int
                        },],
                    'is_paketleri':[
                            {'ad': string,
                             'key': string,
                             'baslama_tarihi': string,
                             'bitis_tarihi': string,
                             'is': [{'key': string,
                                     'ad': string
                                     'baslama_tarihi': string,
                                     'bitis_tarihi': string},]
                             'actions': [ # per row actions
                                {
                                  "cmd": "add_edit_form",
                                  "name": "Düzenle",
                                  "show_as": "button",
                                  "mode": "normal"
                                },
                                {
                                  "cmd": "delete",
                                  "name": "Sil",
                                  "show_as": "button",
                                  "mode": "normal"
                            }
                    ]
                }
            }
        """

        item = {'is_paketleri': []}

        tarih = [{'yil': 2017, 'ay': 1},
                 {'yil': 2017, 'ay': 2},
                 {'yil': 2017, 'ay': 3},
                 {'yil': 2017, 'ay': 4},
                 {'yil': 2017, 'ay': 5},
                 {'yil': 2017, 'ay': 6}, ]

        item['tarih'] = tarih

        is_paketleri = BAPIsPaketi.objects.filter()
        for is_paketi in is_paketleri:
            item['is_paketleri'].append({'ad': is_paketi.ad,
                                         'key': is_paketi.key,
                                         'baslama_tarihi':
                                             datetime.strftime(is_paketi.baslama_tarihi,
                                                               '%d.%m.%Y'),
                                         'bitis_tarihi':
                                             datetime.strftime(is_paketi.bitis_tarihi,
                                                               '%d.%m.%Y'),
                                         'is': [{'key': bap_is.isler.key,
                                                 'ad': bap_is.isler.ad,
                                                 'baslama_tarihi':
                                                     datetime.strftime(bap_is.isler.baslama_tarihi,
                                                                       '%d.%m.%Y'),
                                                 'bitis_tarihi':
                                                     datetime.strftime(bap_is.isler.bitis_tarihi,
                                                                       '%d.%m.%Y')}
                                                for bap_is in is_paketi.Isler]})

        self.current.output['is_paketi_takvimi'] = item

        form = JsonForm(title=_(u"Bap İş Paketi Takvimi"))
        form.yeni_paket = fields.Button(_(u"Yeni İş Paketi Ekle"))
        self.form_out(form)

    def add_edit_form(self):
        self.form_out(IsPaketiHazirlaForm(title=_(u"İş Paketi Ekle")))

    def is_paketi_kontrolu_yap(self):
        hata_msg = ''

        ip_baslama_tarihi = datetime.strptime(self.input['form']['baslama_tarihi'],
                                              '%d.%m.%Y').date()
        ip_bitis_tarihi = datetime.strptime(self.input['form']['bitis_tarihi'],
                                            '%d.%m.%Y').date()

        if ip_bitis_tarihi < ip_baslama_tarihi:
            hata_msg = _(u"Bitiş tarihi, başlangıç tarihinden küçük olamaz")

        if 'Isler' in self.input['form'] and not hata_msg:
            for bap_is in self.input['form']['Isler']:
                bas = datetime.strptime(bap_is['baslama_tarihi'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                bit = datetime.strptime(bap_is['bitis_tarihi'], '%Y-%m-%dT%H:%M:%S.%fZ').date()
                if not iki_tarih_arasinda_mi(bas, bit, ip_baslama_tarihi, ip_bitis_tarihi):
                    hata_msg = _(u"%s işinizin tarihi iş paketinizin tarih aralığında değil. "
                                 u"Lütfen tekrardan düzenleyiniz.") % bap_is['ad']
                    break
        elif 'Isler' not in self.input['form']:
            hata_msg = _(u"En az bir tane iş eklemelisiniz")

        if hata_msg:
            self.current.task_data['sonuc'] = 0
            self.current.output['msgbox'] = {"type": "warning",
                                             "title": _(u'Kayıt Başarısız Oldu!'),
                                             "msg": hata_msg}
        else:
            self.current.task_data['sonuc'] = 1

    def kaydet(self):
        is_paketi = BAPIsPaketi()
        is_paketi.ad = self.input['form']['ad']
        is_paketi.baslama_tarihi = datetime.strptime(self.input['form']['baslama_tarihi'],
                                                     '%d.%m.%Y').date()
        is_paketi.bitis_tarihi = datetime.strptime(self.input['form']['bitis_tarihi'],
                                                   '%d.%m.%Y').date()
        isler = [BAPIs(ad=bap_is['ad'],
                       baslama_tarihi=datetime.strptime(bap_is['baslama_tarihi'],
                                                        '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                       bitis_tarihi=datetime.strptime(bap_is['bitis_tarihi'],
                                                      '%Y-%m-%dT%H:%M:%S.%fZ').date()).save()
                 for bap_is in self.input['form']['Isler']]
        [is_paketi.Isler(isler=b_is) for b_is in isler]
        is_paketi.blocking_save()

    def confirm_deletion(self):
        pass

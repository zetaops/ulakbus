# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.exceptions import IntegrityError
from ulakbus.models import BAPIsPaketi, BAPIs, BAPProje
from ulakbus.lib.date_time_helper import iki_tarih_arasinda_mi

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __

from pyoko import ListNode

from datetime import datetime


class IsPaketiHazirlaForm(JsonForm):
    class Meta:
        always_blank = False

    ad = fields.String(__(u"İş Paketinin Adı"))
    baslama_tarihi = fields.Date(__(u"Başlama Tarihi"), format="%d.%m.%Y")
    bitis_tarihi = fields.Date(__(u"Bitiş Tarihi"), format="%d.%m.%Y")

    class Isler(ListNode):
        class Meta:
            title = __(u"İş Ekle")

        ad = fields.String(__(u"Bap İş"))
        baslama_tarihi = fields.Date(__(u"Başlama Tarihi"))
        bitis_tarihi = fields.Date(__(u"Bitiş Tarihi"))

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

        if 'iptal' in current.task_data['cmd'] and 'IsPaketiHazirlaForm' in self.current.task_data:
            del current.task_data['IsPaketiHazirlaForm']

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

        item = {
            'options': {
                'maxHeight': 850,
                'viewScale': "month",
                'columnWidth': 80
            },
            'data': []
        }

        is_paketleri = BAPIsPaketi.objects.filter(proje_id=self.current.task_data.get(
            'bap_proje_id', None))
        for is_paketi in is_paketleri:
            item['data'].append(
                {
                    'name': is_paketi.ad,
                    'children': [bap_is.isler.ad for bap_is in is_paketi.Isler]
                })
            for bap_is in is_paketi.Isler:
                item['data'].append(
                    {
                        'name': bap_is.isler.ad,
                        'tooltips': True,
                        'tasks': [
                            {
                                'id': bap_is.isler.key,
                                'name': bap_is.isler.ad,
                                'color': '#a61229',
                                'from': bap_is.isler.baslama_tarihi.strftime(
                                    '%Y-%m-%dT%H:%M:%S.%fZ'),
                                'to': bap_is.isler.bitis_tarihi.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                            }
                        ]
                    }
                )
        self.current.output['gantt_chart'] = item

        form = JsonForm(title=_(u"Bap İş Paketi Takvimi"))
        form.yeni_paket = fields.Button(_(u"Yeni İş Paketi Ekle"),cmd = 'add_edit_form')
        form.bitir = fields.Button(_(u"Tamam"), cmd='bitir')
        self.form_out(form)
        error_msg = self.current.task_data.get('integrity_error_msg', None)
        if error_msg:
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'İş Paketi Ekleme Başarısız'),
                "msg": error_msg
            }
            del self.current.task_data['integrity_error_msg']

    def add_edit_form(self):
        # if 'IsPaketiHazirlaForm' in self.current.task_data:
        #     for i in range(len(self.current.task_data['IsPaketiHazirlaForm']['Isler'])):
        #         bas = self.current.task_data['IsPaketiHazirlaForm']['Isler'][i]['baslama_tarihi']
        #         bit = self.current.task_data['IsPaketiHazirlaForm']['Isler'][i]['bitis_tarihi']
        #         self.current.task_data['IsPaketiHazirlaForm']['Isler'][i]['baslama_tarihi'] = \
        #             datetime.strftime(datetime.strptime(bas, '%Y-%m-%dT%H:%M:%S.%fZ').date(),
        #                               '%d.%m.%Y')
        #         self.current.task_data['IsPaketiHazirlaForm']['Isler'][i]['bitis_tarihi'] = \
        #             datetime.strftime(datetime.strptime(bit, '%Y-%m-%dT%H:%M:%S.%fZ').date(),
        #                               '%d.%m.%Y')

        self.form_out(IsPaketiHazirlaForm(current=self.current, title=_(u"İş Paketi Ekle")))

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
                try:
                    format_date = '%d.%m.%Y'
                    datetime.strptime(bap_is['baslama_tarihi'], format_date).date()
                except ValueError:
                    format_date = '%Y-%m-%dT%H:%M:%S.%fZ'

                except TypeError:
                    hata_msg = _(u"Lütfen tarihlerinizi kontrol edip düzeltiniz.")
                    break

                bas = datetime.strptime(bap_is['baslama_tarihi'], format_date).date()
                bit = datetime.strptime(bap_is['bitis_tarihi'], format_date).date()
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
        is_paketi.proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        try:
            is_paketi.blocking_save()
        except IntegrityError:
            self.current.task_data['integrity_error_msg'] = _(u"Aynı isimde birden "
                                                              u"fazla iş paketi olamaz!")

        if 'IsPaketiHazirlaForm' in self.current.task_data:
            del self.current.task_data['IsPaketiHazirlaForm']

    def confirm_deletion(self):
        pass

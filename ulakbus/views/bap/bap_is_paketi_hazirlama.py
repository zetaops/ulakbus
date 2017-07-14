# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.exceptions import IntegrityError
from pyoko import ListNode

from ulakbus.models import BAPIsPaketi, BAPIs, BAPProje
from ulakbus.lib.date_time_helper import iki_tarih_arasinda_mi

from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, gettext_lazy as __

from datetime import datetime
from collections import defaultdict
from pyoko.fields import DATE_TIME_FORMAT


def get_format_date(tarih):
    try:
        format_date = '%d.%m.%Y'
        datetime.strptime(tarih, format_date).date()
    except ValueError:
        format_date = '%Y-%m-%dT%H:%M:%S.%fZ'

    return format_date


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
        if 'is_paketi_yok_msg' in self.current.task_data:
            self.current.msg_box(title=_(u'Mevcut İş Paketi Bulunamadı!'),
                                 msg=_(u"İş paketi silmek veya düzenlemek istiyorsanız, "
                                       u"en az 1 tane iş paketinizin olması lazım."),
                                 typ='warning')
            del self.current.task_data['is_paketi_yok_msg']

        item = {
            'options': {
                'maxHeight': 350,
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
                    'name': is_paketi.ad
                })
            for bap_is in is_paketi.Isler:
                item['data'].append(
                    {
                        'parent': is_paketi.ad,
                        'name': bap_is.isler.ad,
                        'tooltips': True,
                        'tasks': [
                            {
                                'id': bap_is.isler.key,
                                'name': bap_is.isler.ad,
                                'color': '#a61229',
                                'from': bap_is.isler.baslama_tarihi.strftime(
                                    DATE_TIME_FORMAT),
                                'to': bap_is.isler.bitis_tarihi.strftime(DATE_TIME_FORMAT)
                            }
                        ]
                    }
                )
        self.current.output['gantt_chart'] = item

        form = JsonForm(title=_(u"Bap İş Paketi Takvimi"))
        form.yeni_paket = fields.Button(_(u"Yeni İş Paketi Ekle"), cmd='add_edit_form')
        form.duzenle = fields.Button(_(u"İş Paketini Düzenle"), cmd='duzenle_veya_sil')
        form.sil = fields.Button(_(u"İş Paketini Sil"), cmd='duzenle_veya_sil')
        form.bitir = fields.Button(_(u"Tamam"), cmd='bitir')
        self.form_out(form)
        error_msg = self.current.task_data.get('integrity_error_msg', None)
        if error_msg:
            self.current.output['msgbox'] = {
                'type': 'info', "title": _(u'İş Paketi Ekleme Başarısız'),
                "msg": error_msg
            }
            del self.current.task_data['integrity_error_msg']

    def duzenle_sil_kontrol(self):
        proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        is_paketleri = [(ispaketi.key, ispaketi.ad) for ispaketi in BAPIsPaketi.objects.filter(
            proje=proje)]
        if not is_paketleri:
            self.current.task_data['cmd'] = 'is_paketi_yok'
            self.current.task_data['is_paketi_yok_msg'] = 1
        else:
            self.current.task_data['is_paketleri'] = is_paketleri
            if self.input['form']['duzenle']:
                self.current.task_data['is_paketi_durum'] = 1
            else:
                self.current.task_data['is_paketi_durum'] = 0

    def is_paketi_sec(self):
        form = JsonForm(title=_(u"İş Paketi Seç"))
        form.is_paketi = fields.String(_(u"İş Paketi"),
                                       choices=self.current.task_data['is_paketleri'])
        form.ilerle = fields.Button(_(u"İlerle"))
        self.form_out(form)

    def add_edit_form(self):
        form = IsPaketiHazirlaForm(current=self.current,
                                   title=_(u"İş Paketi Ekle"))
        if 'is_paketi' in self.input['form']:
            form.title = _(u"İş Paketi Düzenle")
            self.current.task_data['is_paketi_id'] = self.input['form']['is_paketi']
            data = self.current.task_data['is_paketleri_form'][self.input['form']['is_paketi']]
            [form.Isler(ad=bap_is['ad'],
                        baslama_tarihi=datetime.strptime(
                           bap_is['baslama_tarihi'],
                           get_format_date(bap_is['baslama_tarihi'])).date(),
                        bitis_tarihi=datetime.strptime(
                           bap_is['bitis_tarihi'],
                           get_format_date(bap_is['bitis_tarihi'])).date())
             for bap_is in data['Isler']]

            isler = data.pop('Isler')
            form.set_data(data)
            data['Isler'] = isler

        self.form_out(form)

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
                format_date = get_format_date(bap_is['baslama_tarihi'])
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
        if 'is_paketi_id' in self.current.task_data:
            is_paketi = BAPIsPaketi.objects.get(self.current.task_data['is_paketi_id'])
            del self.current.task_data['is_paketi_id']
        else:
            is_paketi = BAPIsPaketi()

        is_paketi.ad = self.input['form']['ad']
        is_paketi.baslama_tarihi = datetime.strptime(self.input['form']['baslama_tarihi'],
                                                     '%d.%m.%Y').date()
        is_paketi.bitis_tarihi = datetime.strptime(self.input['form']['bitis_tarihi'],
                                                   '%d.%m.%Y').date()
        isler = [BAPIs(ad=bap_is['ad'],
                       baslama_tarihi=datetime.strptime(
                           bap_is['baslama_tarihi'],
                           get_format_date(bap_is['baslama_tarihi'])).date(),
                       bitis_tarihi=datetime.strptime(
                           bap_is['bitis_tarihi'],
                           get_format_date(bap_is['bitis_tarihi'])).date()).save()
                 for bap_is in self.input['form']['Isler']]
        is_paketi.Isler.node_stack = []
        is_paketi.Isler._data = []
        [is_paketi.Isler(isler=b_is) for b_is in isler]
        is_paketi.proje = BAPProje.objects.get(self.current.task_data['bap_proje_id'])
        try:
            is_paketi.blocking_save()
        except IntegrityError:
            self.current.task_data['integrity_error_msg'] = _(u"Aynı isimde birden "
                                                              u"fazla iş paketi olamaz!")

        if 'IsPaketiHazirlaForm' in self.current.task_data:
            if 'is_paketleri_form' not in self.current.task_data:
                self.current.task_data['is_paketleri_form'] = defaultdict(dict)
            self.current.task_data['is_paketleri_form'][is_paketi.key] = \
                self.current.task_data['IsPaketiHazirlaForm']

            del self.current.task_data['IsPaketiHazirlaForm']

    def confirm_deletion(self):
        self.current.task_data['is_paketi_id'] = self.input['form']['is_paketi']
        self.object = BAPIsPaketi.objects.get(self.input['form']['is_paketi'])

        form = JsonForm(title=_(u"İş Paketi Silme İşlemi"))
        form.help_text = _(u"%s iş paketini silmek istiyor musunuz?") % self.object
        form.evet = fields.Button(_(u"Sil"), cmd='delete')
        form.hayir = fields.Button(_(u"İptal"))
        self.form_out(form)

    def delete(self):
        self.object = BAPIsPaketi.objects.get(self.current.task_data['is_paketi_id'])
        CrudView.delete(self)
        del self.current.task_data['is_paketi_id']

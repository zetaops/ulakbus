# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from collections import OrderedDict

from ulakbus.models import DersEtkinligi, Room, Donem
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView
from ulakbus.lib.date_time_helper import map_etkinlik_hafta_gunleri, HAFTA
from zengine.lib.translation import gettext as _, gettext_lazy


class DerslikSecimFormu(JsonForm):
    """
    Derslik Seç adımında kullanılan formdur.

    """
    ileri = fields.Button(gettext_lazy(u"İleri"))


class DerslikDersProgrami(CrudView):
    """ Derslik Ders Programı İş Akışı
    Derslik Ders Programi,bir bölümün sahip olduğu dersliklere ait ders programlarını gösterir ve
    kullanıcının ders programlarını yazdırabilmesine olanak sağlar.

    Bu iş akışı 4 adımdan oluşur.

    Ders Etkinliklerini Kontrol Et:
    Yayınlanmış ders etkinlikleri var mı yok mu diye kontrol eder.

    Bilgi Ver:
    Yayınlanmış ders etkinlikleri yok ise ekrana bilgi mesajı basılır.

    Derslik Seç:
    Derslikler listelenir.

    Derslik Ders Programını Göster:
    Seçilen dersliğe ait ders programlarını ekrana basar.

    """
    class Meta:
        model = 'DersEtkinligi'

    def ders_etkinliklerini_kontrol_et(self):
        """
        Yayınlanmış ders etkinlikleri var mı yok mu diye kontrol eder.

        """
        length = len(DersEtkinligi.objects.filter(published=True,
                                                  donem=Donem.guncel_donem(self.current),
                                                  bolum=self.current.role.unit))
        self.current.task_data['yayinlanmamis_ders_sayisi'] = length

    def bilgi_ver(self):
        """
        Yayınlanmış ders etkinlikleri yok ise  ekrana bilgi mesajı basılır.

        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Yayınlanmamış Dersler'),
            'msg': _(u"Yayınlanmış dersler bulunmamaktadır.")
        }

    def derslik_sec(self):
        """
        Derslikler listelenir.

        """
        _form = DerslikSecimFormu(title=_(u'Derslik Seçiniz'), current=self.current)
        ders_etkinlikleri = DersEtkinligi.objects.filter(published=True,
                                                         donem=Donem.guncel_donem(self.current),
                                                         bolum=self.current.role.unit)
        _choices = [(_etkinlik.room.key, _etkinlik.room.__unicode__())
                    for _etkinlik in ders_etkinlikleri]
        _form.derslik = fields.Integer(choices=_choices)
        self.form_out(_form)

    def derslik_ders_programini_goster(self):
        """
        Seçilen dersliğe ait ders programlarını ekrana basar.

        """
        room = Room.objects.get(self.current.input['form']['derslik'])
        hafta = dict(HAFTA)
        self.output['objects'] = [hafta]
        d_etkinlikleri = DersEtkinligi.objects.filter(room=room,
                                                      published=True,
                                                      donem=Donem.guncel_donem(self.current))
        ders_etkinlikleri = map_etkinlik_hafta_gunleri(
            d_etkinlikleri.order_by(
                'gun', 'baslangic_saat',
                'bitis_saat','baslangic_dakika', 'bitis_dakika'))
        # Bir güne ait maximum etkinlik sayısı.
        max_etkinlik = max(map(len, ders_etkinlikleri.values()))
        for i in range(max_etkinlik):
            ders_etkinlikleri_dict = OrderedDict({})
            for hafta_gun in hafta.keys():
                if hafta_gun in ders_etkinlikleri:
                    try:
                        etkinlik = ders_etkinlikleri[hafta_gun][i]
                        ders_etkinlikleri_dict[hafta[hafta_gun]] = etkinlik
                    except IndexError:
                        ders_etkinlikleri_dict[hafta[hafta_gun]] = ""
                else:
                    ders_etkinlikleri_dict[hafta[hafta_gun]] = ""
            item = {
                "type": "table-multiRow",
                "fields": ders_etkinlikleri_dict,
                "actions": False,
                'key': ''
            }
            self.output['objects'].append(item)

        _form = JsonForm(title=_(u"%s Dersliğine Ait Ders Programları") % room.__unicode__())
        _form.yazdir = fields.Button(_(u'Pdf yazdır'))
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

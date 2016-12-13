# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import SinavEtkinligi, Room, Donem
from zengine.forms import JsonForm
from zengine.forms import fields
from zengine.views.crud import CrudView
from collections import OrderedDict
from ulakbus.lib.date_time_helper import map_etkinlik_hafta_gunleri, HAFTA
from zengine.lib.translation import gettext as _, gettext_lazy


class DerslikSecimFormu(JsonForm):
    """
    Derslik Sınav ProgramLaı iş akışının sınav seç adımında kullanılan form.
    """

    ileri = fields.Button(gettext_lazy(u"İleri"))


class DerslikSinavProgramlari(CrudView):
    """ Derslik Sınav Programları
    Derslik Sınav Programları iş akışı, seçilen dersliğe ait sınav programlarını gösterip kullanıcının
    yazdırabilmesine olanak sağlar.

    İş akışı 4 adımdan oluşur.

    Sınav Etkinliklerini Kontrol Et:
    Yayınlanmış sınav etkinlikleri var mı yok mu diye kontrol eder.

    Bilgi Ver:
    Yayınlananmış sınavlar yok ise bilgi mesajı  ekrana basılır.

    Derslik Seç:
    Derslik Seçilir.

    Derslik Sınav Programlarını Göster:
    Seçilen dersliğe ait sınavlar etkinliklerinin ders adını ve tarihi gösterir.

    """

    class Meta:
        model = "SinavEtkinligi"

    def sinav_etkinliklerini_kontrol_et(self):
        """
        Yayınlanmış sınav etkinlikleri var mı yok mu diye kontrol eder.

        """
        sinav_etkinlikleri = SinavEtkinligi.objects.filter(published=True,
                                                           donem=Donem.guncel_donem(self.current),
                                                           bolum=self.current.role.unit)
        self.current.task_data['yayinlanmamis_sinav_sayisi'] = len(sinav_etkinlikleri)

    def bilgi_ver(self):
        """
        Yayınlananmış sınavlar yok ise bilgi mesajı  ekrana basılır.

        """
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Yayınlanmamış Sınavlar'),
            'msg': _(u"Yayınlanmış sınavlar bulunmamaktadır.")
        }

    def derslik_sec(self):
        """
        Derslik Seçilir.

        """
        _form = DerslikSecimFormu(title=_(u"Derslik Seçiniz"), current=self.current)
        _choices = []
        for s_etkinlik in SinavEtkinligi.objects.filter(published=True,
                                                        donem=Donem.guncel_donem(self.current),
                                                        bolum=self.current.role.unit):
            for s_yerleri in s_etkinlik.SinavYerleri:
                if s_etkinlik.SinavYerleri:
                    _choices.append((s_yerleri.room.key, s_yerleri.room.__unicode__()))
        _form.derslik = fields.Integer(choices=_choices)
        self.form_out(_form)

    def derslik_sinav_programlarini_goster(self):
        """
        Seçilen dersliğe ait sınavlar etkinliklerinin ders adını ve tarihi gösterir.

        """

        room = Room.objects.get(self.current.input['form']['derslik'])
        s_etkinlikleri = [s for s in SinavEtkinligi.objects.order_by('tarih') if
                          room in s.SinavYerleri]
        sinav_etkinlikleri = map_etkinlik_hafta_gunleri(s_etkinlikleri)
        hafta = dict(HAFTA)
        self.output['objects'] = [hafta]

        # Bir güne ait maximum etkinlik sayısı.
        max_etkinlik = max(map(len, sinav_etkinlikleri.values()))
        for i in range(max_etkinlik):
            sinav_etkinlik_list = OrderedDict({})
            for hafta_gun in hafta.keys():
                if hafta_gun in sinav_etkinlikleri:
                    try:
                        etkinlik = sinav_etkinlikleri[hafta_gun][i]
                        sinav_etkinlik_list[hafta[hafta_gun]] = etkinlik
                    except IndexError:
                        sinav_etkinlik_list[hafta[hafta_gun]] = ''

                else:
                    sinav_etkinlik_list[hafta[hafta_gun]] = ''
            item = {
                "type": "table-multiRow",
                "fields": sinav_etkinlik_list,
                "actions": False,
                'key': ''
            }
            self.output['objects'].append(item)
        _form = JsonForm(title=_(u"%s Dersliğine Ait Sınav Programlar") % room.__unicode__())
        _form.yazdir = fields.Button(_(u"Pdf Yazdır"))
        self.form_out(_form)
        self.current.output["meta"]["allow_actions"] = False

# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
"""Akademik Takvim

Akademik Takvim İş Akışı modülü.

İş akışı tek adımdan oluşur. Bu adımda giriş yapan kullanıcının bağlı olduğu
birime ait akademik takvim gösterilir. Eğer birime özel bir akademik takvim bulunamazsa
üniversitenin genel takvimi görtüntülenir.

"""

from collections import OrderedDict

from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models.ogrenci import AKADEMIK_TAKVIM_ETKINLIKLERI, Donem, OgretimYili
from ulakbus.models.ogrenci import Takvim
from ulakbus.lib.common import get_akademik_takvim
from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _, format_datetime

__author__ = 'Ali Riza Keles'


class AkademikTakvimView(CrudView):
    """
    CrudView üzerine geliştirilmiştir.

    İş akışının tek adımına karşılık gelen tek bir metoda sahiptir.

    """

    class Meta:
        model = "AkademikTakvim"

    def goster(self):
        """
        AkademikTakvim modelinden kullanıcıya gösterilecek takvime erişir ve bir tablo
        halinde çıktıya ekler.

        Akademik Takvim öğelerinin (takvim etkinlikleri) sırlaması önemli olduğu için
        OrderedDict kullanılmıştır. Data bu sözlüğün içinde sıralandığı haliyle
        seriyalize edilir.

        AKADEMIK_TAKVIM_ETKINLIKLERI önceden tanımlanmış ve sıralanmış bir etkinlikler
        toplamıdır. AkademikTakvim modeli ile birlikte models.ogrenci modülü içinde
        sıralı olarak tanımlanmıştır. Örn::

            AKADEMIK_TAKVIM_ETKINLIKLERI = [
            ('1', 'Yeni Öğrenci Ön Kayıt'),
            ('2', 'Güz Dönem Başlangıcı'),
            ('3', 'Derslerin Acılması'),
            ('4', 'Subelendirme ve Ders Programının Ilan Edilmesi'),

            ...
            ('53', 'Yarıyıl Sınavı Not Giriş'),
            ('54', 'Yarıyıl Sınavı Notlarının Öğrenciye Yayınlanmasi'),
            ('55', 'Öğretim Elemanı Yoklama Girişi'),
            ]

        Kayıtların herbiri bu öğeler için belirli bir tarih veya tarih aralığına denk gelmektedir.

        """
        self.current.output['client_cmd'] = ['show', ]
        etkinlikler = []

        ogretim_yili = OgretimYili.objects.get(yil=Donem.guncel_donem().baslangic_tarihi.year)
        akademik_takvim = get_akademik_takvim(self.current.role.unit, ogretim_yili)

        for e in Takvim.objects.filter(akademik_takvim=akademik_takvim):
            etkinlik = OrderedDict({})
            etkinlik[_(u'Etkinlik')] = dict(AKADEMIK_TAKVIM_ETKINLIKLERI).get(str(e.etkinlik), '')
            etkinlik[_(u'Başlangıç')] = format_datetime(e.baslangic) if e.baslangic else ''
            etkinlik[_(u'Bitiş')] = format_datetime(e.bitis) if e.bitis else ''
            etkinlikler.append(etkinlik)

        # cikti multirow table seklindedir.
        self.output['object'] = {
            "type": "table-multiRow",
            "fields": etkinlikler
        }

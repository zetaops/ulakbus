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
from ulakbus.models.ogrenci import AKADEMIK_TAKVIM_ETKINLIKLERI
from ulakbus.models.ogrenci import AkademikTakvim, Unit
from zengine.views.crud import CrudView

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

        def get_akademik_takvim(unit):
            try:
                akademik_takvim = AkademikTakvim.objects.get(birim_id=unit.key)
                return akademik_takvim
            except ObjectDoesNotExist:
                yoksis_key = unit.parent_unit_no
                birim = Unit.objects.get(yoksis_no=yoksis_key)
                return get_akademik_takvim(birim)

        akademik_takvim = get_akademik_takvim(self.current.role.unit)
        for e in akademik_takvim.Takvim:
            etkinlik = OrderedDict({})
            etkinlik['Etkinlik'] = dict(AKADEMIK_TAKVIM_ETKINLIKLERI).get(str(e.etkinlik), '')
            etkinlik['Başlangıç'] = '{:%d.%m.%Y}'.format(e.baslangic)
            etkinlik['Bitiş'] = '{:%d.%m.%Y}'.format(e.bitis)
            etkinlikler.append(etkinlik)

        # cikti multirow table seklindedir.
        self.output['object'] = {
            "type": "table-multiRow",
            "fields": etkinlikler
        }
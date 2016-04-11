# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import OgrenciProgram


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """
    def test_kayit_silme(self):
        """
        Kayıt silme iş akışı başlatılmadan önce kaydı silinecek öğrenci seçilir.
        Sunucudan dönen ayrılma nedenleri sayısı ile veritabanından dönen ayrılma
        nedenlerinin sayısının eşitliği karşılaştırılıp test edilir.

        İş akışının ilk adımında ayrılma nedeni seçilir ve açıklama yazılır.
        Dönen cevapta msgbox'ın olup olmadığı test edilir.

        İkinci adımda danışmana ve öğrenciye bilgi verilir.

        """

        # Öğrenci İşleri personeline login yaptırılır.
        self.prepare_client('/kayit_sil', username='meshur-ertas')
        resp = self.client.post(id="T8PMMytvrHwhlRnQpBq8B5eB7Ut",
                                param="ogrenci_id",
                                filters={'ogrenci_id': {'values': ["T8PMMytvrHwhlRnQpBq8B5eB7Ut"],
                                                        'type': "check"}})
        # Ayrılma nedenlerini tutan list.
        lst = OgrenciProgram().get_choices_for('ayrilma_nedeni')
        # Sunucudan dönen ayrılma nedenleri sayısı ile veritabanından dönen ayrılma nedenlerinin sayısının
        # eşitliği karşılaştırılır.
        assert len(resp.json['forms']['form'][1]['titleMap']) == len(lst)
        # Kaydı silinecek öğrencinin ayrılma nedeni seçilir ve açıklama yazılır.
        resp = self.client.post(form=dict(ayrilma_nedeni=11, sec=1, aciklama='Yatay Geçiş'))

        assert 'msgbox' in resp.json

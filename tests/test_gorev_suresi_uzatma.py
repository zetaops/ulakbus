# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import User, Personel
from zengine.lib.test_utils import BaseTestCase
from dateutil.relativedelta import relativedelta
from pyoko.db.connection import log_bucket, version_bucket
import datetime

__author__ = 'Mithat Raşit Özçıkrıkcı'


class TestCase(BaseTestCase):
    def test_gorev_suresi_uzatma(self):
        """
             Test data'daki mithat kullanıcısı ile test işlemi gerçekleştirilir.
             Seçilen personelin görev süresinin açılan formda görev süresi bitiş
             tarihi girilerek görev süresini uzatma mantığına dayanır.
        """
        log_bucket_count = len(log_bucket.get_keys())
        version_bucket_keys = version_bucket.get_keys()

        user = User.objects.get(username="personel_isleri_1")
        personel_id = "V9AJztgnQQc6vbIfNice2ZrHAvF"
        personel = Personel.objects.get(personel_id)
        eski_gorev_suresi_bitis = personel.gorev_suresi_bitis
        yeni_gorev_suresi_bitis = eski_gorev_suresi_bitis + relativedelta(years=1)
        self.prepare_client("/gorev_suresi_uzatma", user=user)

        # Görev süresi uzatılacak personel seçilir.
        self.client.post(
            id=personel_id,
            model="Personel",
            param="personel_id",
            wf="gorev_suresi_uzatma"
        )

        # Görev süresi uzatma formu doldurulur.
        self.client.post(
            cmd="kaydet",
            wf="gorev_suresi_uzatma",
            form=dict(gorev_suresi_bitis=yeni_gorev_suresi_bitis.strftime("%d.%m.%Y"),
                      personel_id=personel.key)
        )

        # save() işlemi meta paremetresi olmadan çalıştırıldığı için aktivite kaydının tutulmaması
        # ve aynı kalması beklenir.
        assert len(log_bucket.get_keys()) == log_bucket_count
        # Yeni versiyon keyleri getirilir.
        versiyon_keyleri = list(set(version_bucket.get_keys()) - set(version_bucket_keys))
        # Personel kaydı ile ilgili versiyon kaydı bulunur.
        key = ''
        for key in versiyon_keyleri:
            if version_bucket.get(key).data['model'] == 'personel':
                break
        yeni_versiyon_key = key

        # Versiyon kaydındaki görev_suresi_bitis field'ınin belirlenen tarihle ayni olmasi kontrol edilir.
        assert version_bucket.get(yeni_versiyon_key).data['data']['gorev_suresi_bitis'] == \
               yeni_gorev_suresi_bitis.strftime("%Y-%m-%dT%H:%M:%SZ")
        # Versiyon kaydındaki görev_suresi_baslama field'ınin bugünün tarihiyle ayni olması kontrol edilir.
        assert version_bucket.get(yeni_versiyon_key).data['data']['gorev_suresi_baslama'] == \
               datetime.date.today().strftime("%Y-%m-%dT%H:%M:%SZ")

        # Personelin görev süresi bitiş tarihinin belirlediğimiz
        # şekilde değişip değişmediği kontrol ediliyor.
        personel = Personel.objects.get(personel.key)
        assert personel.gorev_suresi_bitis == yeni_gorev_suresi_bitis

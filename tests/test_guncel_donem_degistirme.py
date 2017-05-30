# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import User, Donem
from zengine.lib.test_utils import BaseTestCase
from pyoko.db.connection import log_bucket, version_bucket


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_guncel_donem_degistirme(self):
        """
        Güncel Dönem Değiştirme iş akışında güncel dönem seçilir,
        kaydedilir, bilgi verilir.
        Seçilen dönemin güncel dönem olarak kaydedilip kaydedilmediği test edilir.
        Sunucudan dönen cevapta msgboz olup olmadığı test edilir.

        Testte üretilen dataların diğer testleri kırmaması için değişiklikler geri alınır.

        """
        log_bucket_count = len(log_bucket.get_keys())
        log_bucket_keys = log_bucket.get_keys()
        version_bucket_keys = version_bucket.get_keys()

        # ögrenci_isleri_1 kullanıcısı seçilir.
        user = User.objects.get(username='ogrenci_isleri_1')

        # guncel_donem_degistirme iş akışı başlatılır.
        self.prepare_client('/guncel_donem_degistirme', user=user)
        self.client.post()

        ilk_guncel_donem = Donem.guncel_donem()

        # Seçilen dönem
        secilen_guncel_donem_key = 'SBx09BKCv86hp53HGVT2i7vBxGN'

        # Yeni dönem seçilir ve kaydedilir.
        resp = self.client.post(form={'guncel_donem': secilen_guncel_donem_key, 'kaydet': 1})
        time.sleep(1)

        # Save işlemi meta_data parametresi ile yapıldığından aktivite kaydının tutulması ve
        # bir artması beklenir.
        assert len(log_bucket.get_keys()) == log_bucket_count + 1
        # Yeni log kaydının keyi bulunur.
        yeni_log_key = list(set(log_bucket.get_keys()) - set(log_bucket_keys))[0]
        # WF isminin doğruluğu kontrol edilir.
        assert log_bucket.get(yeni_log_key).data['wf_name'] == 'guncel_donem_degistirme'
        # Her bir save işleminde version logları tutulduğundan yeni kayıtlar birikir.
        yeni_versiyon_kayitlari = list(set(version_bucket.get_keys()) - set(version_bucket_keys))
        # Bu kayıtlardan donemle ilgili olanları süzülür.
        donem_kayitlari = list(filter(lambda x: version_bucket.get(x).data['model'] == 'donem',
                                      yeni_versiyon_kayitlari))
        # Oluşturma zamanına göre sıralanır.
        sirali_donem_kayitlari = sorted(donem_kayitlari,
                                        key=lambda x: version_bucket.get(x).data['timestamp'])
        # Son kaydın güncel field'ının True olduğu kontrol edilir.
        assert version_bucket.get(sirali_donem_kayitlari[-1]).data['data']['guncel'] == True
        # Son kaydın dönem key'inin verilen key olduğu kontrol edilir.
        assert version_bucket.get(sirali_donem_kayitlari[-1]).data[
                   'key'] == 'SBx09BKCv86hp53HGVT2i7vBxGN'
        # Bir önceki dönem kaydının guncel field'ının False olduğu kontrol edilir.
        # Bunun anlamı yeni güncel dönem kaydedilirken, öncelikle güncel olan dönemin güncel fieldı
        # False yapılır ardından yeni istenilen dönem güncel olarak kaydedilir.
        assert version_bucket.get(sirali_donem_kayitlari[-2]).data['data']['guncel'] == False
        # Yeni log kaydının indexleri getirilir.
        indexes = log_bucket.get(yeni_log_key).indexes
        # Belirtilen indexlerin doğru tutulduğu kontrol edilir.
        assert ('user_id_bin', self.client.current.user_id) in indexes
        assert ('wf_name_bin', self.client.current.workflow_name) in indexes
        assert yeni_log_key in log_bucket.get_index('user_id_bin',
                                                    self.client.current.user_id).results
        assert yeni_log_key in log_bucket.get_index('wf_name_bin',
                                                    self.client.current.workflow_name).results

        # Güncel dönem olarak kaydedilip kaydedilmediği test edilir.
        assert Donem.guncel_donem().key == secilen_guncel_donem_key

        assert 'msgbox' in resp.json

        yeni_guncel_donem = Donem.guncel_donem()
        ilk_guncel_donem.guncel = True
        ilk_guncel_donem.blocking_save()
        yeni_guncel_donem.ogretim_yili.blocking_delete()
        yeni_guncel_donem.reload()
        assert yeni_guncel_donem.guncel == False
        assert ilk_guncel_donem.guncel == True
        assert Donem.guncel_donem().key == ilk_guncel_donem.key

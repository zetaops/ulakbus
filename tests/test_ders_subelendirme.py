# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import time

from ulakbus.models import Program, Ders, Sube
from zengine.lib.test_utils import *


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ders_subelendirme(self):
        """
        Ders şubelendirme iş akışının ilk adımında program seçilir.
        Veritabanına kayıtlı olan program sayısı ile iş akışı başlatıldıktan sonra
        sunucudan dönen cevaptaki program sayısı karşılaştılıp test edilir.

        İş akışının ikinci adımında seçilen program kayıtlı şubelenecek ders seçilir.
        Sunucudan dönen ders keylerinin veritabanında kayıtlı olup olmadığı ve
        sunucudan dönen ders sayısı ile veritabanından dönen ders sayısı karşılaştılır.

        İş akışının üçüncü adımında ise dönem okutman formu doldurulur,seçilen derse
        ait yeni bir şube oluşturulur.
        Subelendirme yapıldıktan sonra değişikliğin kaydedilip kaydedilmediği test edilir.

        Ders seçim ekranına geri döner, şubelenecek ders seçilir, dönem okutman
        formu doldurulup yeni şube yaratılıp kaydedilir.

        İş akışının son adımında hocalara bilgilendirme mesajı yollanır.

        """

        # Bölüm başkanı kullanıcısı seçilir.
        usr = User.objects.get('YcheZ4qYfgr2tOvEBxxekR2pb7c')

        # WF başlatılır ve kullanıcıya login yaptılır.
        self.prepare_client('/ders_hoca_sube_atama', user=usr)
        resp = self.client.post()

        # Veritabanından kayıtlı olan programların sayısını tutar.
        count_of_program = Program.objects.count()

        assert count_of_program == len(resp.json['forms']['form'][2]['titleMap'])

        # Program seçer.
        resp = self.client.post(cmd='ders_sec',
                                form=dict(program='HUqZl1XUBlFcI3G1iAegLtmlL65', sec=1))

        # Sunucudan dönen ders key'inin veritabanında kayıtlı olup olmadığı ve sayılarının
        # eşit olup olmadığı test edilir.
        for i in range(1, len(resp.json['objects'])):
            key = resp.json['objects'][i]['key']
            assert Ders.objects.get(key).exist

        # Dersin kayıtlı olduğu sube sayısı.
        subeler = list(Sube.objects.filter(ders_id="XERlRTgNiNwwm3P00sMoLv48hLh"))

        # Şubelenilecek ders seçilir.
        self.client.post(cmd='ders_okutman_formu',
                         sube='XERlRTgNiNwwm3P00sMoLv48hLh')

        # Şubelendirme formu doldurulur.
        sube = [{'okutman': "8cH3gnnnygN4ghl7JCe8kpbzjle", 'kontenjan': 34, 'dis_kontenjan': 45, 'ad': "Sube 1"}]

        # Formu kaydedip ders seçim ekranına döner.
        self.client.post(cmd='subelendirme_kaydet',
                         flow='ders_okutman_formu',
                         form=dict(program_sec='null', kaydet_ders=1, bilgi_ver='null', Subeler=sube))

        # Dersin kayıtlı olduğu sube sayısı.
        _derse_ait_subeler = list(Sube.objects.filter(ders_id="XERlRTgNiNwwm3P00sMoLv48hLh"))

        # Subelendirme yapıldıktan sonra değişikliğin kaydedilip kaydedilmediği test edilir.
        assert len(subeler) + 1 == len(_derse_ait_subeler)

        yeni_sube_1_key = list(set([d.key for d in _derse_ait_subeler]) - set([d.key for d in subeler]))[0]
        yeni_sube_1 = Sube.objects.get(yeni_sube_1_key)
        yeni_sube_1.blocking_delete()

        assert len(Sube.objects.filter(ders_id="XERlRTgNiNwwm3P00sMoLv48hLh")) == len(subeler)

        # Şubelendirme formu doldurulur.
        sube = [{'okutman': "6Hb5xCkqfbRnysVyTW15qB4rWL8", 'kontenjan': 30, 'dis_kontenjan': 5, 'ad': "Sube 2"}]

        # Şubelenilecek ders seçilir.
        resp = self.client.post(cmd='ders_okutman_formu',
                                sube='XERlRTgNiNwwm3P00sMoLv48hLh')

        # Hocalara bilgilendirme mesajı gönderilir.
        # İş akışı bu adımdan sonra sona erer.
        resp = self.client.post(cmd='subelendirme_kaydet',
                                flow='bilgi_ver',
                                form=dict(program_sec='null', kaydet_ders='null', bilgi_ver=1, Subeler=sube))

        _derse_ait_subeler_2 = Sube.objects.filter(ders_id="XERlRTgNiNwwm3P00sMoLv48hLh")
        assert len(subeler) + 1 == len(_derse_ait_subeler_2)

        yeni_sube_2_key = list(set([d.key for d in _derse_ait_subeler_2]) - set([d.key for d in subeler]))[0]
        yeni_sube_2 = Sube.objects.get(yeni_sube_2_key)
        yeni_sube_2.blocking_delete()
        assert len(Sube.objects.filter(ders_id="XERlRTgNiNwwm3P00sMoLv48hLh")) == len(subeler)






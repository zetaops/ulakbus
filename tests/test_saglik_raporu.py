# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.lib.test_utils import BaseTestCase
from ulakbus.models import SaglikRaporu, Personel
import time


class TestCase(BaseTestCase):

    def test_saglik_raporu_olustur(self):
        for i in range(2):
            if i == 0:
                personel_id = "OI3vq7rWIaTdSNUj4KwSBpeHMrc"     # ismet tarhan
                rapor_form = {
                    'baslama_tarihi': "17.01.2017",
                    'bitis_tarihi': "18.01.2017",
                    'gecirecegi_adres': "Urla",
                    'kaydet': 1,
                    'nerden_alindigi': "Hastane",
                    'onay_tarihi': "17.01.2017",
                    'rapor_cesidi': 1,
                    'raporun_alindigi_il': 35,
                    'sure': 2,
                    'telefon': "02321234567"
                }    # Tek Hekim raporu
            else:
                personel_id = "RngBQlVfKwyFHcqcmXRvlxipK6x"  # cevale akça
                rapor_form = {
                    'baslama_tarihi': "30.01.2017",
                    'bitis_tarihi': "28.02.2017",
                    'gecirecegi_adres': "Urla",
                    'kaydet': 1,
                    'nerden_alindigi': "Hastane",
                    'onay_tarihi': "17.01.2017",
                    'rapor_cesidi': 3,
                    'raporun_alindigi_il': 35,
                    'sure': 30,
                    'telefon': "02321234567"
                }    # Dogum öncesi tek hekim raporu

            personel = Personel.objects.get(personel_id)

            self.prepare_client('/saglik_raporu_olusturma', username='personel_isleri_1')
            self.client.post(id=personel_id,
                             model="SaglikRaporu",
                             param="personel_id",
                             wf="saglik_raporu_olusturma")

            raporlar = SaglikRaporu.objects.filter(personel=personel)

            kayit_oncesi_rapor_sayisi = raporlar.count()

            # saglik raporu ekleme formu cagirilir

            if i == 0:
                sure = 2
                tek_hekim_saglik_raporlari = raporlar.filter(rapor_cesidi='Tek Hekim Raporu')
                tek_hekim_toplam_gun_sayisi = reduce(
                    lambda x, y: x + y,
                    [rapor.sure for rapor in tek_hekim_saglik_raporlari], 0)

                self.client.post(form={"add": 1}, cmd='add_edit_form')
                resp = self.client.post(form=rapor_form)

                if tek_hekim_toplam_gun_sayisi + 2 > 40:
                    assert resp.json['msgbox']['title'] == u'Hatalı Veri Girişi'
                    assert resp.json['msgbox']['msg'] == \
                        u'Tek Hekim Raporu için yıl içerisinde ' \
                        u'40 günden fazla rapor alamazsınız!'
                    kayit = False
                else:
                    assert resp.json['forms']['form'][0]['helpvalue'] == \
                        u'İsmet Tarhan adlı personelin ' \
                        u'Tek Hekim Raporu başarılı bir şekilde kaydedildi.'
                    kayit = True
            else:
                sure = 30
                tek_hekim_dogum_oncesi = raporlar.filter(
                    rapor_cesidi='Tek Hekim Raporu Dogum Oncesi'
                )
                tek_hekim_dogum_oncesi_rapor_sayisi = tek_hekim_dogum_oncesi.count()

                self.client.post(form={"add": 1}, cmd='add_edit_form')
                resp = self.client.post(form=rapor_form)

                assert resp.json['forms']['form'][0]['helpvalue'] == \
                    u'Cevale Akça adlı personelin Tek Hekim Raporu Doğum Öncesi ' \
                    u'başarılı bir şekilde kaydedildi.'
                kayit = True
            time.sleep(1)
            resp = self.client.post(form={'raporlar': 1})
            if kayit:
                assert len(resp.json['objects']) - 1 == kayit_oncesi_rapor_sayisi + 1

                rapor_object = SaglikRaporu.objects.filter(personel=personel,
                                                           sure=sure,
                                                           telefon="02321234567")[0]
                self.client.post(id=personel_id,
                                 model="SaglikRaporu",
                                 param="personel_id",
                                 object_id=rapor_object.key,
                                 wf="saglik_raporu_olusturma",
                                 cmd="add_edit_form")

                rapor_form['nerden_alindigi'] = "Sağlık Ocağı"
                rapor_form['object_key'] = rapor_object.key

                resp = self.client.post(form=rapor_form)
                if i == 0:
                    assert resp.json['forms']['form'][0]['helpvalue'] == \
                        u'İsmet Tarhan adlı personelin ' \
                        u'Tek Hekim Raporu başarılı bir şekilde kaydedildi.'
                else:
                    pass
                self.client.post(form={'raporlar': 1})

                resp = self.client.post(id=personel_id,
                                        model="SaglikRaporu",
                                        param="personel_id",
                                        object_id=rapor_object.key,
                                        wf="saglik_raporu_olusturma",
                                        cmd="sil")

                assert resp.json['forms']['schema']['title'] == u'Sağlık Raporu Silme İşlemi'

                time.sleep(1)

                resp = self.client.post(form={'evet': 1}, cmd='delete')

                assert len(resp.json['objects']) - 1 == kayit_oncesi_rapor_sayisi

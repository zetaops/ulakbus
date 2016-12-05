# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import User, Ogrenci, OgrenciProgram
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_ogrenci_onkayit(self):
        """
        Ilk asamada ogrenci_1 kullanicisina giris yaptirilir.
        Onceki egitim bilgileri ekrana gelir ve mezuniyet yili kontrolu yapilir.

        Ikinci asamada ilgili ogrencinin onceki egitim bilgileri kaydedilir. Kaydin dogru yapilip
        yapilmadigi kontrol edilir.

        Ucuncu asamada ogrencinin yerlestirme bilgileri girilip kaydedilir. Donen response a gore ilgili ogrencinin
        kan grubu kontrol edilir.

        Son asamada ise ogrenciye ait on kayit formu doldurulup kaydedilir. Kaydin basarili olup olmadigini ekrana
        gelen mesajdan kontrol edilirm
        """

        # Kullanıcıya login yaptırılır.
        usr = User.objects.get(username='ogrenci_1')
        self.prepare_client('/ogrenci_on_kayit', user=usr)

        resp = self.client.post(wf='ogrenci_on_kayit')

        assert resp.json['forms']['model']['mezuniyet_yili'] == '2015'

        resp = self.client.post(cmd='kaydet', form={'diploma_notu': 2,
                                             'kaydet': 1,
                                             'mezuniyet_yili': '2015',
                                             'model_type': "OncekiEgitimBilgisi",
                                             # 'object_key': "C0Et9YQFzCs7yKEbEJcRSHog8Ro",
                                             'okul_adi': "EGE UNIVERSITESI",
                                             'unicode': "EGE UNIVERSITESI 2015 Hürmet"})

        assert resp.json['forms']['model']['unicode'] == "Hürmet Sezer - BİYOKİMYA ANABİLİM DALI / 2014"

        resp = self.client.post(cmd='kaydet', form={'giris_puan_turu': 1,
                                                    'giris_puani': 1,
                                                    'ileri_buton': 1,
                                                    'model_type': "OgrenciProgram",
                                                    'unicode': "Hürmet Sezer - BİYOKİMYA ANABİLİM DALI / 2014"})

        assert resp.json['forms']['model']['kan_grubu'] == "0 RH-"

        resp = self.client.post(cmd='kaydet', form={'aile_adresi': 'bornova - izmir',
                                                    'aile_gsm': "0444 234 23 12",
                                                    'aile_tel': "234 234 23 23",
                                                    'anne_aylik_kazanc': 2,
                                                    'anne_meslek': 'Ev',
                                                    'anne_ogrenim_durumu': 1,
                                                    'baba_aylik_kazanc': 2,
                                                    'baba_meslek': 'Memur',
                                                    'baba_ogrenim_durumu': 1,
                                                    'burs_kredi_no': 'KYK-100',
                                                    'emeklilik_durumu': 'Emekli',
                                                    'erkek_kardes_sayisi': 1,
                                                    'kan_grubu': '0 RH-',
                                                    'kaydet_buton': 1,
                                                    'kiz_kardes_sayisi': 1,
                                                    'masraf_sponsor': 3,
                                                    'model_type': "Ogrenci",
                                                    'ogrenim_goren_kardes_sayisi': 1,
                                                    'ozur_durumu': 1,
                                                    'ozur_orani': 0,
                                                    'unicode': 'Hürmet Sezer'})

        assert resp.json['msgbox']['title'] == 'Başarılı'

    def test_ogrenci_isleri_on_kayit_onay(self):
        """
            Ilk asamada ogrenci_isleri_1 adli memur girisi yapilir.

            Bu test'de 'Ik8SEGcDdJnHUvA7MKHpBBlwrJr' keyine sahip ogrenciye gidilir. Ilgili ogrencinin on kaydi
            yapilmis mi yapmilmamis mi kontrol edilir. Eger yapilmamissa ilgili memur belge konrolleri yapar.

            Belge kontrolu asamasinda, memurun belgeye yaptigi aciklama kontrol edilir.

            Son asamada ise, Memurun belge kontrolu bittiginde on kayit islemi onaylar. Onay konrolu ekrana gelen mesaj
            bolumunden kontrol edilir ve ogrencinin ogrencilik statusu 2 yapilir.

            Memur tekrar 'Ik8SEGcDdJnHUvA7MKHpBBlwrJr' keyine sahip ogrencinin on kaydina bakmak istediginde, ilgili
            ogrencinin ogrencilik statusu 2 oldugundan 'Bu Kayit Zaten Var!' mesaj ekraniyla karsilasir.

        """
        for i in range(2):
            usr = User.objects.get(username='ogrenci_isleri_1')
            ogrenci = Ogrenci.objects.get('Ik8SEGcDdJnHUvA7MKHpBBlwrJr')
            ogrenci_program = OgrenciProgram.objects.get(ogrenci=ogrenci)

            self.prepare_client('/ogrenci_isleri_onkayit_onay', user=usr)

            resp = self.client.post(wf='ogrenci_isleri_onkayit_onay', id="Ik8SEGcDdJnHUvA7MKHpBBlwrJr",
                                    model="OgrenciProgram", param="ogrenci_id")
            if resp.json['reload_cmd'] == 'kayitli':
                assert resp.json['msgbox']['title'] == "Bu Kayıt Zaten Var!"
            else:
                assert resp.json['forms']['model']['unicode'] == "Hürmet Sezer - BİYOKİMYA ANABİLİM DALI / 2014"

                resp = self.client.post(cmd='save', form={'Belgeler': [{'tip': 3, 'aciklama': 'Kontrol Edildi', 'tamam': True}],
                                                          'kaydet': 1,
                                                          'model_type': "OgrenciProgram",
                                                          'unicode': "Hürmet Sezer - BİYOKİMYA ANABİLİM DALI / 2014"})

                assert resp.json['forms']['model']['Belgeler'][0]['aciklama'] == 'Kontrol Edildi'

                resp = self.client.post(cmd='onayla', form={'Belgeler': [{'tip': 3,
                                                                          'aciklama': 'Kontrol Edildi',
                                                                          'tamam': True}],
                                                            'onayla': 1,
                                                            'model_type': "OgrenciProgram",
                                                            'unicode': "Hürmet Sezer - BİYOKİMYA ANABİLİM DALI / 2014"})

                ogrenci_program.ogrencilik_statusu = 2
                assert resp.json['msgbox']['title'] == "Ön Kayıt İşlemi Gerçekleştirildi!"

            ogrenci_program.ogrencilik_statusu = 1
            ogrenci_program.save()


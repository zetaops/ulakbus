# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import OgrenciProgram, Ogrenci, Role
from ulakbus.lib.ogrenci import kaydi_silinmis_abs_role
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):
    """
    Bu sınıf ``BaseTestCase`` extend edilerek hazırlanmıştır.

    """

    def test_kayit_silme(self):
        """
        Kayıt silme iş akışı başlatılmadan önce kaydı silinecek öğrenci seçilir.

        İş akışının ikinci adımında personelin iş akışına devam etmek isteyip
        istemediği sorulur.
        Eğer personel vazgeçerse;
        Dönen cevapta işlemin iptal olduğuna dair mesajın olup olmadığı test edilir.

        Aynı öğrenci seçilerek iş akışı tekrardan başlatılır.

        İş akışının ikinci adımında personelin iş akışına devam etmek isteyip
        istemediği sorulur.

        Personelin işleme devam etmesi durumunda;

        Sunucudan dönen ayrılma nedenleri sayısı ile veritabanından dönen ayrılma
        nedenlerinin sayısının eşitliği karşılaştırılıp test edilir.

        Ayrılma nedeni seçilir ve açıklama yazılır.

        Öğrencinin kayıtlı olduğu öğrenci programının ayrılma nedeni ve
        ogrencilik statüsü alanlarına atanan değerlerin doğruluğu test edilir.

        Rolü değiştirilen öğrencinin, değişikliğe sahip olup olmadığı test
        edilir.

        İşlemin başarılı olduğuna dair bilgi mesajı ekrana basılırç
        Dönen cevapta msgbox olup olmadığı test edilir.

        Aynı öğrenci seçilerek iş akışı tekrardan başlatılır.

        Dönen cevapta kaydın daha önceden silindiğine dair mesajın olup olmadığı test edilir.

        """

        # Öğrenci İşleri personeline login yaptırılır.
        self.prepare_client('/kayit_sil', username='ogrenci_isleri_1')
        self.client.post(id="RnKyAoVDT9Hc89KEZecz0kSRXRF",
                         param="ogrenci_id",
                         filters={'ogrenci_id': {'values': ["RnKyAoVDT9Hc89KEZecz0kSRXRF"],
                                                 'type': "check"}})

        # Kayıt silme işleminden vazgeçilir.
        resp = self.client.post(form={'vazgecme': 1, 'kaydet': 'null'},
                                flow='kayit_silme_isleminden_vazgec')

        # Bilgi mesajı verilip verilmediğini test eder.
        assert resp.json['msgbox']['msg'] == "Kayıt silme işlemi iptal edilmiştir."

        # İş akışı tekrar başlatılır.
        self.client.set_path('/kayit_sil')
        self.client.post(id="RnKyAoVDT9Hc89KEZecz0kSRXRF",
                         param="ogrenci_id",
                         filters={'ogrenci_id': {'values': ["RnKyAoVDT9Hc89KEZecz0kSRXRF"],
                                                 'type': "check"}})

        # Bahtinur Zengin adlı öğrenci veritabanından çekilir.
        ogrenci = Ogrenci.objects.get('RnKyAoVDT9Hc89KEZecz0kSRXRF')

        user = ogrenci.user

        _roles = {role.key: role.abstract_role for role in Role.objects.filter(user=user)}

        # Kayıt silme işleminden onaylanır.
        self.client.post(form={'vazgecme': 'null', 'kaydet': 1}, flow='fakulte_yonetim_karari')

        # Fakülte kara no girilir.
        resp = self.client.post(form={'karar': "455", 'kaydet': 1})

        # Ayrılma nedenlerini tutan list.
        lst = OgrenciProgram().get_choices_for('ayrilma_nedeni')

        # Sunucudan dönen ayrılma nedenleri sayısı ile
        # veritabanından dönen ayrılma nedenlerinin sayısının
        # eşitliği karşılaştırılır.
        assert len(resp.json['forms']['form'][1]['titleMap']) == len(lst)

        # Kaydı silinecek öğrencinin ayrılma nedeni seçilir ve açıklama yazılır.
        resp = self.client.post(form=dict(ayrilma_nedeni=11, sec=1, aciklama='Yatay Geçiş'))

        # Öğrencinin kayıtlı olduğu program
        ogrenci_program = OgrenciProgram.objects.filter(ogrenci=ogrenci)

        # İş akışı tekrardan başlatılır.
        self.client.set_path('/kayit_sil')
        resp = self.client.post(id="RnKyAoVDT9Hc89KEZecz0kSRXRF",
                                param="ogrenci_id",
                                filters={'ogrenci_id': {'values': ["RnKyAoVDT9Hc89KEZecz0kSRXRF"],
                                                        'type': "check"}})

        assert resp.json['msgbox'][
                   'msg'] == " Bahtinur Zengin adlı öğrencinin kaydı daha önceden silinmiştir."

        for program in ogrenci_program:
            # Ayrılma nedenine atanan değerin doğruluğu test eder.
            assert program.ayrilma_nedeni == 11
            # Öğrencilik statüsüne atanan değerin doğruluğunu test eder.
            assert program.ogrencilik_statusu == 21

            program.ayrilma_nedeni = 0
            program.ogrencilik_statusu = 0
            program.save()

        # Rolün değişip değişmediğini test eder
        for key in _roles:
            role = Role.objects.get(key)
            assert role.abstract_role == kaydi_silinmis_abs_role(role)
            role.abstract_role = _roles[key]
            role.save()





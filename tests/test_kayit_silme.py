# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.models import OgrenciProgram, Ogrenci, Role
from ulakbus.lib.ogrenci import kaydi_silinmis_abs_role
from zengine.lib.test_utils import BaseTestCase
from pyoko.db.connection import version_bucket, log_bucket

from ulakbus.views.ogrenci.kayit_silme import ABSTRACT_ROLE_LIST, ABSTRACT_ROLE_LIST_SILINMIS


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
        log_bucket_count = len(log_bucket.get_keys())
        log_bucket_keys = log_bucket.get_keys()

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

        # Öğrencinin kayıtlı olduğu programlar
        ogrenci_program = OgrenciProgram.objects.filter(ogrenci=ogrenci)

        # Her bir program için değiştirilecek rol sayısı bulunur.
        role_count = 0
        for program in ogrenci_program:
            roles = Role.objects.filter(user=user, unit=program.program.birim)
            for role in roles:
                if role.abstract_role.key in ABSTRACT_ROLE_LIST:
                    role_count += 1

        # Öğrenci programı ve rol değişiklikleri toplamı bulunur.
        yeni_kayit_sayisi = len(ogrenci_program) + role_count

        _roles = {role.key: role.abstract_role for role in Role.objects.filter(user=user)}

        # Kayıt silme işleminden onaylanır.
        self.client.post(form={'vazgecme': 'null', 'kaydet': 1}, flow='fakulte_yonetim_karari')

        # Fakülte karar no girilir.
        resp = self.client.post(form={'karar': "455", 'kaydet': 1})

        # Ayrılma nedenlerini tutan list.
        lst = OgrenciProgram().get_choices_for('ayrilma_nedeni')

        # Sunucudan dönen ayrılma nedenleri sayısı ile
        # veritabanından dönen ayrılma nedenlerinin sayısının
        # eşitliği karşılaştırılır.
        assert len(resp.json['forms']['form'][1]['titleMap']) == len(lst)

        # Kaydı silinecek öğrencinin ayrılma nedeni seçilir ve açıklama yazılır.
        resp = self.client.post(form=dict(ayrilma_nedeni=11, sec=1, aciklama='Yatay Geçiş'))

        # Save işlemi meta_data parametresi ile yapıldığından aktivite logunun tutulması ve
        # sayısının yeni_kayit_sayisi kada rolması beklenir.
        assert len(log_bucket.get_keys()) == log_bucket_count + yeni_kayit_sayisi
        # Yeni log kayıtlarının keyleri bulunur.
        yeni_log_keyleri = list(set(log_bucket.get_keys()) - set(log_bucket_keys))
        # Bu log kayıtlarının içinde bulunan version_key leri bulunur.
        yeni_versiyon_keyleri = [log_bucket.get(x).data['version_key'] for x in yeni_log_keyleri]
        # Versiyon kayıtlarından 'ogrenci_program' modeline ait olanlar süzülür.
        ogrenci_program_kayitlari = list(
            filter(lambda x: version_bucket.get(x).data['model'] == 'ogrenci_program',
                   yeni_versiyon_keyleri))
        # Versiyon kayıtlarından 'role' modeline ait olanlar süzülür.
        rol_kayitlari = list(
            filter(lambda x: version_bucket.get(x).data['model'] == 'role', yeni_versiyon_keyleri))
        # Aktivite log kayıtlarının '455' fakülte karar numarasıyla yapıldığı kontrol edilir.
        # WF isminin 'kayit_sil' olduğu kontrol edilir.
        for kayit in yeni_log_keyleri:
            assert log_bucket.get(kayit).data['reason'] == 'FAKÜLTE_KARAR_NO_455'
            assert log_bucket.get(kayit).data['wf_name'] == 'kayit_sil'
        # Öğrenci program sayısı kadar ogrenci_program versiyon kaydı tutulduğu kontrol edilir.
        assert len(ogrenci_program_kayitlari) == len(ogrenci_program)
        # Program versiyon kayıtlarının ayrılma nedeni, ogrencilik statusu fieldlarının belirtildiği
        # gibi olduğu kontrol edilir.
        for kayit in ogrenci_program_kayitlari:
            assert version_bucket.get(kayit).data['data']['ayrilma_nedeni'] == 11
            assert version_bucket.get(kayit).data['data']['ogrencilik_statusu'] == 21
            assert version_bucket.get(kayit).data['model'] == 'ogrenci_program'
        # Değişiklik yapılan rol sayısı kadar role versiyon kaydı tutulduğu kontrol edilir.
        assert len(rol_kayitlari) == role_count
        # Role versiyon kayıtlarının abstract_role_id bölümlerinin silinmiş olarak işaretlendiği kontrol edilir.
        # Role versiyon kayıtlarının model bölümünün 'role' oldğu kontrol edilir.
        for kayit in rol_kayitlari:
            assert version_bucket.get(kayit).data['model'] == 'role'
            assert version_bucket.get(kayit).data['data'][
                       'abstract_role_id'] in ABSTRACT_ROLE_LIST_SILINMIS
        # Yeni log kaydının indexleri getirilir.
        indexes = log_bucket.get(yeni_log_keyleri[0]).indexes
        # Belirtilen indexlerin doğru tutulduğu kontrol edilir.
        assert ('wf_name_bin', self.client.current.workflow_name) in indexes
        # wf_name indexi ile log kaydının getirildiği kontrol edilir.
        assert yeni_log_keyleri[0] in log_bucket.get_index('wf_name_bin',
                                                           self.client.current.workflow_name).results

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

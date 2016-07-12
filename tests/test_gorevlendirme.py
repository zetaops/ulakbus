# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from ulakbus.models import User, Personel, Unit, KurumIciGorevlendirmeBilgileri, KurumDisiGorevlendirmeBilgileri
from ulakbus.models import AbstractRole, HizmetKayitlari
from zengine.lib.test_utils import BaseTestCase
from dateutil.relativedelta import relativedelta
import datetime

class TestCase(BaseTestCase):
    """
        Personel görevlendirme işlemine görevlendirme türü seçilerek başlanır.
        Görevlendirme Türleri:
        1- Kurum içi görevlendirme
        2- Kurum dışı görevlendirme
        Seçilen görevlendirme türüne göre görüntülenen formda gereken bilgiler girilir ve kaydedilir.
    """
    def test_kurum_ici_gorevlendirme_standart(self):
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user = user)
        personel_id = "ShW15GBQCCUAuk64ZrK9myA470y"

        # Görevlendirilecek birim
        birim_id = "PNrGNyS35dmw9WHKPyl9Er0CiWN"
        birim = Unit.objects.get(birim_id)

        # Görevlendirilecek personel veritabanından çekilir.
        personel = Personel.objects.get(personel_id)

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id,model="Personel", param="personel_id", wf="gorevlendirme")

        # Veritabanındaki görevlendirme bilgileri test sonunda kontrol edebilmek amacıyla silinir.
        KurumIciGorevlendirmeBilgileri.objects.delete()

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme", form=dict(gorevlendirme_tur=2))

        # Görevlendirmesi yapılacak soyut rol
        soyut_rol_id = "AGTuBwCYUzDF5axgV3h7oDSCwyl"
        soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(gorev_tipi=2,
            kurum_ici_gorev_baslama_tarihi = baslangic, kurum_ici_gorev_bitis_tarihi = bitis,
            birim = birim, soyut_rol_id = soyut_rol_id, aciklama = "Test Öğrenci İşleri Daire Başkanlığı Görevlendirme",
            resmi_yazi_sayi = "123123", resmi_yazi_tarih = resmi_yazi_tarih.strftime("%d.%m.%Y")))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        gorevlendirme = KurumIciGorevlendirmeBilgileri()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.kurum_ici_gorev_baslama_tarihi == baslangic

        assert gorevlendirme.kurum_ici_gorev_bitis_tarihi == bitis

        assert gorevlendirme.birim.key == birim_id

    def test_kurum_ici_gorevlendirme_dekan(self):
        """
            Bir personelin kurum içerisinde herhangi bir fakülteye dekan olarak
            görevlendirilmesi durumunu içeren test metodudur.
            Standart görevlendirmeden farkı, görevlendirmenin hizmet cetvelini etkiliyor olmasıdır.
        """

        # Dekan Soyut Rol
        soyut_rol_id = "YmEn6XK0L3OHDObgWi5RjZmkk0O"
        soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        # Görevlendirme yapılacak personel
        personel_id = "OFrnc32AYZou8KcZjKFZGD7gOj3"
        personel = Personel.objects.get(personel_id)

        # Görevlendirilecek birim
        birim_id = "ZDfRAEBXkRwVd5g8FpTYNsfhqgR"
        birim = Unit.objects.get(birim_id)

        # Veritabanındaki hizmet kayıtları test sonunda kontrol edebilmek amacıyla silinir.
        HizmetKayitlari.objects.delete()

        # Veritabanındaki görevlendirme bilgileri test sonunda kontrol edebilmek amacıyla silinir.
        KurumIciGorevlendirmeBilgileri.objects.delete()

        #Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user = user)

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id,model="Personel", param="personel_id", wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme", form=dict(gorevlendirme_tur=2))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            gorev_tipi=2,
            kurum_ici_gorev_baslama_tarihi = baslangic,
            kurum_ici_gorev_bitis_tarihi = bitis,
            birim = birim,
            soyut_rol = soyut_rol,
            aciklama = "Dekan olarak görevlendirme",
            resmi_yazi_sayi = "123123",
            resmi_yazi_tarih = resmi_yazi_tarih
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        gorevlendirme = KurumIciGorevlendirmeBilgileri()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.kurum_ici_gorev_baslama_tarihi == baslangic

        assert gorevlendirme.kurum_ici_gorev_bitis_tarihi == bitis

        assert gorevlendirme.birim.key == birim_id

        # Hizmet cetveli kontrolü
        assert HizmetKayitlari.objects.filter().count() > 0

    def kurum_disi_gorevlendirme_standart(self):
        """
            Herhangi bir personelin kurum dışı görevlendirilmesi durumudur.
        """

        #Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user = user)

        # Görevlendirmesi yapılacak soyut rol
        soyut_rol_id = "AGTuBwCYUzDF5axgV3h7oDSCwyl"
        soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        # Görevlendirmesi yapılacak personel
        personel_id = "YpMvzcYw3msFu79V7BfSzvNjAng"
        personel = Personel.objects.get(personel_id)

        # Kurum dışı görevlendirme bilgilerinin test sonunda kontrol edilebilmesi için önceki kayıtlar siliniyor
        KurumDisiGorevlendirmeBilgileri.objects.delete()

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id,model="Personel", param="personel_id", wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme", form=dict(gorevlendirme_tur=1))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            kurum_disi_gorev_baslama_tarihi = baslangic,
            kurum_disi_gorev_bitis_tarihi = bitis,
            aciklama = "Standart kurum dışı görevlendirme",
            resmi_yazi_sayi = "234234",
            resmi_yazi_tarih = resmi_yazi_tarih,
            maas = False,
            yevmiye = False,
            yolluk = True,
            ulke= 90,
            soyut_rol = soyut_rol,
            personel = personel
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        assert KurumDisiGorevlendirmeBilgileri.objects.filter().count() > 0
        gorevlendirme = KurumDisiGorevlendirmeBilgileri.objects.filter()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.kurum_ici_gorev_baslama_tarihi == baslangic

        assert gorevlendirme.kurum_ici_gorev_bitis_tarihi == bitis

    def test_kurum_disi_gorevlendirme_rektor(self):
        """
            Bir personelin kurum dışına rektör olarak görevlendirilmesi durumudur.
        """

        #Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user = user)

        # Rektör Soyut Rol
        soyut_rol_id = "5xanqtlXnY9dsQhWNV8gMK1rXcm"
        soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        #Görevlendirilecek personel
        personel_id = "XFLlsTdqyOV07kgQCbJiIGIvC0v"
        personel = Personel.objects.get(personel_id)

        # Kurum dışı görevlendirme bilgilerinin test sonunda kontrol edilebilmesi için önceki kayıtlar siliniyor
        KurumDisiGorevlendirmeBilgileri.objects.delete()

        # Veritabanındaki hizmet kayıtları test sonunda kontrol edebilmek amacıyla silinir.
        HizmetKayitlari.objects.delete()

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id,model="Personel", param="personel_id", wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme", form=dict(gorevlendirme_tur=1))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            kurum_disi_gorev_baslama_tarihi = baslangic,
            kurum_disi_gorev_bitis_tarihi = bitis,
            aciklama = "Rektör kurum dışı görevlendirme",
            resmi_yazi_sayi = "234234",
            resmi_yazi_tarih = resmi_yazi_tarih,
            maas = False,
            yevmiye = False,
            yolluk = True,
            ulke= 90,
            soyut_rol = soyut_rol,
            personel = personel
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        assert KurumDisiGorevlendirmeBilgileri.objects.filter().count() > 0
        gorevlendirme = KurumDisiGorevlendirmeBilgileri.objects.filter()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.kurum_ici_gorev_baslama_tarihi == baslangic

        assert gorevlendirme.kurum_ici_gorev_bitis_tarihi == bitis

        # Hizmet cetveli kontrolü
        assert HizmetKayitlari.objects.filter().count() > 0

    def test_kurum_disi_gorevlendirme_dekan(self):
        """
            Bir personelin kurum dışına dekan olarak görevlendirilmesi durumudur.
        """

        #Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user = user)

        # Dekan Soyut Rol
        soyut_rol_id = "YmEn6XK0L3OHDObgWi5RjZmkk0O"
        soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        #Görevlendirilecek personel
        personel_id = "XFLlsTdqyOV07kgQCbJiIGIvC0v"
        personel = Personel.objects.get(personel_id)

        # Kurum dışı görevlendirme bilgilerinin test sonunda kontrol edilebilmesi için önceki kayıtlar siliniyor
        KurumDisiGorevlendirmeBilgileri.objects.delete()

        # Veritabanındaki hizmet kayıtları test sonunda kontrol edebilmek amacıyla silinir.
        HizmetKayitlari.objects.delete()

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id,model="Personel", param="personel_id", wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme", form=dict(gorevlendirme_tur=1))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            kurum_disi_gorev_baslama_tarihi = baslangic,
            kurum_disi_gorev_bitis_tarihi = bitis,
            aciklama = "Rektör kurum dışı görevlendirme",
            resmi_yazi_sayi = "234234",
            resmi_yazi_tarih = resmi_yazi_tarih,
            maas = False,
            yevmiye = False,
            yolluk = True,
            ulke= 90,
            soyut_rol = soyut_rol
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        assert KurumDisiGorevlendirmeBilgileri.objects.filter().count() > 0
        gorevlendirme = KurumDisiGorevlendirmeBilgileri.objects.filter()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.kurum_ici_gorev_baslama_tarihi == baslangic

        assert gorevlendirme.kurum_ici_gorev_bitis_tarihi == bitis

        # Hizmet cetveli kontrolü
        assert HizmetKayitlari.objects.filter().count() > 0

    def kurum_disi_gorevlendirme_rektor(self):
        """
         Bir personelin başka bir kuruma rektör olarak görevlendirilmesi durumudur.
        """

        #Görevlendirme işlemini yapacak olan personel işleri dairesi personeli
        user = User.objects.get(username="personel_isleri_1")
        self.prepare_client("/gorevlendirme", user = user)

        # Rektör Soyut Rol
        soyut_rol_id = "5xanqtlXnY9dsQhWNV8gMK1rXcm"
        soyut_rol = AbstractRole.objects.get(soyut_rol_id)

        #Görevlendirilecek personel
        personel_id = "XFLlsTdqyOV07kgQCbJiIGIvC0v"
        personel = Personel.objects.get(personel_id)

        # Kurum dışı görevlendirme bilgilerinin test sonunda kontrol edilebilmesi için önceki kayıtlar siliniyor
        KurumDisiGorevlendirmeBilgileri.objects.delete()

        # Veritabanındaki hizmet kayıtları test sonunda kontrol edebilmek amacıyla silinir.
        HizmetKayitlari.objects.delete()

        # Görevlendirilecek personel seçilir.
        self.client.post(id=personel_id,model="Personel", param="personel_id", wf="gorevlendirme")

        # Görevlendirme türü kaydedilir.
        self.client.post(cmd="gorevlendirme_tur_kaydet", wf="gorevlendirme", form=dict(gorevlendirme_tur=1))

        # Görevlendirme bilgileri girilir ve görevlendirme kaydedilir.
        baslangic = datetime.date.today()
        bitis = baslangic + relativedelta(years=1)
        resmi_yazi_tarih = baslangic + relativedelta(days=-3)
        self.client.post(cmd="kaydet", wf="gorevlendirme", form=dict(
            kurum_disi_gorev_baslama_tarihi = baslangic,
            kurum_disi_gorev_bitis_tarihi = bitis,
            aciklama = "Rektör kurum dışı görevlendirme",
            resmi_yazi_sayi = "234234",
            resmi_yazi_tarih = resmi_yazi_tarih,
            maas = False,
            yevmiye = False,
            yolluk = True,
            ulke= 90,
            soyut_rol = soyut_rol,
            personel = personel
        ))

        # İlgili wf adımında görevlendirme kaydının yapılıp yapılmadığının kontrolü
        assert KurumDisiGorevlendirmeBilgileri.objects.filter().count() > 0
        gorevlendirme = KurumDisiGorevlendirmeBilgileri.objects.filter()[0]
        assert gorevlendirme.personel.key == personel_id

        assert gorevlendirme.kurum_ici_gorev_baslama_tarihi == baslangic

        assert gorevlendirme.kurum_ici_gorev_bitis_tarihi == bitis

        # Hizmet cetveli kontrolü
        assert HizmetKayitlari.objects.filter().count() > 0
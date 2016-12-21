# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

"""Zato Servis URL Paths

Zato servislerine erişmek için kullanacağımız url pathlerden
oluşan sözlük.

"""

service_url_paths = {
    "HitapAcikSureGetir": {"url": "/services/personel/hitap/hizmet-acik-sure-getir"},
    "HitapAcikSureSenkronizeEt": {"url": "/services/personel/hitap/hizmet-acik-sure-sync"},
    "HitapAcikSureEkle": {"url": "/services/personel/hitap/hizmet-acik-sure-ekle"},
    "HitapAcikSureGuncelle": {"url": "/services/personel/hitap/hizmet-acik-sure-guncelle"},
    "HitapAcikSureSil": {"url": "/services/personel/hitap/hizmet-acik-sure-sil"},
    "HitapAskerlikGetir": {"url": "/services/personel/hitap/hizmet-askerlik-getir"},
    "HitapAskerlikSenkronizeEt": {"url": "/services/personel/hitap/hizmet-askerlik-sync"},
    "HitapAskerlikEkle": {"url": "/services/personel/hitap/hizmet-askerlik-ekle"},
    "HitapAskerlikGuncelle": {"url": "/services/personel/hitap/hizmet-askerlik-guncelle"},
    "HitapAskerlikSil": {"url": "/services/personel/hitap/hizmet-askerlik-sil"},
    "HitapBirlestirmeGetir": {"url": "/services/personel/hitap/hizmet-birlestirme-getir"},
    "HitapBirlestirmeSenkronizeEt": {"url": "/services/personel/hitap/hizmet-birlestirme-sync"},
    "HitapBirlestirmeEkle": {"url": "/services/personel/hitap/hizmet-birlestirme-ekle"},
    "HitapBirlestirmeGuncelle": {"url": "/services/personel/hitap/hizmet-birlestirme-guncelle"},
    "HitapBirlestirmeSil": {"url": "/services/personel/hitap/hizmet-birlestirme-sil"},
    "HitapBorclanmaGetir": {"url": "/services/personel/hitap/hizmet-borclanma-getir"},
    "HitapBorclanmaSenkronizeEt": {"url": "/services/personel/hitap/hizmet-borclanma-sync"},
    "HitapBorclanmaEkle": {"url": "/services/personel/hitap/hizmet-borclanma-ekle"},
    "HitapBorclanmaGuncelle": {"url": "/services/personel/hitap/hizmet-borclanma-guncelle"},
    "HitapBorclanmaSil": {"url": "/services/personel/hitap/hizmet-borclanma-sil"},
    "HitapHizmetCetveliGetir": {"url": "/services/personel/hitap/hizmet-cetveli-getir"},
    "HitapHizmetCetveliSenkronizeEt": {"url": "/services/personel/hitap/hizmet-cetveli-sync"},
    "HitapHizmetCetveliEkle": {"url": "/services/personel/hitap/hizmet-cetveli-ekle"},
    "HitapHizmetCetveliGuncelle": {"url": "/services/personel/hitap/hizmet-cetveli-guncelle"},
    "HitapHizmetCetveliSil": {"url": "/services/personel/hitap/hizmet-cetveli-sil"},
    "HitapIHSGetir": {"url": "/services/personel/hitap/hizmet-ihs-getir"},
    "HitapIHSSenkronizeEt": {"url": "/services/personel/hitap/hizmet-ihs-sync"},
    "HitapIHSEkle": {"url": "/services/personel/hitap/hizmet-ihs-ekle"},
    "HitapIHSGuncelle": {"url": "/services/personel/hitap/hizmet-ihs-guncelle"},
    "HitapIHSSil": {"url": "/services/personel/hitap/hizmet-ihs-sil"},
    "HitapIstisnaiIlgiGetir": {"url": "/services/personel/hitap/hizmet-istisnai-ilgi-getir"},
    "HitapIstisnaiIlgiSenkronizeEt": {"url": "/services/personel/hitap/hizmet-istisnai-ilgi-sync"},
    "HitapIstisnaiIlgiEkle": {"url": "/services/personel/hitap/hizmet-istisnai-ilgi-ekle"},
    "HitapIstisnaiIlgiGuncelle": {"url": "/services/personel/hitap/hizmet-istisnai-ilgi-guncelle"},
    "HitapIstisnaiIlgiSil": {"url": "/services/personel/hitap/hizmet-istisnai-ilgi-sil"},
    "HitapKursGetir": {"url": "/services/personel/hitap/hizmet-kurs-getir"},
    "HitapKursSenkronizeEt": {"url": "/services/personel/hitap/hizmet-kurs-sync"},
    "HitapKursEkle": {"url": "/services/personel/hitap/hizmet-kurs-ekle"},
    "HitapKursGuncelle": {"url": "/services/personel/hitap/hizmet-kurs-guncelle"},
    "HitapKursSil": {"url": "/services/personel/hitap/hizmet-kurs-sil"},
    "HitapMahkemeGetir": {"url": "/services/personel/hitap/hizmet-mahkeme-getir"},
    "HitapMahkemeSenkronizeEt": {"url": "/services/personel/hitap/hizmet-mahkeme-sync"},
    "HitapMahkemeEkle": {"url": "/services/personel/hitap/hizmet-mahkeme-ekle"},
    "HitapMahkemeGuncelle": {"url": "/services/personel/hitap/hizmet-mahkeme-guncelle"},
    "HitapMahkemeSil": {"url": "/services/personel/hitap/hizmet-mahkeme-sil"},
    "HitapNufusGetir": {"url": "/services/personel/hitap/hizmet-nufus-getir"},
    "HitapNufusSenkronizeEt": {"url": "/services/personel/hitap/hizmet-nufus-sync"},
    "HitapNufusEkle": {"url": "/services/personel/hitap/hizmet-nufus-ekle"},
    "HitapNufusGuncelle": {"url": "/services/personel/hitap/hizmet-nufus-guncelle"},
    "HitapNufusSil": {"url": "/services/personel/hitap/hizmet-nufus-sil"},
    "HitapOkulGetir": {"url": "/services/personel/hitap/hizmet-okul-getir"},
    "HitapOkulSenkronizeEt": {"url": "/services/personel/hitap/hizmet-okul-sync"},
    "HitapOkulEkle": {"url": "/services/personel/hitap/hizmet-okul-ekle"},
    "HitapOkulGuncelle": {"url": "/services/personel/hitap/hizmet-okul-guncelle"},
    "HitapOkulSil": {"url": "/services/personel/hitap/hizmet-okul-sil"},
    "HitapTazminatGetir": {"url": "/services/personel/hitap/hizmet-tazminat-getir"},
    "HitapTazminatSenkronizeEt": {"url": "/services/personel/hitap/hizmet-tazminat-sync"},
    "HitapTazminatEkle": {"url": "/services/personel/hitap/hizmet-tazminat-ekle"},
    "HitapTazminatGuncelle": {"url": "/services/personel/hitap/hizmet-tazminat-guncelle"},
    "HitapTazminatSil": {"url": "/services/personel/hitap/hizmet-tazminat-sil"},
    "HitapUnvanGetir": {"url": "/services/personel/hitap/hizmet-unvan-getir"},
    "HitapUnvanSenkronizeEt": {"url": "/services/personel/hitap/hizmet-unvan-sync"},
    "HitapUnvanEkle": {"url": "/services/personel/hitap/hizmet-unvan-ekle"},
    "HitapUnvanGuncelle": {"url": "/services/personel/hitap/hizmet-unvan-guncelle"},
    "HitapUnvanSil": {"url": "/services/personel/hitap/hizmet-unvan-sil"},
    "MernisKimlikBilgileriGetir": {"url": "/services/common/kisi-sorgula-tc-kimlik-no"},
    "MernisCuzdanBilgileriGetir": {"url": "/services/common/cuzdan-sorgula-tc-kimlik-no"},
    "KPSAdresBilgileriGetir": {"url": "/services/common/adres-sorgula"},
    "DersProgramiOlustur": {"url": "/services/ogrenci/ders-programi-start-solver"},
    "SinavProgramiOlustur": {"url": "/services/ogrenci/sinav-plani-start-exam-solver"},
    "EPostaYolla": {"url": "/services/common/e-posta-yolla"}
}
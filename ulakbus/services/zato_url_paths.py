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
    "HitapAcikSureGetir": {"url": "hizmet-acik-sure-getir"},
    "HitapAcikSureSenkronizeEt": {"url": "hizmet-acik-sure-sync"},
    "HitapAcikSureEkle": {"url": "hizmet-acik-sure-ekle"},
    "HitapAcikSureGuncelle": {"url": "hizmet-acik-sure-guncelle"},
    "HitapAcikSureSil": {"url": "hizmet-acik-sure-sil"},
    "HitapAskerlikGetir": {"url": "hizmet-askerlik-getir"},
    "HitapAskerlikSenkronizeEt": {"url": "hizmet-askerlik-sync"},
    "HitapAskerlikEkle": {"url": "hizmet-askerlik-ekle"},
    "HitapAskerlikGuncelle": {"url": "hizmet-askerlik-guncelle"},
    "HitapAskerlikSil": {"url": "hizmet-askerlik-sil"},
    "HitapBirlestirmeGetir": {"url": "hizmet-birlestirme-getir"},
    "HitapBirlestirmeSenkronizeEt": {"url": "hizmet-birlestirme-sync"},
    "HitapBirlestirmeEkle": {"url": "hizmet-birlestirme-ekle"},
    "HitapBirlestirmeGuncelle": {"url": "hizmet-birlestirme-guncelle"},
    "HitapBirlestirmeSil": {"url": "hizmet-birlestirme-sil"},
    "HitapBorclanmaGetir": {"url": "hizmet-borclanma-getir"},
    "HitapBorclanmaSenkronizeEt": {"url": "hizmet-borclanma-sync"},
    "HitapBorclanmaEkle": {"url": "hizmet-borclanma-ekle"},
    "HitapBorclanmaGuncelle": {"url": "hizmet-borclanma-guncelle"},
    "HitapBorclanmaSil": {"url": "hizmet-borclanma-sil"},
    "HitapHizmetCetveliGetir": {"url": "hizmet-cetveli-getir"},
    "HitapHizmetCetveliSenkronizeEt": {"url": "hizmet-cetveli-sync"},
    "HitapHizmetCetveliEkle": {"url": "hizmet-cetveli-ekle"},
    "HitapHizmetCetveliGuncelle": {"url": "hizmet-cetveli-guncelle"},
    "HitapHizmetCetveliSil": {"url": "hizmet-cetveli-sil"},
    "HitapIHSGetir": {"url": "hizmet-ihs-getir"},
    "HitapIHSSenkronizeEt": {"url": "hizmet-ihs-sync"},
    "HitapIHSEkle": {"url": "hizmet-ihs-ekle"},
    "HitapIHSGuncelle": {"url": "hizmet-ihs-guncelle"},
    "HitapIHSSil": {"url": "hizmet-ihs-sil"},
    "HitapIstisnaiIlgiGetir": {"url": "hizmet-istisnai-ilgi-getir"},
    "HitapIstisnaiIlgiSenkronizeEt": {"url": "hizmet-istisnai-ilgi-sync"},
    "HitapIstisnaiIlgiEkle": {"url": "hizmet-istisnai-ilgi-ekle"},
    "HitapIstisnaiIlgiGuncelle": {"url": "hizmet-istisnai-ilgi-guncelle"},
    "HitapIstisnaiIlgiSil": {"url": "hizmet-istisnai-ilgi-sil"},
    "HitapKursGetir": {"url": "hizmet-kurs-getir"},
    "HitapKursSenkronizeEt": {"url": "hizmet-kurs-sync"},
    "HitapKursEkle": {"url": "hizmet-kurs-ekle"},
    "HitapKursGuncelle": {"url": "hizmet-kurs-guncelle"},
    "HitapKursSil": {"url": "hizmet-kurs-sil"},
    "HitapMahkemeGetir": {"url": "hizmet-mahkeme-getir"},
    "HitapMahkemeSenkronizeEt": {"url": "hizmet-mahkeme-sync"},
    "HitapMahkemeEkle": {"url": "hizmet-mahkeme-ekle"},
    "HitapMahkemeGuncelle": {"url": "hizmet-mahkeme-guncelle"},
    "HitapMahkemeSil": {"url": "hizmet-mahkeme-sil"},
    "HitapNufusGetir": {"url": "hizmet-nufus-getir"},
    "HitapNufusSenkronizeEt": {"url": "hizmet-nufus-sync"},
    "HitapNufusEkle": {"url": "hizmet-nufus-ekle"},
    "HitapNufusGuncelle": {"url": "/services/personel/hitap/hizmet-nufus-guncelle"},
    "HitapNufusSil": {"url": "hizmet-nufus-sil"},
    "HitapOkulGetir": {"url": "/services/personel/hitap/hizmet-okul-getir"},
    "HitapOkulSenkronizeEt": {"url": "hizmet-okul-sync"},
    "HitapOkulEkle": {"url": "hizmet-okul-ekle"},
    "HitapOkulGuncelle": {"url": "/services/personel/hitap/hizmet-okul-guncelle"},
    "HitapOkulSil": {"url": "hizmet-okul-sil"},
    "HitapTazminatGetir": {"url": "hizmet-tazminat-getir"},
    "HitapTazminatSenkronizeEt": {"url": "hizmet-tazminat-sync"},
    "HitapTazminatEkle": {"url": "hizmet-tazminat-ekle"},
    "HitapTazminatGuncelle": {"url": "hizmet-tazminat-guncelle"},
    "HitapTazminatSil": {"url": "hizmet-tazminat-sil"},
    "HitapUnvanGetir": {"url": "hizmet-unvan-getir"},
    "HitapUnvanSenkronizeEt": {"url": "hizmet-unvan-sync"},
    "HitapUnvanEkle": {"url": "hizmet-unvan-ekle"},
    "HitapUnvanGuncelle": {"url": "hizmet-unvan-guncelle"},
    "HitapUnvanSil": {"url": "hizmet-unvan-sil"},
    "MernisKimlikBilgileriGetir": {"url": "services/common/kisi-sorgula-tc-kimlik-no"},
    "MernisCuzdanBilgileriGetir": {"url": "services/common/cuzdan-sorgula-tc-kimlik-no"},
    "KPSAdresBilgileriGetir": {"url": "services/common/adres-sorgula"},
    "DersProgramiOlustur": {"url": "services/ogrenci/ders-programi-start-solver"},
    "SinavProgramiOlustur": {"url": "services/ogrenci/sinav-plani-start-exam-solver"},
    "EPostaYolla": {"url": "e-posta"}
}
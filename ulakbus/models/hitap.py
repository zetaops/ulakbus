from personel import Personel
from pyoko import Model, field

class HizmetKurs(Model):
   tckn = field.String("TC Kimlik No", index=True)
   kayit_no = field.String("Kursa Kayıt No", index=True)
   kurs_ogrenim_suresi = field.Integer("Kurs Öğrenim Süresi",index=True)
   mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True)
   kurs_nevi = field.String("Kurs Nevi", index=True)
   bolum_ad = field.String("Bölüm Adı", index=True)
   okul_ad = field.String("Okul Adı", index=True)
   ogrenim_yeri = field.String("Öğrenim Yeri", index=True)
   denklik_tarihi = field.Date("Denklik Tarihi", index=True)
   denklik_okulu = field.String("Denklik Okulu", index=True)
   denklik_bolum = field.String("Denklik Bölüm", index=True)
   kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)

class HizmetOkul(Model):
   kayit_no = field.String("Kayıt No", index=True)
   tckn = field.String("TC Kimlik No", index=True)
   ogrenim_durumu = field.Integer("Öğrenim Durumu", index=True)
   mezuniyet_tarihi = field.Date("Mezuniyet Tarihi", index=True)
   okul_ad = field.String("Okul Adı", index=True)
   bolum = field.String("Bölüm", index=True)
   ogrenim_yer = field.String("Öğrenim Yeri", index=True)
   denklik_tarihi = field.Date("Denklik Tarihi", index=True)
   denklik_okul = field.String("Denklik Okul", index=True)
   denklik_bolum = field.String("Denklik Bölüm", index=True)
   ogrenim_suresi = field.Integer("Öğrenim Süresi", index=True)
   hazirlik = field.Boolean("Hazırlık", index=True)
   kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)

class HizmetMahkeme(Model):
   tckn = field.String("TC Kimlik No", index=True)
   kayit_no = field.String("kayıt No", index=True)
   mahkeme_ad = field.String("Mahkeme Adı", index=True)
   sebep = field.Integer("Mahkeme Sebebi", index=True)
   karar_tarihi = field.Date("Mahkeme Karar Tarihi", index=True)
   karar_sayisi = field.Integer("Karar Sayısı", index=True)
   kesinlesme_tarihi = field.Date("Kesinleşme Tarihi", index=True)
   asil_dogum_tarihi = field.Date("Asıl Doğum Tarihi", index=True)
   tashih_dogum_tarihi = field.Date("Tashih Doğum Tarihi", index=True)
   asil_ad = field.String("Asıl Ad", index=True)
   tashih_ad = field.String("Tashih Ad", index=True)
   asil_soyad = field.String("Asıl Soyad", index=True)
   tashih_soyad = field.String("Tashih Soyad", index=True)
   gecerli_dogum_tarihi = field.Date("Geçerli Doğum Tarihi", index=True)
   aciklama = field.String("Açıklama", index=True)
   gun_sayisi = field.Integer("Gün Sayısı", index=True)
   kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)

class HizmetBirlestirme(Model):
   tckn = field.String("TC Kimlik No", index=True)
   kayit_no = field.String("Kayıt No", index=True)
   sgk_nevi = field.Integer("SGK Nevi", index=True)
   sgk_sicil_no = field.String("SGK Sicil No", index=True)
   baslama_tarihi = field.Date("Başlama Tarihi", index=True)
   bitis_tarihi = field.Date("Bitiş Tarihi", index=True)
   sure = field.Integer("Süre", index=True)
   kamuIsyeri_ad = field.String("Kamu İşyeri Adı", index=True)
   ozel_isyeri_ad = field.String("Özel İşyeri Adı", index=True)
   bag_kur_meslek = field.String("Bağ-Kur Meslek", index=True)
   ulke_kod = field.Integer("Ülke Kodu", index=True)
   banka_sandik_kod = field.Integer("Banka Sandık Kodu", index=True)
   kıdem_tazminat_odeme_durumu = field.String("Kıdem Tazminat Ödeme Durumu", index=True)
   ayrilma_nedeni = field.String("Ayrılma Nedeni", index=True)
   kha_durum = field.String("", index=True)
   kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)

class HizmetTazminat(Model):
   kayit_no = field.String("Kayıt No", index=True)
   tckn = field.String("TC Kimlik No", index=True)
   unvan_kod = field.Integer("Ünvan Kodu", index=True)
   makam = field.Integer("Makam", index=True)
   gorev = field.Integer("Görev", index=True)
   temsil = field.Integer("Temsil", index=True)
   tazminat_tarihi = field.Date("Tazminat Tarihi", index=True)
   tazminat_bitis_tarihi = field.Date("Tazminat Bitiş Tarihi", index=True)
   kadrosuzluk = field.Integer("Kadrosuzluk", index=True)
   kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)

class HizmetUnvan(Model):
   kayit_no = field.String("Hizmet Kayıt No", index=True)
   tckn = field.String("TC Kimlik No", index=True)
   unvan_kod = field.Integer("Ünvan Kodu", index=True)
   unvan_tarihi = field.Date("Ünvan Tarihi", index=True)
   unvan_bitis_tarihi = field.Date("Ünvan Bitiş Tarihi", index=True)
   hizmet_sinifi = field.String("Hizmet Sınıfı", index=True)
   asil_vekil = field.String("Asıl Vekil", index=True)
   atama_sekli = field.String("Atama Sekli", index=True)
   kurum_onay_tarihi = field.Date("Kurum Onay Tarihi", index=True)
   fhz_orani = field.Float("", index=True)

class HizmetAcikSure(Model):
   tckn = field.String("TC Kimlik No", index=True)
   kayit_no = field.String("Kayıt No", index=True)
   acik_sekil = field.Integer("Açık Şekil", index=True)
   durum = field.Integer("Durum", index=True)
   hizmet_durum = field.Integer("Hizmet Durumu", index=True)
   husus = field.String("Husus", index=True)
   aciga_alinma_tarih = field.Date("Açığa Alınma Tarihi", index=True)
   goreve_son_tarih = field.Date("Göreve Son Tarih", index=True)
   goreve_iade_istem_tarih = field.Date("Göreve İade İstem Tarihi", index=True)
   goreve_iade_tarih = field.Date("Göreve İade Tarihi", index=True)
   acik_aylik_bas_tarih = field.Date("Açık Aylık Baş Tarihi", index=True)










"""

@startuml

skinparam classAttributeFontName Monospaced
skinparam classBackgroundColor #FFFFFF
skinparam classBorderColor #D8D8D8
skinparam packageBorderColor #BDBDBD
skinparam classArrowColor #0B615E
skinparam shadowing false

'skinparam monochrome true
'skinparam nodesep 100
'skinparam ranksep 100
'note "All <color:black><b> (M)odels</b></color> extends <b>pyoko.Model</b> class" as N #orchid
title
<size:24>Entity Based Model Diagram</size>
( All Models extends <b>pyoko.Model</b> class )
endtitle
'legend left
'n..*     n or more instances
'n..m    Min n, Max m instances
'endlegend


' field_name            field_type     null blank
'                                      _ = True
'                                      * * = False



package auth{

class Kullanici <<(M,orchid)>>{
|_ id                  Int
|_ **IdentityInfo(Model)**
   |_  tckno           string
   |_  name            string
   |_  surname         string
   |_  birth_date      Date
   |_  birth_place     Date
   |_  neighborhood    string
   |_  father_name     String
   |_  mother_name     String
   |_  gender          String
   |_  marital_status  String
   |_  town_code       Int
   |_  city            Int
   |_  blood_type      String
   |_  former_surname  String
|_ **ContactInfo(Model)**
   |_  home_phone      String
   |_  work_phone      String
   |_  mobile_phone    String
   |_  address_pri     String
   |_  address_sec     String
   |_  postal_code     Int
   |_  primary_email   String
   |_  secondary_email String
   |_  website         String
--
}


class Yetki<<(M,orchid)>>{
name            String
code            String
}
}

package hitap{

class HizmetKurs <<(M,orchid)>>{
tckn                    String   * *
kayit_no                String
kurs_ogrenim_suresi     Int      * *
mezuniyet_tarihi        Date     * *
kurs_nevi               String   * *
bolum_ad                String   * *
okul_ad                 String   * *
ogrenim_yeri            String
denklik_tarihi          Date
denklik_okulu           String
denklik_bolum           String
kurum_onay_tarihi       Date     * *
--
personel       Personel()    * *

--
}

class HizmetOkul <<(M,orchid)>>{
kayit_no                String
tckn                    String   * *
ogrenim_durumu          Int      * *
mezuniyet_tarihi        Date     * *
okul_ad                 String
bolum                   String
ogrenim_yer             String
denklik_tarihi          Date
denklik_okul            String
denklik_bolum           String
ogrenim_suresi          Int      * *
hazirlik                Boolean  * *
kurum_onay_tarihi       Date     * *
--
personel       Personel()    * *
}


class HizmetMahkeme <<(M,orchid)>>{
tckn                    String   * *
kayit_no                String
mahkeme_ad              String   * *
sebep                   Int      * *
karar_tarihi            Date     * *
karar_sayisi            Int      * *
kesinlesme_tarihi       Date
asil_dogum_tarihi       Date
tashih_dogum_tarihi     Date
asil_ad                 String
tashih_ad               String
asil_soyad              String
tashih_soyad            String
gecerli_dogum_tarihi    Date
aciklama                String
gun_sayisi              Int
kurum_onay_tarihi       Date     * *
--
personel       Personel()    * *
}

class HizmetBirlestirme <<(M,orchid)>>{
tckn                          String   * *
kayit_no                      String
sgk_nevi                      Int      * *
sgk_sicil_no                  String   * *
baslama_tarihi                Date     * *
bitis_tarihi                  Date     * *
sure                          Int      * *
kamuİsyeri_ad                 String
ozel_isyeri_ad                String
bag_kur_meslek                String
ulke_kod                      Int
banka_sandık_kod              Int
kıdem_tazminat_odeme_durumu   String
ayrilma_nedeni                String
kha_durum                     String
kurum_onay_tarihi             Date     * *
--
personel       Personel()    * *
}

class HizmetTazminat <<(M,orchid)>>{
kayit_no                String
tckn                    String   * *
unvan_kod               Int      * *
makam                   Int
gorev                   Int
temsil                  Int
tazminat_tarihi         Date     * *
tazminat_bitis_tarihi   Date
kadrosuzluk             Int
kurum_onay_tarihi       Date     * *
--
personel       Personel()    * *
}

class HizmetUnvan <<(M,orchid)>>{
kayit_no                String
tckn                    String   * *
unvan_kod               Int      * *
unvan_tarihi            Date     * *
unvan_bitis_tarihi      Date
hizmet_sinifi           String   * *
asil_vekil              String   * *
atama_sekli             String   * *
kurum_onay_tarihi       Date     * *
fhz_orani               Float
--
personel       Personel()    * *
}

class HizmetAcikSure <<(M,orchid)>>{
tckn                          String   * *
kayit_no                      String
acik_sekil                    Int      * *
durum                         Int      * *
hizmet_durum                  Int      * *
husus                         String   * *
aciga_alinma_tarih            Date
goreve_son_tarih              Date
goreve_iade_istem_tarih       Date
goreve_iade_tarih             Date
acik_aylik_bas_tarih          Date
acik_aylik_bit_tarih          Date
goreve_son_aylik_bas_tarih    Date
goreve_son_aylik_bit_tarih    Date
s_yonetim_kald_tarih          Date
aciktan_atanma_tarih          Date
kurum_onay_tarihi             Date     * *
--
personel       Personel()    * *
}

class HizmetBorclanma <<(M,orchid)>>{
tckn                 String   * *
kayit_no             String
ad                   String   * *
soyad                String   * *
emekli_sicil         String   * *
derece               Int      * *
kademe               Int      * *
ekgosterge           Int      * *
baslama_tarihi       Date     * *
bitis_tarihi         Date     * *
gun_sayisi           Int      * *
kanun_kod            Int      * *
borc_nevi            String   * *
toplam_tutar         Float    * *
odenen_miktar        Float
calistigi_kurum      String   * *
isyeri_il            String   * *
isyeri_ilce          String   * *
borclanma_tarihi     Date
odeme_tarihi         Date
kurum_onay_tarihi    Date     * *
--
personel       Personel()    * *
}
class HizmetIHS <<(M,orchid)>>{
tckn                 String   * *
kayit_no             String
baslama_tarihi       Date     * *
bitis_tarihi         Date     * *
ihz_nevi             Int      * *
--
personel       Personel()    * *
}

class HizmetIstisnaiIlgi <<(M,orchid)>>{
tckn                 String   * *
kayit_no             String
baslama_tarihi       Date     * *
bitis_tarihi         Date     * *
gun_sayisi           Int      * *
istisnai_ilgi_nevi   Int      * *
kha_durum            String   * *
kurum_onay_tarihi    Date     * *
--
personel       Personel()    * *
}


class HizmetKayitlari<<(M,orchid)>>{
tckn                                String   * *
kayit_no                            String
baslama_tarihi                      Date
bitis_tarihi                        Date
gorev                               String   * *
unvan_kod                           Int      * *
yevmiye                             String
ucret                               String
hizmet_sinifi                       String   * *
kadro_derece                        Int      * *
odeme_derece                        Int      * *
odeme_kademe                        Int      * *
odeme_ekgosterge                    Int      * *
kazanilmis_hak_ayligi_derece        Int      * *
kazanilmis_hak_ayligi_kademe        Int      * *
kazanilmis_hak_ayligi_ekgosterge    Int      * *
emekli_derece                       Int      * *
emekli_kademe                       Int      * *
emekli_ekgosterge                   Int      * *
sebep_kod                           Int      * *
kurum_onay_tarihi                   Date     * *
--
personel             **Personel()**
}




}
class AskerlikKayitlari <<(M,orchid)>>{
askerlik_nevi                    Int      * *
baslama_tarihi                   Date
bitis_tarihi                     Date
kayit_no                         String
kita_baslama_tarihi              Date
kita_bitis_tarihi                Date
muafiyet_neden                   String
sayilmayan_gun_sayisi            Int
sinif_okulu_sicil                String
subayliktan_erlige_gecis_tarihi  Date
subay_okulu_giris_tarihi         Date
tckn                             String   * *
tegmen_nasp_tarihi               Date
gorev_yeri                       String
kurum_onay_tarihi                Date     * *
astegmen_nasp_tarihi             Date
--
personel                         **Personel()**
}


class Birim<<(M,orchid)>>{
type        String
name        String
parent      **Birim()**
--
}

class Personel <<(M,orchid)>>{
tckn              String
ad                String
soyad             String
personel_turu     String
dogum_tarihi      Date
cep_telefonu      String
--
**NufusKayitlari(Node)**
|_ tckn                       String  * *
|_ ad                         String  * *
|_ soyad                      String  * *
|_ ilk_soy_ad                 String
|_ dogum_tarihi               Date    * *
|_ cinsiyet                   String  * *
|_ emekli_sicil_no            Int     * *
|_ emekli_giris_tarih         Date    * *
|_ memuriyet_baslama_tarihi   Date    * *
|_ kurum_sicil                String  * *
|_ maluliyet_kod              String  * *
|_ yetki_seviyesi             String  * *
|_ aciklama                   String
|_ kuruma_baslama_tarihi      Date
|_ gorev_tarihi6495           Date
|_ emekli_sicil6495           Int
|_ durum                      Boolean * *
|_ sebep                      Int     * *
}

class Atama <<(M,orchid)>>{
kurum_sicil_no             String   * *
personel_tip               Int      * *
hizmet_sinif               Int      * *
statu                      Int      * *
gorev_suresi_baslama       Date     * *
gorev_suresi_bitis         Date     * *
goreve_baslama_tarihi      Date     * *
ibraz_tarihi               Date     * *
durum                      Int      * *
mecburi_hizmet_suresi      Date
nereden                    Int
atama_aciklama             String
goreve_baslama_aciklama    String
kadro_unvan                Int      * *
kadro_derece               Int      * *
--
kadro                      Kadro()  * *
}

class Kadro <<(M,orchid)>>{
durum                Int          * *
unvan                Int          * *
derece               Int          * *
--
rol                  Rol()
aciklama             String

}


class SoyutRol<<(M,orchid)>>{
Yetkiler(ListNode)
|_permission    **Yetkiler()**
id              Int
name            String
--
}


class Izin<<(M,orchid)>>{
tip            Int            * *
baslangic      Date           * *
bitis          Date           * *
onay           Date           * *
adres          String         * *
telefon        String         * *
--
personel       Personel()    * *
vekil          Personel()    * *
}

class UcretsizIzin<<(M,orchid)>>{
tip            Int            * *
baslangic      Date           * *
bitis          Date           * *
onay           Date           * *
**Donus(Node)**
donus_sebep    Int            * _
ise_baslama    Date           * _


--
personel       Personel()    * *
vekil          Personel()    * *
}

class Rol<<(M,orchid)>>{
soyut_rol   **SoyutRol()**    * *
kullanici            **Kullanici()**
birim            **Birim()**  * *
Yetkiler(ListNode)
|_permission    **Yetkiler()**
active          Boolean
baslangic_tarihi      Date
bitis_tarihi        Date
--
}


Personel "1" -- "0..*" UcretsizIzin
Personel "1" -- "0..*" UcretsizIzin
Personel "1" -- "0..*" AskerlikKayitlari
Personel "1" -- "0..*" HizmetKayitlari
Personel "1" -- "0..*" HizmetKurs
Personel "1" -- "0..*" HizmetOkul
Personel "1" -- "0..*" HizmetTazminat
Personel "1" -- "0..*" HizmetMahkeme
Personel "1" -- "0..*" HizmetUnvan
Personel "1" -- "0..*" HizmetBorclanma
Personel "1" -- "0..*" HizmetBirlestirme
Personel "1" -- "0..*" HizmetIHS
Personel "1" -- "0..*" HizmetAcikSure
Personel "1" -- "0..*" HizmetIstisnaiIlgi
Personel "1" -- "0..*" Atama


Birim "0..*" -- "1" Atama
Birim "0..*" -- "1" Rol
Birim "0..1" --o "0..*" Birim
Kullanici "0..*" o-- "1" Rol

Rol "1" --o "0..*" SoyutRol
SoyutRol "0..*" o-- "0..*" Yetki
Rol "0..*" o-- "0..*" Yetki


Kullanici "1" -- "1" Personel
Birim "0..*" o-- "1..*" Location

@enduml
"""
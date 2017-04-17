+++++++++++++++++++
Dış Veri Kaynakları
+++++++++++++++++++

Sistem birçok veri kaynağı ile konuşabilecek, ihtiyaç duyulan veri alışverişini sağlayacaktır. Bu dış kaynakların biçemleri XML, JSON şeklinde değişik olabilir. Konuşulacak servislerin detayları aşağıdaki gibidir.

LDAP
----
Birçok üniversitede doğrulama ve yetkilendirme gibi amaçlar için aktif şekilde kullanılan LDAP sistem tarafından desteklenecektir. LDAP’ta yapılan değişiklikler sisteme düzenli şekilde yansıtılacak, sistem gerektiğinde LDAP şemalarında değişiklik yapabilecektir. Özellikle göç aşamaları gibi LDAP kullanımının kaçınılmaz olduğu zaman ve şartlar için öngörüşmüştür.

KBS
----
Kamu Harcama ve Muhasebe Bilişim Sistemi (KBS) Maliye Bakanlığı tarafından sağlanan, kamu kurumlarında tahakkuk ve ödeme işlemlerinin otomasyonunu sağlayan bir edevlet uygulamasıdır. Üniversitelerde de birçok mali işlem KBS aracılığıyla gerçekleştirilmektedir. KBS sisteminin el verdiği ölçüde entegrasyon sağlanacaktır.

HİTAP
-----
HİTAP(Hizmet Takip Projesi), devlet memurlarının hizmetlerinin takibi amacıyla Sosyal Güvenlik Kurumu tarafından geliştirilmiş edevlet uygulamasıdır. Personel bilgilerinin iki yönlü güncellenmesi için HİTAP servisi ile düzenli şekilde veri alışverişi yapılacaktır. HİTAP bir SOAP servisidir.

ASAL
----
ASAL Servisi, Milli Savunma Bakanlığı tarafından sağlanan yurttaşların askerlik durumlarını sorgulayabildikleri  bir edevlet uygulamasıdır. Bu uygulama ile web servisi şeklinde konuşup, erkek öğrenci ve personin askerlik durumları karşılıklı olarak takip edilecektir.

ÖSYM
----
Öğrenci kayıtlarının otomatizasyonuna yardımcı olmak için, yerleştirme bilgileri ÖSYM’nin sunduğu

YÖKSİS
------
YÖKSİS (Yükseköğretim Bilgi Sistemi) YÖK tarafından kurulan yükseköğretim kurumlarının çeşitli bilgilerinin merkezi şekilde saklandığı sistemdir. YÖK üniversitelerden YÖKSİS’e düzenli veri girişi beklemektedir. Ayrıca YÖK üniversitelerde açılan bölüm ve programların bilgilerinde çeşitli güncellemeler yapmakta, bu güncellemelerin verinin bütünlüğü ve tutarlılığı için en kısa sürede üniversitelerin sistemlerine aktarılması gerekmektedir. YÖKSİS entegrasyonu bu ihtiyaç ve sorunlara çözüm olacaktır. YÖKSİS bir SOAP servisidir.

AKS
----
Adres Kayıt Sistemi, Nüfus ve Vatandaşlık İşleri tarafından sağlanan bir edevlet hizmetidir. Sistemimiz bu hizmet ile tam entegrasyon halinde olacak ve sisteme kayıtlı kişilerin adres bilgilerini bu sistemdeki kayıtlar ile güncelleyecektir.

MERNİS
------
AKS gibi merkezi kimlik hizmetidir. Sistemde kayıtlı kişilerin kimlik bilgileri MERNİS ile uyumlu şekilde saklanacaktır.

BANKALAR
--------
Öğrenci Harç ve ödeme işlemlerinin takip edilmesi için bankaya açılacak olan servistir. Banka öğrencilerin ödemeleri gereken miktarları bu servis aracılığı ile öğrenir ve ödeme bilgilerini sisteme geri bildirir. Bizim tarafımızda açılacak servis REST türünde olacaktır.

SMS
----
Öğrenci ve personele SMS bildirimleri yapmak isteyecek öğrenciler üniversiteler kendi servislerini Zato ESB ile kolayca yazabileceklerdir.

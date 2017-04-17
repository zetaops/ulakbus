++++++++++++++++++++++++++++++++++++++
Eşli Gözden Geçirme (Peer Code Review)
++++++++++++++++++++++++++++++++++++++

Geliştiriciler, kodlarını çalıştıkları branchtan, master brancha merge etmeden önce bir diğer geliştirici ile birlikte gözden geçireceklerdir. Bu gözden geçirme sırasında aşağıdaki kontrol listesine uygunluk aranacaktır:

- **Kod Stili:** Kod, Statik analiz araçları tarafından yakalanamayan method ve değişken isimlerinin proje standartlarına uygunluğu gibi kriterlere karşı incelenir.

- **Belgelendirme:** Mümkün olduğunca yorum satırlarına gerek duyulmayan, anlaşılır kod yazılmalıdır. Ancak çeşitli nedenlerle kolayca anlaşılmayan bir kod öbeği varsa, bunun nedeni ve nasıl çalıştığı belgelendirilmelidir.

- **Girdilere Karşı Savunma:** Kullanıcıdan ya da üçüncü parti servis ve uygulamalardan gelen veriler, temizlenip biçimlendirilmeli, hata denetiminden geçirilmeli ve gerekiyorsa try/except blokları içerisinde işlenmelidir.

- **Test Edilebilirlik:** Sınıf ve metodlar birim testlerinin kolayca yazılabilmesine olanak verecek şekilde tasarlanmalıdır. Arayüzler (interface) mümkün olduğunca test ortamında taklit edilebilir olmalıdır.

- **Testler ve Kapsam:** Kodun tamamını kapsayan, doğru tasarlanmış yeterli sayıda birim testi yazılmış olmalıdır. Dış servislere bağımlı işlevlerin testi için gerekli mocking kütüphane ve sunucuları kullanılmalıdır.

- **Ayarlanabilirlik:** Uygulamanın çalışmasını ve davranışını etkileyen, dosya dizin yolları, açılır menüde gösterilecek seçenek sayısı gibi  değerler ya kullanıcı tarafından ya da uygulamanın konfigurasyon standardına uygun şekilde (çevre değişkenleri) ile ayarlanabilir olmalıdır.

- **Çöp Kod:** Yorum satırı haline getirilmiş kod olmamalıdır. Silinen herşey sürüm kontrol sisteminden geri getirilebilir.

- **Yapılacaklar:** Todo olarak bırakılmış eksiklerin, sorun çıkarmayacağından emin olunmalıdır.

- **Döngüler:** Döngüler uzunluk ve döngüden çıkış kriterlerinin uygunluğuna karşı denetlenmelidir.

- **Mevcudiyet Denetimi:** Nesneler, kullanılmadan önce, o kapsamda mevcut olup olmadıklarına karşı denetlenmelidir. Bu denetimler, birçok hatanın kaynağında yakalanmasını sağlar.

- **Kod Tekrarı:** Aynı işi yapan kodların tekrar yazılmasından kaçınılmalıdır. Bu amaçla özellikle projeye sonradan katılan geliştiricilerin, mevcut utility metodlarından haberdar olmaları sağlanmalıdır.

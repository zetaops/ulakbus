+++++++++++
Kalıcı Veri
+++++++++++

Verilerin kalıcı olarak saklanacağı Riak, basit anahtar-değer çiftlerinden map, set, counter gibi gelişmiş veri tiplerine, nihayetinde tutarlılıktan (eventually consistent) kesin tutarlılığa (strong consistency) kadar çeşitli veri saklama kiplerini destekleyen gelişmiş bir NoSQL veri tabanıdır.
JSON biçiminde saklanacak olan veriler, Riak’ın dahili Apache Solr entegrasyonunu sayesinde istenilen incelikte indekslenmekte ver sorgulanabilmektedir.

Kalıcı olarak depolanacak tüm veri sürümlendirilerek saklanacaktır. Bu sayede her hangi bir kaydın son 100 sürümü ya da son 10 yıl içindeki tüm sürümlerine istenildiği an ulaşılabilecektir.
Sürüm sayısına ya da süreye göre ne kadar geriye dönük saklama yapılacağı her bucket için kendi model tanımı altında yapılacaktır.

Veritabanı seviyesinde herhangi bir şablon kısıtı olmamasına rağmen, veriyi tutarlı biçimde saklayabilmek ve hızlı bir şekilde sorgulayarak erişebilmek için tüm veriler iç içe Python sınıfları şeklinde modellenecek, bu modeller kayıt esnasında JSON şeklinde biçimlendirilerek saklanacak ve yine modelde tanımlandığı şekilde indekslenecektir.

Test ve Prod ortamları için farklı bucketlar kullanılacak, değişen konfigurasyon ve yük testleri için geçici Riak clusterları açılacaktır.

Veri ve Veri Şablonu Göçü
-------------------------
Uygulamanın yaşamı boyunca veri şablonlarında yapılacak güncellemeler ve bu güncellemeler nedeniyle verinin kendisinde yapılması gerekecek veri göçleri Pyoko kütüphanesi ile sürümlendirilecek ve yönetilecektir. Uygulamayı bir üst sürüme güncellemek ya da önceki sürüme dönmek için gerekli veri tabanı işlemlerini içeren göç betikleri geliştirme aşamasında Pyoko yardımıyla türetilecek ve kod deposuna eklenecektir. Gerektiğinde, elle özel göç betikleride yazılacaktır.


++++++++++++++++++++++++
Tercih Edilen Yazılımlar
++++++++++++++++++++++++

Riak [10]_
**********
Riak, dağıtık bir veritabanı sistemidir. Verileri sunucular arasında dağıtarak yüksek erişilebilirliği sağlar. Riak’ın tercih edilmesindeki sebepler aşağıda sıralanmıştır:

- Çok kullanıcılı / çok rollü sistemde verilerin sürekli erişilebilir olması,

- Aynı veriye eş zamanlı erişerek okuma / yazma işlemlerinin, veriye erişimi bloke etmeyerek gerçekleştirilmesi,

- İş modeline uygun senaryolara göre ortaya çıkacak uyuşmazlıkların çözümlenebilmesine olanak vermesi,

- Zamanla büyüyen verinin sürekli yedekli olarak yönetilmesi,

- Veri tasarım şeklinin, RDBMS kalıpları dışında yapılabilmesi,
- Verinin “strong consistent” olarak tutulabilmesi sayesinde “ACID” benzeri bir tutarlılığa sahip olmak,

- Sistem tüm Türkiye çapında kullanılsa bile, değişik veri merkezlerinde “multi homed” olarak çalışabilir olması.

RiakCS [11]_
************
RiakCS, Riak veritabanı sisteminin üzerine kurulu nesne depolama (object storage) sistemidir. Sistemde kullanıcı tarafından üretilecek dokumanlar (resimler, doc, pdf vb) RiakCS ile saklanacaktır. RiakCS de dağıtık bir sistemdir. RiakCS ile yüksek erişilebilir, ölçeklenebilirlik dağıtık bir bulut depolama sistemi elde edilmiş olacaktır. RiakCS API (Uygulama Programlama Arayüzü) yaygın kullanılan Amazon S3 ile uyumludur.

Postgresql
**********
Postgresql, Zato Clusterı tarafından kullanılmaktadır. Cluster bilgileri gibi Zato’nun iç operasyonlarını ilgilendiren veriler saklanacaktır.


Redis [12]_
***********
Redis, bellekiçi key/value veritabanı sistemidir. Uygulama ile Riak arasında geçici depolama ve hızlı okuma işlemleri için kullanılacaktır. Bu sayede veritabanı üzerindeki yük hafifleyecek, veriye erişim çok yüksek hızlara çıkıp uygulama performası artacaktır.

Redis, ayrıca Zato tarafından benzer amaçlar için de kullanılacaktır.

Zato [13]_
**********
Zato Python ile geliştirilmiş Kurumsal Hizmet Veriyolu (Enterprise Service Bus) yazılımıdır. Zato ile iş akışlarına uygun olarak, uygulamalar arası veri trafiği, mikro servisler haline getirilerek düzenlenecektir. Zato sadece sistem içi operasyonlar için değil aynı zamanda dış kaynaklarla olan iletişimi de üzerine alıp onları sistemin içerden erişebileceği mikro servislere dönüştürecektir. Bu da dış dünya ile uygulamanın tıpkı içerdeki gibi benzer desenler ile konuşabilmesini sağlayarak tutarlılık sağlayacaktır.

HaProxy [14]_
*************
High Available (Yüksek Erişilebilirlik) Proxy, hem kullanıcı arayüzeyleri aracılığı ile gelecek istekler (requests), hem dışarıya açılan servislere yapılacak çağrılar, hem de sistem içi bileşenlerin birbirleri ile olan iletişimleri sonucu doğacak trafiği dengelemek ve yüksek erişilebilirliği sağlamak için kullanılacaktır.

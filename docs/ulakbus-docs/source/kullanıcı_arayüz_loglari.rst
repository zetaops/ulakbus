++++++++++++++++++++++++
Kullanıcı Arayüz Logları
++++++++++++++++++++++++

Kullanıcı arayüzünde oluşacak çalışma zamanı hataları tarayıcı konsoluna düşmektedir. Bu loglar yakalanarak sunucu tarafındaki log tutucuya gönderilerek kaydedilecektir.

Arayüz fonksiyonları logları belirtilen log seviyelerinde tutulacaktır..

Prod başlığında belirtilen maddeler ışığında arayüz logları için stacktrace.js kullanılacaktır.

**incele:**

http://logstash.net/docs/1.1.1/outputs/riak#setting_bucket

http://underthehood.meltwater.com/blog/2015/04/14/riak-elasticsearch-and-numad-walk-into-a-red-hat/

**Notlar:**

CEP için loglarla nasıl bir relation kuracağız? Loglardan event trigger etmek nasıl?

**Refleksler:**

- Duran servisleri yeniden başlatmak

- Ölenlerin yerine yenisini başlatmak

- Ağır yük altında olan servisleri genişletmek

- Hafif yük altında olan servisleri daraltmak

- Ölçeklenecek serviler için sistem kaynaklarının yetersizliğini tespit edip yeni kaynaklar eklemek veya kaynak ihtiyacını bildirmek. Mümkünse clustera yeni nodelar
otomatik eklemek.

- Kronik hale gelen problemlerin tespiti ve bilgilendirilmesi. Muhtemel konfigurasyon problemleri demek.

- Application loglarindan gelen uyarilar

Fleet API kullanarak clusterda tanımlı servisleri başlatmak / durdurmak mümkün. Node ekleyip çıkarmak için Openstack / GCE API ile konuşmamız gerekir. Notification eposta veya sms ile mümkün. Yukarıdakilere ek başka ne gibi aksiyonlar olabilir?

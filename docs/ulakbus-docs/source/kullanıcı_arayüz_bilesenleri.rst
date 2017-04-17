++++++++++++++++++++++++++++
Kullanıcı Arayüz Bileşenleri
++++++++++++++++++++++++++++

	- Angular.js

AngularJS, MVC (Model View Controller) deseni sağlayan bir javascript uygulama çatısıdır. Kullanıcı arayüzü işlemlerini gerçekleştirecek tüm fonksiyonlar için kullanılır.  AngularJS standart sunucu taraflı yazılım geliştirme tekniklerini önyüze uygulayan ve önyüz geliştirmeyi hızlandıran bir uygulama çatısıdır. Karmaşık uygulamalarda DOM yönetimini başarıyla gerçekleştirir ve bu sayede uygulamanın kesintisiz ve sorunsuz çalışmasını sağlar.

        - Karma

Karma, Uygulama fonksiyonları için yazılmış testleri uygulayan test sürücüsüdür. Uygulamamızda Jasmine test çatısı testlerinin çalıştırılmasında kullanılır. Geliştiricinin her bir test ortamı için ayrı ayrı yapılandırma dosyası oluşturmadan tek bir yapılandırma ile testleri çalıştırabilmesini sağlar.

	- Selenium

Selenium, E2E testlerin çalıştırıldığı test platformudur. Kullanıcının tarayıcıda gerçekleştireceği işlemlerin sunucudan dönecek sonuca kadar test edilmesini sağlar.

        - Protractor

Protractor Selenium E2E testleri için bir çözüm enteratörü uygulama çatısıdır. Angularjs için Selenium özelleştirmeleriyle daha etkin ve bekleme sürelerini optimize ederek daha kısa sürede test edilmesini sağlar.

	- Jasmine

Jasmine, javascript testleri için kullanılan bir uygulama çatısıdır. Uygulama fonksiyonlarının testlerinde başarılı sentaksı ile geliştirme sürecini hızlandırır.

	- Bower

Bower, uygulamada kullanılacak paketlerin yönetimi için kullandığımız paket yönetim aracıdır. Uygulamanın gerektirdiği paketlerin kurulum esnasında eksiksiz şekilde ve sürüm uyumlu olarak kurulumunu sağlar.

	- Grunt

Grunt javascript uygulamaları için bir görev yürütücüsüdür. Küçültme, derleme, paketleme, testler gibi tekrarlanan görevleri otomasyon ile yürütmek için kullanılır.

	- Nodejs

Nodejs javascript uygulamaları için sunucu taraflı çalışma zamanı ortamıdır (runtime environment). Uygulama geliştirilirken bower, jasmine, karma gibi araçların kullanılması için gereklidir.
StackTrace.js

     - npm

npm nodejs için paket yönetim aracıdır. Uygulamanın geliştirme ortamı için gerekliliklerinin yönetilmesini sağlar.

     - Bootstrap3

Bootstrap3 grid sistem standardına uygun uyumlu (responsive) arayüz geliştirmek için kullanılan html, css vs javascript uygulama çatısıdır. Uygulamanın değişik ekran boyutlarında ve farklı cihazlarda sorunsuz çalışması için kullanılır.


Kullanıcı arayüz tasarımında uyulacak kurallar ve ilkeler
---------------------------------------------------------
	- Tüm tasarım bileşenleri html5 standardına uyacaktır.

	- Tasarım, kullanıcı arayüzü temiz ve tutarlı modeller temel alınarak anlamlı, kullanışlı ve amaca hizmet edecek şekilde organize etmelidir.

	- Basit ve sık yapılan işlemleri kolayca gerçekleştirebilmeli, kullanıcıyla açık ve kolay iletişim kurabilmeli, uzun işlemler için kullanışlı kısayollar sağlamalıdır.

	- Kullanıcı arayüzü tasarımı, yapılacak işlemler için tüm ihtiyaç duyulan opsiyonları ve materyalleri kullanıcının dikkatini dağıtmadan ve tam şekilde verebilmelidir.

	- Tasarım kullanıcıyı değişiklikler halinde bilgilendirmeli, kullanım esnasında oluşacak hataları kullanıcının anlayacağı şekilde sunabilmelidir.

	- Tasarım bileşenleri tekrar kullanılabilir olmalıdır.

	- Tasarım tüm ekran çözünürlüklerinde düzgün çalışabilmelidir.

	- Tasarım özürlü [22]_ kullanıcılar için “mümkün” olduğu kadar kolay bir kullanım sunabilmelidir.

Kullanıcı veri girişi ilkeleri
------------------------------
	- Kullanıcı verileri güvenli şekilde ve amaca yönelik geçerlilik kuralları çerçevesinde girilebilmelidir.

	- Kullanıcı daha az vuruş kullanarak kısa sürede veri girebilmelidir. Bunun için otomatik tamamlayıcılar, açılır menüler gibi kolaylaştırıcı bileşenler kullanılmalıdır.

++++++++++++++
Bulut Araçları
++++++++++++++

Docker [15]_
************
Docker uygulama ve servislerin konteynerlar şeklinde sanallaştırılarak Linux sistemleri üzerinde çalıştırılmasını sağlar. Docker uygulama ve servislerin yönetimini ve ölçeklenmesini kolaylaştrır. Bütün bileşenler kontenyerlar içinde servisler şeklinde çalışacaktır. Uygulama ve diğer tüm bileşenler bu sayede ihtiyaçlar ölçüsünde kolayca ölçeklenebilecektir.

Consul [16]_
************
Servislerin ve üzerlerinde çalıştıkları sistemlerin erişilebilirliği, yeni açılan veya herhangi bir sebeple çalışması kesintiye uğrayan, kapanan servislerden haberdar olmak için bütün host sistemlerde çalışacak servistir.

Systemd
*******
Systemd linux sistemler için neredeyse standart hale gelmiş modern servis yonetim aracıdır. Konteynerlar haline gelen uygulama parçacıkları systemd servisleri şeklinde yönetilecektir.

Etcd
****
Etcd bir sytemd servisi olarak çalışacak ve cluster çapında data alışverişi yapmak için kullanılacaktır. Ortam değişlenleri, değişen ayarlar, Consul ve benzeri servislerin haberleşmesi için kullanılacaktır.

Confd
*****
Confd başta haproxy gelmek üzere sistem servislerinin yeni durumlarına göre yeni ayar dosyaları üretme ve ilgili servisleri yeniden başlatma işini üstlenmektedir.

Flannel
*******
Flannel cluster içinde çalışan servisler (docker konteynerları) için özel bir ağ katmanı oluşturur.  Bu sayede servisler bu özel ağ üzerinden birbirleri ile konuşabilirler.
Fleet
*****
Fleet, konteyner haline getirilen servislerin cluster çapında systemd ye bildirilmesi ve yönetilmesinden sorumludur. Fleet yazılan bir servis için hazırlanan tanımlama dosyası (unit files) gereklerine uygun olarak, uygun gördüğü makinelerde çalıştırmaktan, bir başka makineye taşımaktan veya durdurmaktan sorumludur.
Github
******
Github [17]_ temel proje yönetim ve geliştirme alanımızdır. Birçok geliştiricinin alışık olduğu bu ortam, katkıcıların kolayca dahil olmalarına olanak vermektedir. Açık kaynaklı yazılım projeleri geliştirme teamüllerine uygun bir ortamdır. Git sürüm yönetim sistemini kullanmaktadır. Geliştirici ve kullanıcı topluluğun teknik tartışmaları, geri bildirimleri Github’ın sağladığı ilgii araçlarla yapılacaktır.

Continuous Integration  & Continuous Delivery
*********************************************
Uygulama kaynak kodu ve/veya sistem/ortam ayarları değişiklikleri üzerine, uygulamanın test edilmesi, belirlenen ortamlarda kurulum ve yayınlanma işlerinin otomatik şekilde yapılması, elde edilen sonuçların geliştiricilerle paylaşılması ve raporlanması, geliştirme süreçlerini kolaylaştırmakta, hızlandırmakta, problemlerin kaynaklarını tespit etmeye yardımcı olmaktadır.

Projede, bu amaçla Buildbot [18]_ kullanılacaktır. Buildbot ile üretilen her türlü sonuç, log, rapor projede ilgili taraflara çeşitli kanallardan iletilecektir.

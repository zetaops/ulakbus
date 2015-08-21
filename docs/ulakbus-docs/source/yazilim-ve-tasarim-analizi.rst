+++++++++++++++++++++++++++++++++++
Yazılım Geliştirme ve Test Döngüsü
+++++++++++++++++++++++++++++++++++


Yazılım Geliştirme Modeli
%%%%%%%%%%%%%%%%%%%%%%%%%
Yazılım geliştirme modeli döngüsel artımlı (iterative and incremental) modele bağlı XP [1]_ olacaktır.

Geliştirme ve Test Döngüsü
**************************
Extreme Programming modeline uygun şekilde 3 haftalık dönemlerde küçük sürüm planı yapılacak ve yazılım geliştirme ve test döngüsü bu sürüm planına bağlı olarak ilerleyecektir.

Sürüm planına dahil edilen işler (issue) geliştiriciler tarafından uygun bir branchte çözülecektir. Geliştiriciler, geliştirme faaliyetleri boyunca aşağıda detayları belirtilen otomatik ve manuel testleri build aşamasından önce uygulayacaklar, ancak bu testlerden geçen kaynak kod sonraki aşamaya geçebilecektir. Kurulum ve yayınlama aşamasında ise bu aşamanın testleri yapılacak ve sonuçlar geliştiricilere bildirilecektir. Ayrıca geliştirilen özelliğe göre kabul testleri de bu aşamada yapılacaktır. Bu geliştirme döngüsü 3 hafta boyunca artımlı şekilde ilerleyecektir.

Bu 3 haftanın sonunda ise sürüm adayı (release candidate) çıkartılacak ve bunun üzerinde kabul testleri ve önceden hazırlanmış test senaryoları, kullanılabilirlik, performans, güvenlik gibi testler yapılacaktır. Bu testlerin kabul sınırları içinde geçilmesi halinde sürüm ortaya çıkartılacaktır.

Bunlara ek olarak her gece, gecelik derlenmiş kod (nightly builds) yayınlanacak, yazılımın tüm bileşenlerine ait tüm otomatik testler bu aşamada gerçekleşecektir.

Sürüm Planı
-----------
Sürüm planı 3 hafta geliştirme + 1 hafta kabul test süreçleri şeklinde planlanır. 7 ay boyunca toplam 7 sürüm çıkarılacaktır. Sürüm planı ihtiyaç analizi isterleri ve YTA belgesi ışığında yeni özelliklerin planlanması, önceki sürümden kalan hataların kapatılması, topluluk geri bildirimlerinden seçilen işlerin (issues) tamamlanması hedefleriyle yapılır.

Depolar
-------
Her bileşen kendi deposunda yaşam döngüsüne devam eder. Birbirlerini etkileyen issuelar için referans verilir. Başlıca geliştirme depolarımız:
**-SpiffWorkFlow:** İş akışı kütüphanesi geliştirme deposudur. Orjinalden fork edilmiştir.

**-Pyoko:** Pyoko Riak/Solr ORM geliştirme deposudur. Zetaops tarafından geliştiriliyor.

**-Zengine:** Zengine Framework geliştirme deposudur. Zetaops tarafından geliştiriliyor.

**-Zaerp (Ulakbus):** Ana uygulama backend geliştirme deposudur. Zetaops tarafından geliştiriliyor.

**-Zaerp-UI (Ulakbus-ui):** Ana uygulama frontend geliştirme deposudur. Zetaops tarafından geliştiriliyor.

**-ZCloud:** Bulut araçları geliştirme deposudur. Zetaops tarafından geliştiriliyor.

Yardımcı kütüphaneler ile fork edilmiş kütüphaneler haricindeki depo isimleri, daha sonra Ulakbim tarafından verilecek isimlerle değiştirilecektir.

Topluluk
--------
Roller
******
**Geliştiriciler**
Depolara kod katkısında bulunacak topluluk üyeleridir. `Geliştirici Rehberleri <https://github.com/zetaops/ulakbus/tree/master/docs/development>`_ ve Git Workflow[**]  Belgesinde açıklanan akışa uygun şekilde geliştirme faaliyetlerine katılırlar.

**Beta Test Edicileri**
Patch ve Minor sürümleri test ederek geri bildirimlerde bulunarak geliştirme faaliyetine katkıda bulunurlar.
**Analiz Uzmanları**
Yüksek Öğrenim Kanunu, Akademik Birimlerin Yönetmelikleri, akademinin yerleşik teammülerini bilen, projenin kapsamına detaylarıyla hakim topluluk üyeleridir. Topluluğun talep ettiği yeni özellikler, iş akışlarının değiştirilmesi, kanun ve yönetmeliklerdeki değişikliklerin projeyi nasıl etkileyeceği gibi konularda tavsiyelerde bulunurlar.
**Topluluk Moderatörleri**
Topluluğun tartışmalarını kolaylaştırmak, konu başlıklarını bağlantılandırmak, tartışmaların gidişatını sorularla belirli hedeflere yönlendirmek gibi görevleri olan topluluk üyeleridir.

Geliştirici ve Katkıcı Rehberleri
*********************************
- **Geliştirme Ortamı Kurulum Rehberi**

- **UI Geliştirci Rehberi**

- **Zaerp Geliştirici Rehberi**

- **Workflow ve Spiff WF Rehberi**

- **Zato ve Servis Yazma Rehberi**

- **Git Workflow**

Test Döngüsünün Amaçları
------------------------

- Yazılım geliştirme döngüsünün denetlenebilir, kolay yönetilebilir ve ölçülebilir hale gelmesini sağlamak,
- Problemleri somutlayarak, çok sayıda yazılımcının daha kolay işbirliği yapabilmesine yardımcı olmak,
- Her bir yazılım parçasını çok yönlü şekilde zamanında test ederek, geliştirme döngüsünün sonraki aşamalarına en az hata ile devam etmek,
- Bir bileşende yapılan geliştirmenin diğer bileşenleri nasıl etkilediğini zamanında görebilmek,
- Kod kalitesini arttırmak,
- Kod yazım desenleri açısından bütünlük sağlamak ve okunabilirliği arttırmak,
- Kurulum sırasında yazılım bileşenleri ve birbirlerine olan bağımlılıkları doğrulamak,
- Yazılımın farklı platformlarda ve farklı ortam değişkenleriyle başarılı bir şekilde kurularak, beklenen şekilde çalıştığından emin olmak,
- Yazılımın beklenen şekilde çalışmasının ardından, önceden belirlenmiş çeşitli yük testleri altında aynı şekilde davranmaya devam ettiğinden emin olmak,
- Ortaya çıkan ürünün, ister belgesindeki işlevleri karşılayıp kaşılamadığını doğrulamak,
- Ürünün kullanım kolaylığı, kullanıcı deneyimi, performans açısından tatmin edici ve standartları karşıladığından emin olmaktır.



Sürüm Planına Bağlı Geliştirme Döngüsü Testleri
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

Eşli Gözden Geçirme (Peer Code Review)
**************************************

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

Arkauç Testleri
---------------

Bileşen (Birim) Testleri
************************
Sistemin arkaucunu oluşturan bileşenlerin tümü py.test test frameworkü kullanılarak test edilecektir. Birim testleri, kodun en az %60’ını kapsayacaktır (code coverage). Uygulamayı oluşturan tüm bileşenlerin birim testleri, kendi ana dizinleri altında “tests” dizininde tutulur. “py.test” komutu, proje ana dizini altında çalıştırıldığında, ismi “test” ile başlayan tüm Python dosyalarını tek tek tarayıp, içlerinde yine ismi “test” ile başlayan metodları çalıştırır. Örnek bir birim test aşağıda görülebilir.

+--------------------------------------------------------------+
| from tests.data.test_data import data                        |
|                                                              |
| from tests.data.test_model import Student                    |
|                                                              |
|                                                              |
| def test_model_to_json_compact():                            |
|                                                              |
|  st = Student(\*\*data)                                      |
|                                                              |
|  st.join_date = data['join_date']                            |
|                                                              |
|  st.AuthInfo(\*\*data['AuthInfo'])                           |
|                                                              |
|  for lct_data in data['Lectures']:                           |
|                                                              |
|    lecture = st.Lectures(\*\*lct_data)                       |
|                                                              |
|    lecture.ModelInListModel(\*\*lct_data['ModelInListModel'])|
|                                                              |
|    for atd in lct_data['Attendance']:                        |
|                                                              |
|        lecture.Attendance(\*\*atd)                           |
|                                                              |
|     for exam in lct_data['Exams']:                           |
|                                                              |
|        lecture.Exams(\*\*exam)                               |
|                                                              |
|                                                              |
|  clean_value  = st.clean_value()                             |
|                                                              |
|                                                              |
|  assert data == clean_value                                  |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
|                                                              |
+--------------------------------------------------------------+

**Örnek birim testi 1**
Py.test, standard “assert” ifadesinin testin başarılı olup olmadığının kontrolü için kullanır. Bu sayede testlerin hazırlanması, yeni geliştiriciler için neredeyse hiçbir ek öğrenme süreci gerektirmez.

Yukarıdaki test, benchmark eklentisiyle birlikte aşağıdaki gibi bir çıktı verecektir.

+---------------------------------------------------------------------------------------+
|================== test session starts ==================                              |
|                                                                                       |
|rootdir: /home/whogirl/Works/pyoko, inifile:                                           |
|                                                                                       |
|plugins: benchmark                                                                     |
|                                                                                       |
|collected 4 items                                                                      |
|                                                                                       |
|tests/test_model_to_json.py                                                            |
|                                                                                       |
|--- benchmark: 1 tests, min 5 rounds (of min 25.00us), 1.00s max time,                 |
|                                                                                       |
|Name (time in us)            Min         Max      Mean     StdDev  Rounds  Iterations  |
|                                                                                       |
|                                                                                       |
|                                                                                       |
|test_model_to_json        214.0999  41221.8571  319.0611  1019.8894    1629     1      |
|                                                                                       |
|                                                                                       |
|                                                                                       |
|                                                                                       |
|================== 1 passed in 1 .37 seconds ==================                        |
+---------------------------------------------------------------------------------------+

Test frameworkünün, kod kapsam analiziyle birlikte çalıştırılması sonucu aşağıdaki gibi bir çıktı elde edilecektir. Bu örnekte pyoko modülünün test kapsam oranı %58 olarak görünmektedir.

+-----------------------------------------------------------------------+
|                                                                       |
|py.test --cov pyoko                                                    |
|                                                                       |
|================== test session starts ==================              |
|                                                                       |
|platform darwin -- Python 2.7.6 -- py-1.4.27 -- pytest-2.7.0           |
|                                                                       |
|rootdir: /home/whogirl/Works/pyoko/pyoko, inifile:                     |
|                                                                       |
|plugins: cov                                                           |
|                                                                       |
|collected 4 items                                                      |
|                                                                       |
|                                                                       |
|pyoko ....                                                             |
|                                                                       |
|                                                                       |
|coverage: platform darwin, python 2.7.6-final-0                        |
|                                                                       |
+----------------------------+--------+-------+-------------------------+
|                            |        |       |                         |
|Name                        | Stmts  | Miss  |Cover                    |
|                            |        |       |                         |
|----------------------------|--------|-------|-------------------------|
|                            |        |       |                         |
|pyoko/__init__              |      1 |     0 |  100%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/db/base               |    165 |   118 |   28%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/db/connection         |      5 |     0 |  100%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/db/schema_update      |     20 |    10 |   50%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/db/solr_schema_fields |      1 |     1 |    0%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/exceptions            |     11 |     0 |  100%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/field                 |     46 |     8 |   83%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/lib/__init__          |      1 |     0 |  100%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/lib/py2map            |     22 |    17 |   23%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/lib/utils             |     16 |     5 |   69%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/model                 |    106 |     7 |   93%                   |
+----------------------------+--------+-------+-------------------------+
|pyoko/settings              |      2 |     0 |  100%                   |
+----------------------------+--------+-------+-------------------------+
|TOTAL                       |    397 |   166 |   58%                   |
+----------------------------+--------+-------+-------------------------+
| ================== 4 passed in 3.14 seconds   ==================      |
|                                                                       |
+-----------------------------------------------------------------------+

HİTAP gibi test ortamı sunmayan üçüncü parti servislerle veri alışverişi yapan modüllerin testleri, harici servisin istek / yanıt setlerini mimik eden Wiremock [2]_ gibi bir simulatöre karşı yapılacaktır. Bu amaçla üretim ortamında servise gönderilen ve alınan veri trafiği kaydedilecek ve simulatör bu verilerle “eğitilecektir”.

**Pyoko**

Veri erişim katmanı (DAL) olarak görev yapacak olan Pyoko kütüphanesi için yazılacak birim testleri, veri doğruluğu ve API işlevlerine ek olarak çalışma hızı ve bellek kullanımı gibi kriterleri de göz önünde bulunduracaktır.

**SpiffWorkflow Engine**

Üçüncü parti bir kütüphane olarak projeye eklenmiş olan SpiffWorkflow’un geliştirilmesi ve bakımı uygulamanın ihtiyaçları doğrultusunda sürdürülecektir. Buna ek olarak,
BPMN iş akışlarının doğruluğunun devamlı olarak sınanabilmesi için entegre bir test kaydetme ve çalıştırma modülü geliştirilecektir.

İş Akışı (Workflow) Testleri
****************************
Sistemin tüm işlevlerinin üzerine inşa edileceği BPMN iş akışları, verilen girdilerle beklenen davranışı gösterip göstermediğine karşı test edilecektirler. Böylece iş
akışları üzerinde yapılacak güncellemelerin, amaçlanan dışında yan etkilere neden olmadığından emin olunması sağlanacaktır.

Benchmark Testleri
******************
İş akışı motoru, Pyoko gibi görev kritik modüllerin performansı  pytest-benchmark eklentisi kullanılarak devamlı olarak ölçülüp kaydedilerek bu modüllerin performanslarındaki zamana bağlı değişim takip edilecek ve olası gerilemeler önlenecektir.

Servis Testleri
***************
Uygulamanın birçok işlevi Zato ESB üzerinde çalıştırılacak mikro servisler üzerinden sunulacaktır. Bu servislerin işlevselliği ve API uyumluluğu zato-apitest frameworkü ile yazılacak testler ile sınanacaktır.

Kural Motoru (Rule Engine) Testleri
***********************************
Uygulamanın iş mantığının önemli bir kısmını oluşturan kural setleri, belirli girdilerle beklenen çıktıları verip vermediklerine karşı denetelenmelidir.. Bu amaçla kural setleri standart birim testleri içerisinde kural motoru ile işletilerek beklenen çıktıyla eşleştirilecektir.

Kurulum ve Yayınlama Aşaması Testleri
-------------------------------------
Kurulum ve Yayınlama (Build Release) aşamasında Buildbot aracılığı ile
kurulum ve kütüphane bağımlılık testleri
uygulamanın tüm bileşenlerine ait birim testleri
entegrasyon testleri uygulanacaktır.

Test Sunucuları ve Geliştirme Test Döngüsü
******************************************
Her iş (issue) kendi geliştirme branchinde minik commitler ile geliştirilir. Bu branchlere yapılan pushlar buildbot u tetikleyip, kurulum ve yayınlama aşamasını başlatır. Bu branchten elde edilen kod diğer kütüphaneler ile birlikte biraraya getirilip kurulum işlemi yapılır ve gerekli testler çalıştırılır. Testleri geçen kaynak kod ve uygulama, geliştiricinin erişebileceği bir porttan yayınlanır.

branch issue/58 → push → buildbot run tests → branch deployed at port 9091
branch issue/59 → push → buildbot run tests → branch deployed at port 9092
branch issue/60 → push → buildbot run tests → branch deployed at port 9010

Sonuca kavuşturulan işler (issues) elle master branch ile birleştirilir (merge). Masterdaki bu değişiklik geliştirme aşamasındaki gibi buildbot u tetikler. Kurulum ve yayınlama işlemi bu branche karşı yapılır. Yayınlama sabit bir porttan yapılır (8080).

Bunun yanısıra gecelik derlenmiş kod (nightly builds) da master branchlerden gerkçekleşir ve aynı portta yayınlanır.

master → manual merge → buildbot run tests → master deployed at 8080
master → automatic buildbot nightly build (backend + UI ) → master deployed at 8080

Master Merge ve Nightly Builds işlemleri sırasında şu bileşenler biraraya getirilir:
1. final git master repo status
2. application artefacts (xml files, json files, binary files, zip files, config files, certs)
3. db schema migration file

Yayına Alma (Production)
************************
Sürüm adayı haline gelen master branchte bulunan kaynak kod, aşağıda detaylı şekilde anlatılan sürüm öncesi kabul testlerinden geçer. Bu testlerin başarılı olması halinde, semantik sürümlendirme sistemine [3]_ göre etiketlenir (tagging).

Semantik sürümlendirme sistemine göre kullanılacak desen MAJOR.MINOR.PATCH şeklindedir. Buna göre 3 haftalık küçük sürümler MINOR, gündelik çözülen işler PATCH, önceden belirlenmiş hedefleri kapsayan fazların sonunda ise MAJOR değerleri arttırılır.

MINOR sürümler çıktıkça, buildbot taglenmiş sürümdeki depoları production ortamında yayına alır. Gerekli dosyaları kopyalar ve veritabanı şemalarını yeni sürümlere göç ettirir.

Kullanıcı Arayüzü Testleri
--------------------------
Kullanıcı Arayüzü AngularJS ile Model-View-Controller (MVC) yapısı ile programlanacaktır. Modül yapısı aşağıdaki örnekte olduğu gibidir:

+-----------------------------------------------------------------------------------------------+
|                                                                                               |
| app/                                                                                          |
|                                                                                               |
|     dashboard/                                                                                |
|                                                                                               |
|       dashboard.html (template)                                                               |
|                                                                                               |
|       dashboard.js (Controller ve Model tanımlarının olduğu dosya)                            |
|                                                                                               |
|       dashboard.test.js (Testlerin yazıldığı dosya)                                           |
|                                                                                               |
|       … (diğer modüller)                                                                      |
|                                                                                               |
|       app.css (stil dosyası)                                                                  |
|                                                                                               |
|       app.js (Uygulamanın tanımlandığı yapılandırıldığı dosya)                                |
|                                                                                               |
|    karma.conf.js (testlerin çalışma zamanı yapılandırmalarını içeren dosya)                   |
|                                                                                               |
|    e2e-tests/                                                                                 |
|                                                                                               |
|       #protractor.conf.js (e2e testlerini çalıştıran protractor yapılandırma dosyası)         |
|       #scenarios.js (e2e test senaryolarının bulunduğu dosya)                                 |
|                                                                                               |
+-----------------------------------------------------------------------------------------------+

Bileşen (Birim) Testleri
************************
Uygulamada \*.test.js dosyaları modüllerin Unit testlerinin barındığı dosyalardır. Unit testler Jasmine test uygulama çatısı kullanılarak yazılır.
Uygulamanın Giriş (Login) modülü için yazılmış bir örnek aşağıdaki gibidir:

+------------------------------------------------------------------+
|describe('zaerp.login module', function () {                      |
|                                                                  |
|   beforeEach(module('zaerp.login'));                             |
|                                                                  |
|   describe('login controller', function () {                     |
|                                                                  |
|         it('should have a login controller', inject(function (){ |
|                                                                  |
| expect('zaerp.login.LoginCtrl').toBeDefined();                   |
|                                                                  |
|     }));                                                         |
|                                                                  |
|   });                                                            |
|                                                                  |
| });                                                              |
+------------------------------------------------------------------+

Bu test örneğinde “login controller”ının tanımlanmış olması gerekliliği test edilmektedir.
Kullanıcı arayüzü unit testleri karma test yürütücüsü (test runner) ile çalıştırılır. Bunun için yukarıda açıkladığımız yapıda da görüleceği gibi “karma.conf.js” ismiyle bir yapılandırma dosyası bulunmaktadır. Karma yapılandırma örneği aşağıdaki gibidir:

+-----------------------------------------------------------------------------+
|module.exports = function (config) {                                         |
|                                                                             |
|    config.set({                                                             |
|                                                                             |
|        basePath: './',                                                      |
|                                                                             |
|         files: [                                                            |
|                                                                             |
|            'app/bower_components/angular/angular.js',                       |
|                                                                             |
|            'app/bower_components/angular-route/angular-route.js',           |
|                                                                             |
|            'app/bower_components/angular-mocks/angular-mocks.js',           |
|                                                                             |
|            'app/app.js',                                                    |
|                                                                             |
|            'app/components/\*\*/\*.js',                                     |
|                                                                             |
|            'app/login/\*.js',                                               |
|                                                                             |
|        ],                                                                   |
|                                                                             |
|        autoWatch: true,                                                     |
|                                                                             |
|        frameworks: ['jasmine'],                                             |
|                                                                             |
|        browsers: ['ChromeCanary'],                                          |
|                                                                             |
|        plugins: [                                                           |
|                                                                             |
|            'karma-chrome-launcher',                                         |
|                                                                             |
|            'karma-firefox-launcher',                                        |
|                                                                             |
|            'karma-jasmine',                                                 |
|                                                                             |
|            'karma-junit-reporter'                                           |
|                                                                             |
|        ],                                                                   |
|                                                                             |
|        junitReporter: {                                                     |
|                                                                             |
|            outputFile: 'test_out/unit.xml',                                 |
|                                                                             |
|            suite: 'unit'                                                    |
|                                                                             |
|        }                                                                    |
|                                                                             |
|    });                                                                      |
|                                                                             |
|};                                                                           |
+-----------------------------------------------------------------------------+

Bu yapılandırmada test dosyalarının hangileri olduğu ve testlerin çalışması için uygulama bağımlılıkları (dependencies) “files” anahtarında, hangi test uygulama çatısı kullanılacağı “frameworks” anahtarında, hangi tarayıcının kullanılacağı “browsers” anahtarında ve eklentiler “plugins” anahtarında belirtilmektedir.

Unit testler nodejs kullanılarak uygulama kök dizininde “npm test” komutuyla çalıştırılır. Örnek bir test çıktısı aşağıdaki gibidir:

INFO [watcher]: Changed file "zetaops/ng-zaerp/app/login/login_test.js".
Chrome 45.0.2412 (Mac OS X 10.10.3): Executed 8 of 8 SUCCESS (0.409 secs / 0.063 secs)

Bu çıktıdan 8 test senaryosunun başarıyla geçtiği görülmektedir (Executed 8 of 8 SUCCESS (0.409 secs / 0.063 secs)).

Birim testlerinin kodun ne kadarını kapsadığı yine karma ile incelenecektir. Karma testler çalıştıktan sonra coverage/ dizini altında bir html dosyası oluşturarak kod kapsama oranını yayınlar. Örnek html çıktı sayfası şu şekildedir:

.. image:: _static/codecoverage.png
   :scale: 100 %
   :align: center


Kabul Testleri
**************
Kabul testleri e2e-tests dizini altındaki “scenarios.js” dosyasına yazılır. Testler Jasmine test uygulama çatısı ile yazılacaktır. Örnek bir test senaryosu aşağıdaki gibidir:

+------------------------------------------------------------------------------+
|describe('dashboard', function () {                                           |
|                                                                              |
|       beforeEach(function () {                                               |
|                                                                              |
|              browser.get('index.html#/dashboard');                           |
|                                                                              |
|       });                                                                    |
|                                                                              |
|       it('should redirect to login if not logged in', function (){           |
|                                                                              |
|                expect(element.all(by.css('[ng-view] h1')).first().getText()).|
|                                                                              |
|                     toMatch(/Zaerp Login Form/);                             |
|                                                                              |
|        });                                                                   |
|                                                                              |
|});                                                                           |
+------------------------------------------------------------------------------+

Yukarıdaki örnekte tarayıcı uygulamanın “dashboard” sayfasını çağırmakta eğer giriş yapılmamışsa “login” sayfasına yönlendirmesi beklenmektedir.

Bu testler Protractor ile çalıştırılır. Protractor, Selenium web-driver’larını angularJS ile kullanmak için özelleştirmeler barındıran bir çözümdür. Örnek yapılandırma dosyası aşağıdaki gibidir:

+--------------------------------------------------------------------+
|exports.config = {                                                  |
|                                                                    |
|   allScriptsTimeout: 11000,                                        |
|                                                                    |
|   specs: [                                                         |
|                                                                    |
|      '*.js'                                                        |
|                                                                    |
|   ],                                                               |
|                                                                    |
|   capabilities: {                                                  |
|                                                                    |
|     'browserName': 'chrome'                                        |
|                                                                    |
|   },                                                               |
|                                                                    |
|   baseUrl: 'http://localhost:8000/',                               |
|                                                                    |
|   framework: 'jasmine',                                            |
|                                                                    |
|   jasmineNodeOpts: {                                               |
|                                                                    |
|   defaultTimeoutInterval: 30000                                    |
|                                                                    |
|  }                                                                 |
|                                                                    |
|};                                                                  |
+--------------------------------------------------------------------+

Bu yapılandırma dosyasında testlerin çalıştırılacağı tarayıcı (browserName), url (baseUrl), uygulama çatısı (framework) timeout süreleri gibi özellikler yapılandırılır. Kabul testleri kök dizinde “protractor e2e-tests/protractor.conf.js” komutu ile çalıştırılır.

Manuel Testler
**************
Tarayıcılara has hatalar, görsel düzenlemeler ve diğer otomatik olarak test edilemeyen arayüz özellikleri ve fonksiyonları manuel olarak test edilecektir.

Sürüm Öncesi Kabul Testleri
%%%%%%%%%%%%%%%%%%%%%%%%%%%

Test Senaryoları
****************

Ihtiyaç analiz belgelerinde belirtilen kullanıcı senaryolarına uygun şekilde test senaryoları yazılacaktır. Test senaryolarının amacı, ihtiyaç analizinde ortaya çıkan gereksinimlerin, geliştirme faaliyeti sonucu ortaya çıkan ürün ile karşılanıp karşılanmadığıdır.

Sürüm aşamasında önceden yazılmış test senaryoları, kullanıcılar tarafından manuel şekilde uygulanır ve sonuçlar raporlanır. Bazı test senaryoları otomatik olarak da gerçeklenebilirler.

Bizim uygulamamızda test senaryoları bir veya birden çok iş akışından (workflow) oluşan eylemler dizisi şeklinde olacaktır. Birden çok aktör ve ön koşulu içinde barındıran, problemi yeterli karmaşıklık düzeyine getirecek belirli sayıdaki öğrencinin ders seçimi ve sonuçlarının web sitelerinde yayınlanması veya öğrenciler için ders programının hazırlanması gibi..

Kullanılabilirlik Testi
***********************

Uygulama ekranları, uluslararası kabul görmüş kullanılabilirlik ilkeleri (w3c) ve KAMİS (Kamu Internet Siteleri Rehberi)'nin temel aldığı TS EN ISO 9241-151 (İnsan-Sistem Etkileşiminin Ergonomisi Standartları), WCAG ve ISO/IEC 40500:2012 (Web İçeriği Kullanılabilirlik Standartları ve Kriteri) standartlarında uygunluğu test edilecektir.

Bu amaçla genel bir kontrol listesi (checklist) hazırlanmıştır:

**Genel Görünüm**

      - Klavye kısayollarıyla gezinmek mümkün mü?

      - Klavye kısayollarıyla gezinmek kolay mı?

      - Sayfalar otomatik olarak yenilenmemeli

      - Website iletişim bilgileri, referansları uygun bir alanda mı?

      - Servis/hizmet/uygulama bilgilerine kolayca erişiliyor mu?

      - Görme engelliler için erişilebilirlik düzenlenmiş mi?

      - Grid sistem kullanılmış mı?

      - Klavye kullanımı sitedeki tüm işlemleri kapsıyor mu?

      - Kullanıcılara içerikleri okuyabilmeleri için yeterli zaman verililyor mu?

      - Hukuki ya da mali sonuçları olan işlemlerde kullanıcının hata yapma olasılığı azaltılmalıdır.

**Anasayfa**

      - Amacı kolay anlatıyor mu?

      - Yapmak istediği işleme kolay ulaşılıyor mu?

      - Sayfa görünümü pozitif bir intiba bırakıyor mu?

      - Giriş yapan kullanıcı ismi yer alıyor mu?

      - Büyük değişiklikler ana sayfadan duyuruluyor mu?

      - Konum ve iletişim bilgileri yer alıyor mu?

      - Lisans, sözleşme gibi statik sayfalara linkler var mı?

      - Sayfadaki imajlar ve/veya videolar amaçla alakalı mı?

      - Site hem www alt alanadıyla hem alt alanadı olmadan erişilebilir mi?

      - Sitede yapılacak temel işlemler ana sayfada yer alıyor mu?


**Yönetim Paneli**

      - İçerikler kullanıcı rolüyle ilgili mi?

      - Uyarılar zamanında ve etkili şekilde gösteriliyor mu?

      - Uyarılar öncelik ve önem derecelerine göre renklendirilmiş mi?

      - Birden fazla role sahip kullanıcılar için roller arası geçişi sağlayan bir buton var mı?

**Erişilebilirlik**

      - İmajların “alt” özellikleri kullanılmış mı?

      - İçerik stil dosyası (css) olmadan da okunabilir mi?

      - Bağlantılar, butonlar ve seçim kutuları kolayca tıklanabilir mi?

      - örnek erişilebilirlik testi: http://achecker.ca/checker/index.php

**Site İçi Yönlendirme**

      - Önemli bağlantılar sayfanın hareketli öğelerinde olmamalı

      - Linkler alfabetik olarak sıralanmamalı, gruplanmalı

      - Kullanıcı sitede hangi sayfada olduğunu kolayca farkedebilmeli

      - Yönlendirme bağlantıları her sayfada görünür mü?

      - Bağlantılar açıklayıcı mı?

      - Title’da site ve o sayfanın kısa bir açıklaması var mı?

      - Site url’si akılda kalıcı mı?

**Arama**

      - Bir arama kutusu var mı?

      - Arama kutusu her sayfada görünür mü?

      - Arama kutusu yeterince geniş mi?

      - Arama sonuçları kategorilendiriliyor mu?

**Bağlantılar**

      - Önemli komutlar bağlantı yerine buton olarak gösterilmeli, örn: kaydet gibi

      - Linkler kolayca farkedilir mi?

      - Kırık (erişilemeyen) link olmamalı

**Şablon**

      - Öğünemli içerikler öncelikli olarak gösteriliyor mu?

      - Site şablonu farklı ekran boyutlarında ölçekleniyor mu?

      - Birbiriyle alakalı bilgiler gruplandırılmış mı?

      - Tüm sayfalarda tutarlı mı?

      - Sayfalar çok sıkışık olmamalı

**Formlar**

      - Formlar kolay doldurulabilir mi?

      - Form alanlarının açıklamaları var mı?

      - Alanların alması gereken değerler kullanıcıya gösteriliyor mu?

      - Çok uzun açılır menüden kaçınılmış mı?

      - Form alanlarının isimleri açık ve anlaşılır mı?

      - Form onay butonu var mı?

      - Hata mesajları ilgili form alanının yanında yer alıyor mu?

      - Birden fazla adımdan oluşan formlar için hangi adımda olduğu anlaşılıyor mu?

**İçerik**

      - Metin ve arkaplan rengi arasında yeterli derecede kontrast var mı?

      - İçerik gözle taranabiliyor mu?

      - İçerik temiz bir dille yazılmış mı?

      - İletişim bilgileri açık şekilde yazılmış mı?

      - İçerik kullanışlı ve güncel mi?

      - Dil kurallarına uyuyor mu?

      - İçerik sıralaması anlamlı mı?

      - İçeriklerin ayırt edilebilmesi ya da doğru anlaşılabilmesi için renk kullanımına dikkat edilmiş mi?

      - Hareketli içerikler kullanıcılar tarafından kontrol edilebiliyor mu?

      - Tekrarlı içerikler pas geçilebiliyor mu?

      - Metin öğeleri yeniden boyutlandırılabilir mi?



Her ekran kontrol listesi formu ile birlikte açılır. Test kullanıcıları bu formu doldurup kaydederler. Sonuçlar ilgili servise raporlanır.

Performans Testleri
*******************
Load Tests
----------
Yük testleri, uygulamanın belirli parçalarının yoğun trafik altındaki davranışlarını ölçmek amacıyla yapılır. Yayınlama aşamasında önceden belirlenen yük değerleri ile otomatik şekilde gerçekleştirilecektir. Bu amaçla geçici sanal makineler oluşturulacak, testler bu makineler üzerinde gerçekleştirilecektir. Temel test aracımız Tsung [4]_ olarak seçilmiştir. Tsung birçok farklı protokolde detaylı şekilde özelleştirilebilen requestler hazırlamaya olanak vermektedir.

Ağ Kullanımı ve Web Sayfa Başarımı
**********************************
Ağ Kullanımı uygulama modüllerinin gerektiğinde çağırılacak şekilde düzenlenmesi (lazy load), statik dosyaların (javascript, css, imaj ve diğer dosyalar) optimize ve minimize edilmesi gibi konuları içerir. Bu süre çevrimiçi araçlar ve tarayıcılar kullanılarak test edilir.

Render Performansı
******************
Sayfa render süresi kod tekrarı, optimizasyonu, DOM kullanımı gibi bilinen gerekliliklere göre kısalmaktadır. Sayfa bileşenlerinin yüklenme süresinden sonra gereken tüm fonksiyonların çalıştırılması ve stillerin uygulanması süresi render performansıdır. Tarayıcının yeteneklerine bağımlı olsa da belirlenecek minimum değerin altında olmamalıdır. Selenium ile test edilecektir.

Güvenlik Testleri
*****************
Uygulamanın güvenlik test ve kontrolleri için Open Web Application Security Project (OWASP) [5]_ topluluğunun yayınladığı test rehberinde [6]_ yer alan testlerin bazıları kullanılacaktır. 11 konu başlığı altında toplanan testlerin uygulamamız için uygun olanları seçilerek her sürüm öncesi kabul testleri aşamasında uygulanacaktır.

Kontroller Sistem Hakkında Bilgi Toplama, Yapılandırma ve Yayınlama, Kimlik Yönetimi, Kimlik Doğrulama ve Yetkilendirme, Oturum Yönetimi, Girdi Geçerliliği, Hata Ayıklama, Şifreleme, İş Mantığı, İstemci Tarafı Testleri başlıkları altında yapılacaktır.

Yapılacak testler ayrıca ISO 27002 bilgi güvenliği standartlarında belirlenen kriterlerin tamamlanması için kuruma destek olacaktır.


.. [1]  http://www.extremeprogramming.org
.. [2]  http://wiremock.org/
.. [3]  http://semver.org/
.. [4]  http://tsung.erlang-projects.org/
.. [5]  https://www.owasp.org/
.. [6]  https://www.owasp.org/images/5/52/OWASP_Testing_Guide_v4.pdf
.. [7]  https://zato.io/docs/intro/esb-soa-tr.html
.. [8]  https://coreos.com/docs/running-coreos/platforms/openstack/
.. [9]  http://docs.openstack.org/image-guide/content/ubuntu-image.html
.. [10]  http://www.basho.com/riak
.. [11]  http://basho.com/riak-cloud-storage/
.. [12]  http://redis.io/
.. [13]  https://zato.io/docs/intro/esb-soa-tr.html
.. [14]  http://www.haproxy.org/
.. [15]  https://www.docker.com/
.. [16] https://www.consul.io/
.. [17] https://github.com/
.. [18] http://buildbot.net/
.. [19] https://www.elastic.co/products/logstash
.. [20] https://www.elastic.co/products/kibana
.. [21] https://www.elastic.co/products/elasticsearch
.. [22] http://achecker.ca/checker/index.php http://www.w3.org/standards/webdesign/accessibility   http://www.w3.org/WAI/ http://www.w3.org/TR/WCAG10/full-checklist.html
.. [23] http://ngmodules.org/ http://quantumui.org/ http://usablica.github.io/intro.js/
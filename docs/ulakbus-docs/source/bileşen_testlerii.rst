++++++++++++++++++++++++
Bileşen (Birim) Testleri
++++++++++++++++++++++++

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

++++++++++++++
Kabul Testleri
++++++++++++++

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

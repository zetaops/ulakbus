++++++++++++++++++++++++++
Kullanıcı Arayüzü Testleri
++++++++++++++++++++++++++

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

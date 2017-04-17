++++++++++++++++++++++++
Bileşen (Birim) Testleri
++++++++++++++++++++++++

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

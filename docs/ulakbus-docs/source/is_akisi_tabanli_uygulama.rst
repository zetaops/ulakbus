+++++++++++++++++++++++++
İş Akışı Tabanlı Uygulama
+++++++++++++++++++++++++

İş Akışı (Workflow) Tabanlı Uygulumalar, iş süreçlerini yeterince küçük adımlara bölerek, iş akışlarının aktörlerini ve her bir adımda işlenecek veriyi net bir şekilde tanımlayarak kolay yönetilebilirlik ve esneklik sağlarlar. İş süreçlerinin tamamıyla olmasa bile belli oranda otomatikleştirilmesi ve yazılım tarafından işlenebilir olması değişen ihtiyaçları karşılamak için kolaylık sağlamaktadır. Sadece iş akışı şemalarında yapılacak değişikliklerle uygulamaya yön vermek mümkündür.

.. image:: _static/workflows.png
   :scale: 100 %
   :align: center

**Örnek İş Akış Şeması**

İş süreçleri yönetimi için, BPMN2 kural setine uyan Workflow Management yapısı seçilmiştir.   Python dünyasında WorkFlow Management ve BPMN desteği bulunan SpiffWorkFlow kütüphanesi geliştirilmeye açık en uygun aday olduğu için seçilmiştir.

İş süreçlerinin görsel olarak oluşturulması için de Camunda Modeler seçilmiştir.
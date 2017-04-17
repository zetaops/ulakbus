+++++++++++++++++++++++++++++++
Arka Uçta Kullanılan Bileşenler
+++++++++++++++++++++++++++++++

Genel Sistem Akış Şeması
------------------------
.. image:: _static/genelsistemakssemas.png
   :scale: 70 %
   :align: center

Modül / Bileşenlerin Genel Görünümü
-----------------------------------
- zaerp

    -zdispatch

requestleri karsilayip ilgili is akislarina yonlendiren falcon web çatısı dosyalari yer alacaktir

    -bin

çalıştırılabilir uygulamalar. örn: bpmn packager.

	-lib

yardımcı kütüphane ve fonksiyon setleri

	-modules

bazıları kendi alt dizinlerine sahip olan uygulama modulleri.

	-auth

örnek authentication modülü

	-models

		%user.py

		%auth.py

		%employee.py

		%unit.py

	-services

bu dizinde Zato mikro servis dosyaları yer alacaktır.

	-workflows

bu dizinde iş akışı paketleri bpmn dosyaları yer alacaktır

- tests

methodlar, uygulama birimleri ve uygulama geneli icin yazilan unit testleri yer alacaktır

- docs

	-geliştiriciler

		%diagrams

		%api

	-son kullanıcılar

	-sistem yöneticileri

kod, api, kullanici, gelistirici, sistem yoneticisi dokumanlari yer alacaktir.


Uygulamanın veri ve iş mantığının şu ana kadar planlanan yapısını gösteren class diagramlar aşağıda görülebilir.

.. image:: _static/pyoko.png
   :scale: 70 %
   :align: center

.. image:: _static/spiffworkflow.png
   :scale: 70 %
   :align: center

.. image:: _static/entitybasedmodeldiagram.png
   :scale: 100 %
   :align: center

.. image:: _static/genericrequesttoresponseseqdiagram.png
   :scale: 100 %
   :align: center
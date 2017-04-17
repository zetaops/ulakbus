++++++++++++
Log Yönetimi
++++++++++++

Hem uygulama hem de uygulamanın çalışacağı ortam bileşenlerinin her birinden toplanacak loglar, merkezi bir loglama sisteminde toplanacaktır. Sistemin anlık olarak izlenmesi, olağandışı gelişmelere uygun aksiyonlar alınması, uzun vadede geliştirme süreçlerine geribildirim olarak dönmesi amacıyla toplanan kayıtlar analiz edilecektir.

Bu amaçla Logstash [19]_ , Kibana [20]_, Elasticsearch [21]_ üçlüsü kullanılacaktır. Logstash ve Elasticsearch logların toplanması, filtrelenmesi, analiz edilmesi, Kibana ise görselleştirilmesi için kullanılacaktır.

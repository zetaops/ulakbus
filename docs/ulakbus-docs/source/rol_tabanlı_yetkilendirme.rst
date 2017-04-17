+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Rol Tabanlı Yetkilendirme (Rol Based Authorization Control)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Rol ve yetkiler, Akademik ve İdari Birimler (Units), Soyut Roller(Abstract Roles), İş Akışı(WorkFlows), İş Akışı Adımları(WorkFlow Tasks) ve Kullanıcı (User) kavramlarının kesişimleri sonucu ortaya çıkarlar.

Kullanıcıların bir birimde, tanımlanmış herhangi bir role (bölüm sekreteri, öğretim elemanı, öğrenci vb.) dahil olmaları onları belirli workflowların belirli adımları için yetkili olmalarını sağlayacaktır. Örnek verecek olursak:

Birim: Mühendislik Fakültesi Bilgisayar Mühendisliği Bölümü
Soyut Rol: Bölüm Başkanlığı
Kullanıcı: Ayşe Bilgin, Öğretim Üyesi, Prof.
İş Akışı: Ders, Öğretim Elemanı Paylaşımı. Bu iş akışının 2 aktörü vardır. Paylaşımı yapan bölüm sekreteri, bu paylaşıma onay veren bölüm başkanı.
İş Akışı Adımları: İş akışı, yineleyen düzeltme - gözden geçirme ve nihayetinde onay ve ilgililere bildirim adımlarından oluşmaktadır.

Ayşe Bilgin, bölüm başkanı olarak, sadece kendi bölümü ile ilgili olarak bu iş akışının ilgili adımları için otomatik olarak yetkilendirilmiş olacaktır.

Öte yandan Ayşe Bilgin bir başka birimde, geçici olarak, bir rol ile sadece belli görevleri yapmak üzere görevlendirilmiş olsun. Bu durumda Ayşe Bilgin'in yetkileri, ilgili rolün sahip olduğu yetkilerin (iş akışı adımları yetkileri) bir kısmı ile genişletilebilecektir. Bu da ancak ilgili iş akışı adımlarının ilgili birim ve rol ile somutlanmasının yetki olarak tarif edilmesiyle mümkün olabilmektedir.

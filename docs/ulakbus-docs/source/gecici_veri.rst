+++++++++++
Geçici Veri
+++++++++++

Uygulamanın sık kullandığı veriler Redis üzerinde önbelleklenecektir. Bu önbellek verileri işlemci ve veritabanı yükü açısından pahalı işlemlerle hesaplanmış değerleri ve veritabanından sık sık okunan verileri  içerir. Pyoko kütüphanesi üzerinden yapılan doğrudan veri çağrıları (get request) otomatik olarak önbellekleneren veri tabanı üzerindeki sorgu yükü hafifletilecektir.

Önbellekleme haricinde, kullanıcı oturumları da Redis üzerinde tutulacaktır. Kullanıcının o an geçerli yetkileri, oturum boyunca yaptığı işlemlerle ilgili durum bilgileri de yine kullanıcı oturumu içerisinde tutulacaktır.

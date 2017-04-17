++++++++++++++++++++++++++++++++++++++++++
Test Sunucuları ve Geliştirme Test Döngüsü
++++++++++++++++++++++++++++++++++++++++++

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

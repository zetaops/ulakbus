++++++++++++++++++++++++++
Geliştirme ve Test Döngüsü
++++++++++++++++++++++++++


Extreme Programming modeline uygun şekilde 3 haftalık dönemlerde küçük sürüm planı yapılacak ve yazılım geliştirme ve test döngüsü bu sürüm planına bağlı olarak ilerleyecektir.

Sürüm planına dahil edilen işler (issue) geliştiriciler tarafından uygun bir branchte çözülecektir. Geliştiriciler, geliştirme faaliyetleri boyunca aşağıda detayları belirtilen otomatik ve manuel testleri build aşamasından önce uygulayacaklar, ancak bu testlerden geçen kaynak kod sonraki aşamaya geçebilecektir. Kurulum ve yayınlama aşamasında ise bu aşamanın testleri yapılacak ve sonuçlar geliştiricilere bildirilecektir. Ayrıca geliştirilen özelliğe göre kabul testleri de bu aşamada yapılacaktır. Bu geliştirme döngüsü 3 hafta boyunca artımlı şekilde ilerleyecektir.

Bu 3 haftanın sonunda ise sürüm adayı (release candidate) çıkartılacak ve bunun üzerinde kabul testleri ve önceden hazırlanmış test senaryoları, kullanılabilirlik, performans, güvenlik gibi testler yapılacaktır. Bu testlerin kabul sınırları içinde geçilmesi halinde sürüm ortaya çıkartılacaktır.

Bunlara ek olarak her gece, gecelik derlenmiş kod (nightly builds) yayınlanacak, yazılımın tüm bileşenlerine ait tüm otomatik testler bu aşamada gerçekleşecektir.





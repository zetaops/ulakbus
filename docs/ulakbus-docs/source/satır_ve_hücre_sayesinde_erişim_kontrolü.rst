++++++++++++++++++++++++++++++++++++++++++
Satır ve Hücre Seviyesinde Erişim Kontrolü
++++++++++++++++++++++++++++++++++++++++++

Yukarıdaki modellere göre yetkilendirilen kullanıcılar, belirli bir buckettaki kayıtların hangilerine erişebilecekleri ve erişebildikleri bu kayıtların hangi alanlarını görebilecekleri konusunda sınırlandırılacaklardır. Bu sınırlamaların hemen hepsi veri erişim katmanı (pyoko) seviyesinde işletilecektir.


+----------------------------------------------------------------------------------------+
|                                                                                        |
| # Veri modeli tanımlaması                                                              |
|                                                                                        |
| class Student(Model):                                                                  |
|                                                                                        |
| sno = field.String(index=True)                                                         |
|                                                                                        |
| name = field.String(index_as='text_tr')                                                |
|                                                                                        |
| phone = field.String(index=True)                                                       |
|                                                                                        |
|                                                                                        |
|class Meta(object):                                                                     |                                                                                        |                                                                                        |
|    cell_filters = {                                                                    |
|                                                                                        |
|  'can_view_student_phone': ['phone']                                                   |
|                                                                                        |
| }                                                                                      |
|                                                                                        |
|   def row_level_access(self):                                                          |
|                                                                                        |
|       self.objects = self.objects.filter(unit_in=self._context.user['unit']['id'])     |
|                                                                                        |
|# Workflow adımında çağırılan view metodunda veritabanı sorgulaması                     |
|                                                                                        |
|def show_student_list(context):                                                         |
|                                                                                        |
|# context 'session', 'request', 'response', 'permissions', 'user' nesnelerini içerir.   |
|                                                                                        |
|  Student(context).all()                                                                |
+----------------------------------------------------------------------------------------+

Yukarıda öğrenci listesini gösteren örnek view metodunda Student modelindeki tüm kayıtlar istenmesine karşın, erişim katmanı model içerisine tanımlanmış olan satır tabanlı kısıtları işleterek o an giriş yapmış olan personelin, sadece kendi bölümündeki öğrencileri görmesine müsade etmektedir. Benzer şekilde eğer cell_filters süzgeci tanımlandıysa, veri tabanından dönen veriler, kullanıcının görmeye yetkili olmadığı hücreler filtrelendikten sonra view metoduna döndürülür. Veri erişim kontrolü mümkün olduğunca model seviyesinde yapılarak, olası hata ve güvenlik açıklarının en aza indirgenmesi hedeflenmektedir.

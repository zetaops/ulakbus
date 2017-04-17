++++++++++++++++++++++++
Yayına Alma (Production)
++++++++++++++++++++++++

Sürüm adayı haline gelen master branchte bulunan kaynak kod, aşağıda detaylı şekilde anlatılan sürüm öncesi kabul testlerinden geçer. Bu testlerin başarılı olması halinde, semantik sürümlendirme sistemine [3]_ göre etiketlenir (tagging).

Semantik sürümlendirme sistemine göre kullanılacak desen MAJOR.MINOR.PATCH şeklindedir. Buna göre 3 haftalık küçük sürümler MINOR, gündelik çözülen işler PATCH, önceden belirlenmiş hedefleri kapsayan fazların sonunda ise MAJOR değerleri arttırılır.

MINOR sürümler çıktıkça, buildbot taglenmiş sürümdeki depoları production ortamında yayına alır. Gerekli dosyaları kopyalar ve veritabanı şemalarını yeni sürümlere göç ettirir.

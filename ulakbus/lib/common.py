# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import datetime
from math import floor
from ..models import AkademikTakvim, ObjectDoesNotExist, Unit, Room, DersEtkinligi, SinavEtkinligi, User
from zengine.lib.translation import gettext as _
from zengine.lib.cache import Cache
import random
import hashlib
import re

# Dakika cinsinden her bir slotun uzunluğu. Ders planlamada kullanılan en küçük zaman birimi.
SLOT_SURESI = 5

# CPSolver'ın ID alanlarında kabul ettiği maximum değer
SOLVER_MAX_ID = 900000000000000000

# En az bir büyük harf, (?=.*?[A-Z])
# En az bir küçük harf, (?=.*?[a-z])
# En az bir sayı, (?=.*?[0-9])
# En az bir özel karakter, (*&^%$@!?#.:/><; )
# En az 8 en fazla 100 karakter .{8,100}
# Türkçe karakter içermemesi (?=.*?^[^ıöüşçğ]*$)

parola_kalibi = re.compile(
    "^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[\(\)\[\]\{\}!@#\$%\^&\*\+=\-§±_~\/|\\"
    "><\.,:;≤≥])[A-Za-z\d\(\)\[\]\{\}!@#\$%\^&\*\+=\-§±_~\/|\\><\.,:;≤≥]{8,100}$")


def saat2slot(saat):
    return saat * 60 / SLOT_SURESI


def timedelta2slot(td):
    """timedelta cinsinden süreyi slot cinsine dönüştürür.

    Slot, CPSolver tarafından işlenen en küçük zaman birimidir.

    Args:
        td (datetime.timedelta):

    Returns:
        int: Slot cinsinden süre.
    """
    dakika = td.seconds / 60
    return dakika / SLOT_SURESI


def datetime2timestamp(dt):
    """Bir datetime objesini, saat dilimi bilgisi olmayan bir POSIX timestamp'ine dönüştürür.

    Bu fonksiyonun verdiği sonuç, datetime.datetime.utcfromtimestamp
    methodu ile geri okunabilir. Yani,
    >>> dt == datetime.datetime.utcfromtimestamp(datetime2timestamp(dt))
    True

    Bu fonksiyon saat dilimlerini dikkate almadan çalışmaktadır, bu nedenle bu fonksiyonun
    sonuçlarının farklı saat dilimleri arasında kullanılması sorun çıkaracaktır. Aynı nedenle,
    bu fonksiyonun verdiği timestampler POSIX ile uyumlu değildir.

    Args:
        dt (datetime.datetime): Dönüştürülecek datetime objesi

    Returns:
        float: Karşılık gelen POSIX timestamp'i
    """
    return (dt - datetime.datetime(1970, 1, 1)).total_seconds()


def get_akademik_takvim(unit, ogretim_yili):
    # verilen ogretim yilina gore guncel akademik
    # dondurmesi icin ogretim_yili parametresi eklenmistir.
    try:
        akademik_takvim = AkademikTakvim.objects.get(birim_id=unit.key, ogretim_yili=ogretim_yili)
        return akademik_takvim
    except ObjectDoesNotExist:
        yoksis_key = unit.parent_unit_no
        birim = Unit.objects.get(yoksis_no=yoksis_key)
        return get_akademik_takvim(birim, ogretim_yili)


def ders_programi_doldurma(root):
    # inst = [child for child in root.iter('instructor') if child.get('solution') == 'true']

    # room = [child for child in root.iter('room') if child.get('solution') == 'true']

    # time = [child for child in root.iter('time') if child.get('solution') == 'true']

    cls = [child for child in root.iter('class') for i in child.iter('instructor') if
           i.get('solution') == 'true']

    for child in cls:
        ders_etkinlik = DersEtkinligi.objects.get(unitime_key=child.get('id'))
        ders_etkinlik.solved = True

        for room in child.iter('room'):
            if room.get('solution') == 'true':
                room = Room.objects.get(unitime_key=room.get('id'))
                ders_etkinlik.room = room
                break

        for time in child.iter('time'):
            if time.get('solution') == 'true':
                day = time.get('days')
                for gun, k in enumerate(day):
                    if k == '1':
                        ders_etkinlik.gun = gun + 1

                start = int(time.get('start'))
                length = int(time.get('length'))
                duration = (start * SLOT_SURESI) / 60

                saat = "%02d" % floor(duration)
                ders_etkinlik.baslangic_saat = str(saat)
                dakika = "%02d" % (60 * (duration % 1))
                ders_etkinlik.baslangic_dakika = dakika

                duration = start + length
                duration = (duration * SLOT_SURESI) / 60
                saat = "%02d" % floor(duration)
                ders_etkinlik.bitis_saat = str(saat)
                dakika = "%02d" % (60 * (duration % 1))
                ders_etkinlik.bitis_dakika = dakika

        ders_etkinlik.save()


def sinav_etkinlikleri_oku(root):
    """CPSolver tarafından çözülen bir sınav planını okur.

    Args:
        root (xml.etree.ElementTree.Element): Çözülmüş
            sınav planının root elemanı.
    """
    periods = root.find('periods')
    zamanlar = {}
    for period in periods.iter('period'):
        baslangic_s, bitis_s = period.get('time').split(' ')
        baslangic = datetime.datetime.utcfromtimestamp(float(baslangic_s))
        id_ = period.get('id')
        zamanlar[id_] = baslangic

    exams = root.find('exams')
    for exam in exams.iter('exam'):
        assignment = exam.find('assignment')
        if assignment is not None:
            etkinlik = SinavEtkinligi.objects.get(unitime_key=exam.get('id'))
            period_id = assignment.find('period').get('id')
            etkinlik.tarih = zamanlar[period_id]
            etkinlik.solved = True
            for period in assignment.iter('room'):
                room = Room.objects.get(unitime_key=period.get('id'))
                etkinlik.SinavYerleri.add(room=room)
            etkinlik.save()


def aktivasyon_kodu_uret():
    """
    İki tane 12 karakterli random sayı ile anlık zaman bilgisinin birleşiminden
    rastgele bir string oluşturulur. Bu string sha1 ile hashlenir ve 40
    karakterli bir aktivasyon kodu üretilir.

    """
    rastgele_sayi = "%s%s%s" % (str(random.randrange(100000000000)),
                                str(datetime.datetime.now()),
                                str(random.randrange(100000000000)))

    hash_objesi = hashlib.sha1(rastgele_sayi)
    aktivasyon_kodu = hash_objesi.hexdigest()

    return aktivasyon_kodu


class ParolaK_AdiKontrol():
    def parola_uygunlugu(self, parola):
        """
        Belirlenen parola kalıbına göre verilen parolanın uyup uymadığı test edilir.
        Parolanın en az bir sayı, bir büyük harf, bir küçük harf, bir özel karakter içerdiği ve
        Türkçe karakter içermediği test edilir.

        Args:
            parola: Yeni parola

        Returns:
            (bool): True ya da False

        """
        return True if parola_kalibi.match(parola) else False

    def kullanici_adi_uygunlugu(self, yeni_k_adi):
        """
        Kullanıcının yeni kullanıcı adının başka bir kullanıcı
        tarafından kullanıp kullanmadığını kontrol eden method.
        Eğer kullanılıyorsa False, kullanılmıyorsa uygundur
        anlamında True gönderilir.

        Args:
            yeni_kullanici_adi: Yeni kullanıcı adı

        Returns:
            (bool) True ya da False

        """
        kullanici_adlari = [u.username for u in User.objects.filter()]
        return not yeni_k_adi in kullanici_adlari


def kullanici_adi_kontrolleri(eski_k_adi, yeni_k_adi, guncel_k_adi):
    """
    Kullanıcı adı kontrol setine kontrol edilmesi istenen durumlar yazılır. Eğer kontrol iki
    stringin karşılaştırılması ise tuple'ın ilk iki kısmına bu stringler yazılır. Eğer kontrol
    bir method yardımıyla yapılacaksa tuple'ın ilk kısmına method ismi, ikinci kısmına liste içine
    method içinde kullanılacak parametreler, beşinci kısma ise hangi object ile kullanılacaksa
    o yazılır. Üçüncü kısma bu kontrollerden hangi sonucun dönülmesinin beklendiği yazılır. Dördüncü
    kısıma ise beklenen durum karşılanmadığında döndürülecek hata mesajı yazılır.

    Args:
        guncel_k_adi(str): güncel kullanıcı adı
        eski_k_adi(str): Kullanıcının güncel kullanıcı adını doğrulaması için girdiği kullanıcı adı.
        yeni_k_adi(str): yeni belirlenecek olan kullanıcı adı.

    Returns:
        (bool) True ya da False
        msg(str): hata mesajı

    """
    k_adi_kontrol_set = [
        (guncel_k_adi, eski_k_adi, True, _(u'Kullanıcı adınızı yanlış girdiniz. Lütfen tekrar deneyiniz.')),
        (eski_k_adi, yeni_k_adi, False, _(u'Yeni kullanıcı adınız ile eski kullanıcı adınız aynı olmamalıdır.')),
        ('kullanici_adi_uygunlugu', [yeni_k_adi], True, _(u"""Böyle bir kullanıcı adı bulunmaktadır.
         Lütfen başka bir kullanıcı adı deneyiniz."""), ParolaK_AdiKontrol())]

    return kontrol_seti_uygunluk_testi(k_adi_kontrol_set)


def parola_kontrolleri(yeni_parola, yeni_parola_tekrar, kullanici=None, eski_parola=None):
    """
    Parola kontrol setine kontrol edilmesi istenen durumlar yazılır. Eğer kontrol iki
    stringin karşılaştırılması ise tuple'ın ilk iki kısmına bu stringler yazılır. Eğer kontrol
    bir method yardımıyla yapılacaksa tuple'ın ilk kısmına method ismi, ikinci kısmına liste içine
    method içinde kullanılacak parametreler, beşinci kısma ise hangi object ile kullanılacaksa
    o yazılır. Üçüncü kısma bu kontrollerden hangi sonucun dönülmesinin beklendiği yazılır. Dördüncü
    kısıma ise beklenen durum karşılanmadığında döndürülecek hata mesajı yazılır.

    Args:
        yeni_parola(str): yeni belirlenecek olan parola
        yeni_parola_tekrar(str): yeni parolanın tekrarı
        kullanici: User objesi
        eski_parola(str): kullanının güncel parolası

    Returns:
        (bool) True ya da False
        msg(str): hata mesajı

    """
    parola_kural_set = [
        ('check_password', [eski_parola], True, _(u'Kullanmakta olduğunuz parolanızı yanlış girdiniz.'), kullanici),
        (yeni_parola, yeni_parola_tekrar, True, _(u'Yeni parolanız ve tekrarı uyuşmamaktadır.')),
        (eski_parola, yeni_parola, False, _(u'Yeni parolanız ile eski parolanız aynı olmamalıdır.')),
        ('parola_uygunlugu', [yeni_parola], True, _(u"""Girmiş olduğunuz parola kurallara uymamaktadır.
        Lütfen parola kural setini dikkate alarak tekrar deneyiniz."""), ParolaK_AdiKontrol())]

    # Eğer eski_parola parametresi doluysa, eski parola kontrolleri için gerekli olan kontroller
    # kontrol listesinden kaldırılır.
    if not eski_parola:
        parola_kural_set = [parola_kural_set[1], parola_kural_set[3]]

    return kontrol_seti_uygunluk_testi(parola_kural_set)


def kontrol_seti_uygunluk_testi(kontrol_set):
    """
    kural[0] = method adı ya da karşılaştırılma yapılacak birinci parametre
    kural[1] = kural[0] method adı ise methodda çalıştırılacak parametre listesi
               değilse karşılaştırılma yapılacak ikinci parametre
    kural[2] = kontrolden gelmesi beklenen yanıt True ya da False
    kural[3] = kontrolden geçmemesi durumunda gösterilecek hata mesajı
    kural[4] = kural[0] method adı ise o methodun çalıştırılacağı obje

    Args:
        kontrol_set(list of tuple): Kontrol edecek durumlarin listesi

    Returns:
        uygunluk(bool): True ya da False
        hata mesajı(str): uygunluk False olduğunda gösterilecek hata mesajı

    """
    uygunluk = True
    hata_mesaji = ''
    for kural in kontrol_set:
        result = (kural[0] == kural[1]) if not isinstance(kural[1], list) else getattr(kural[4], kural[0])(*kural[1])
        if not (result == kural[2]):
            uygunluk = False
            hata_mesaji = kural[3]
            break

    return uygunluk, hata_mesaji


class ParolaSifirlama(Cache):
    """
    Parola sıfırlamak için kullanılan cache objesi.

    """
    PREFIX = 'PARE'
    SERIALIZE = False


class EPostaDogrulama(Cache):
    """
    E-Posta doğrulamak için kullanılan cache objesi.

    """
    PREFIX = 'EMVR'
    SERIALIZE = False

# def guncel_parola_kontrolu(user, parola):
#     """
#     Kullanıcının güncel parolası ile girdiği parolanın aynı olup
#     olmadığını kontrol eden method.
#
#     Args:
#         user : Kullanıcı nesnesi
#         parola (str): Kullanıcının güncel kullanıcı adını doğrulamak
#                       için girdiği kullanıcı adı
#
#     Returns:
#
#         (bool) True ya da False
#
#     """
#     return user.check_password(parola), _(u'Kullanmakta olduğunuz parolanızı yanlış girdiniz.')
#
#
# def yeni_parola_ve_tekrari_kontrolu(parola, parola_tekrar):
#     """
#     Kullanıcının girdiği yeni parolanın ve tekrarının aynı olup
#     olmadığını kontrol eden method.
#
#     Args:
#         parola(str): Yeni Parola
#         parola_tekrar(str): Yeni Parolanın tekrarı
#
#     Returns:
#
#         (bool) True ya da False
#
#     """
#     return parola == parola_tekrar, _(u'Yeni parolanız ve tekrarı uyuşmamaktadır.')
#
#
# def yeni_parola_eski_parola_ayni_olmamasi_kontrolu(eski_parola, yeni_parola):
#     """
#     Kullanıcının girdiği yeni parolanın, güncel parola ile aynı olup olmadığını
#     kontrol eden method. Aynı ise hatalı olduğu anlamında
#     False, değil ise True yollanır.
#
#     Args:
#         eski_parola(str): Güncel parola
#         yeni_parola(str): Yeni parola
#
#     Returns:
#
#         (bool) True ya da False
#
#     """
#     return not eski_parola == yeni_parola, _(u'Yeni parolanız ile eski parolanız aynı olmamalıdır.')
#
#
# def guncel_kullanici_adi_kontrolu(guncel_kullanici_adi, kullanici_adi):
#     """
#     Kullanıcının güncel kullanıcı adı ile girilen kullanıcı adının
#     aynı olup olmadığı kontrol edilir.
#
#     Args:
#         guncel_kullanici_adi(str): Kullanıcının güncel kullanıcı adı
#         kullanici_adi(str): Kullanıcının güncel kullanıcı adını doğrulamak
#                             için girdiği kullanıcı adı
#
#     Returns:
#
#         (bool) True ya da False
#         msg(str): hata mesajı
#
#     """
#     return guncel_kullanici_adi == kullanici_adi, _(u'Kullanıcı adınızı yanlış girdiniz. Lütfen tekrar deneyiniz.')
#
#
# def yeni_kullanici_adi_eskisiyle_ayni_olmamasi_kontrolu(eski_kullanici_adi, yeni_kullanici_adi):
#     """
#     Kullanıcının yeni kullanıcı adı ile eski kullanıcı adının aynı olmaması
#     kontrol edilir.
#
#     Args:
#         eski_kullanici_adi: Güncel kullanıcı adı
#         yeni_kullanici_adi: Yeni kullanıcı adı
#
#     Returns:
#         (bool) True ya da False
#         msg(str): hata mesajı
#
#     """
#     return eski_kullanici_adi != yeni_kullanici_adi, \
#            _(u'Yeni kullanıcı adınız ile eski kullanıcı adınız aynı olmamalıdır.')

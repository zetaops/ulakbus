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

# En az bir büyük harf
# En az bir küçük harf
# En az bir sayı
# En az bir özel karakter
# En az 8 en fazla 100 karakter
# Türkçe karakter içermemesi

parola_kalibi = re.compile(
    "^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[\(\)\[\]\{\}!@#\$%\^&\*\+=\-§±_~\/|\\"
    "><\.,:;≤≥])[A-Za-z\d\(\)\[\]\{\}!@#\$%\^&\*\+=\-§±_~\/|\\><\.,:;≤≥]{8,100}$")

e_posta_kalibi = re.compile('[^@]+@[^@]+\.[^@]+')


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


def parola_uygunlugu(parola):
    """
    Belirlenen parola kalıbına göre verilen parolanın uyup uymadığı test edilir.
    Parolanın en az bir sayı, bir büyük harf, bir küçük harf, bir özel karakter içerdiği ve
    Türkçe karakter içermediği test edilir.

    Args:
        parola: Yeni parola

    Returns:
        (bool): True ya da False

    """
    return bool(re.match(parola_kalibi, parola))

def e_posta_uygunlugu(e_posta):
    """
    Belirlenen e_posta adresi kalıbına göre verilen parolanın uyup uymadığı test edilir.

    Args:
        e_posta: Test edilecek e_posta adresi

    Returns:
        (bool): True ya da False

    """
    return bool(re.match(e_posta_kalibi, e_posta))



def kullanici_adi_var_mi(yeni_k_adi):
    """
    Verilen kullanıcı adının başka bir kullanıcı
    tarafından kullanıp kullanılmadığını kontrol eden method.
    Eğer kullanılıyorsa True, kullanılmıyorsa False döndürülür.

    Args:
        yeni_kullanici_adi: Yeni kullanıcı adı

    Returns:
        (bool) True ya da False

    """
    try:
        User.objects.get(username=yeni_k_adi)
        return True
    except ObjectDoesNotExist:
        return False


def kullanici_adi_kontrolleri(eski_k_adi, yeni_k_adi, guncel_k_adi):
    """
    Kullanıcı adı uygunluk kontrolleri.

    Args:
        guncel_k_adi(str): current nesnesi altindaki güncel kullanıcı adı
        eski_k_adi(str): formdan gelen kullanıcı adı.
        yeni_k_adi(str): formdan gelen yeni belirlenecek olan kullanıcı adı.

    Returns:
        (bool) True ya da False
        msg(str): hata mesajı

    """
    if guncel_k_adi != eski_k_adi:
        return False, _(u'Kullanıcı adınızı yanlış girdiniz. Lütfen tekrar deneyiniz.')

    if eski_k_adi == yeni_k_adi:
        return False, _(u'Yeni kullanıcı adınız ile eski kullanıcı adınız aynı olmamalıdır.')

    if kullanici_adi_var_mi(yeni_k_adi):
        return False, _(u"""Böyle bir kullanıcı adı bulunmaktadır.
        Lütfen başka bir kullanıcı adı deneyiniz.""")

    return True, None


def parola_kontrolleri(yeni_parola, yeni_parola_tekrar, kullanici=None, eski_parola=None):
    """
    Parola uygunluk kontrolleri.

    Args:
        yeni_parola(str): formdan gelen yeni belirlenecek olan parola
        yeni_parola_tekrar(str): formdan gelen yeni parolanın tekrarı
        kullanici: User objesi
        eski_parola(str): formdan gelen kullanının güncel olarak girdigi parolası

    Returns:
        (bool) True ya da False
        msg(str): hata mesajı

    """

    if eski_parola and not kullanici.check_password(eski_parola):
        return False, _(u'Kullanmakta olduğunuz parolanızı yanlış girdiniz.')
    if yeni_parola != yeni_parola_tekrar:
        return False, _(u'Yeni parolanız ve tekrarı uyuşmamaktadır.')
    if eski_parola and eski_parola == yeni_parola:
        return False, _(u'Yeni parolanız ile eski parolanız aynı olmamalıdır.')
    if not parola_uygunlugu(yeni_parola):
        return False, _(u"""Girmiş olduğunuz parola kurallara uymamaktadır.
        Lütfen parola kural setini dikkate alarak tekrar deneyiniz.""")

    return True, None


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

# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

import datetime
from math import floor
from ..models import AkademikTakvim, ObjectDoesNotExist, Unit, Room, DersEtkinligi, SinavEtkinligi

# Dakika cinsinden her bir slotun uzunluğu. Ders planlamada kullanılan en küçük zaman birimi.
SLOT_SURESI = 5

# CPSolver'ın ID alanlarında kabul ettiği maximum değer
SOLVER_MAX_ID = 900000000000000000


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

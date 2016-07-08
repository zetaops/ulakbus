
# -*-  coding: utf-8 -*-

from ..models import AkademikTakvim, ObjectDoesNotExist, Unit, Room, DersEtkinligi
from math import floor

# Dakika cinsinden her bir slotun uzunluğu. Ders planlamada kullanılan en küçük zaman birimi.
SLOT_SURESI = 5
# CPSolver'ın ID alanlarında kabul ettiği maximum değer
SOLVER_MAX_ID = 900000000000000000


def saat2slot(saat):
    return saat * 60 / SLOT_SURESI

def get_akademik_takvim(unit):
    try:
        akademik_takvim = AkademikTakvim.objects.get(birim_id=unit.key)
        return akademik_takvim
    except ObjectDoesNotExist:
        yoksis_key = unit.parent_unit_no
        birim = Unit.objects.get(yoksis_no=yoksis_key)
        return get_akademik_takvim(birim)


def ders_programi_doldurma(root):
    # inst = [child for child in root.iter('instructor') if child.get('solution') == 'true']

    # room = [child for child in root.iter('room') if child.get('solution') == 'true']

    # time = [child for child in root.iter('time') if child.get('solution') == 'true']

    cls = [child for child in root.iter('class') for i in child.iter('instructor') if i.get('solution') == 'true']

    for child in cls:
        ders_etkinlik = DersEtkinligi.objects.get(unitime_id=child.get('id'))
        ders_etkinlik.solved = True

        for room in child.iter('room'):
            if room.get('solution') == 'true':
                room = Room.objects.get(unitime_id=room.get('id'))
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
                duration = start * SLOT_SURESI / 60

                saat = "%02d" % floor(duration)
                ders_etkinlik.baslangic_saat = str(saat)
                dakika = "%02d" % (60 * (duration % 1))
                ders_etkinlik.baslangic_dakika = dakika

                duration = start + length
                duration = duration * SLOT_SURESI / 60
                saat = "%02d" % floor(duration)
                ders_etkinlik.bitis_saat = str(saat)
                dakika = "%02d" % (60 * (duration % 1))
                ders_etkinlik.bitis_dakika = dakika

        ders_etkinlik.save()

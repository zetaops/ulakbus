from ..models import AkademikTakvim, ObjectDoesNotExist, Unit, Room, ders_programi_data
from ulakbus.lib.unitime import ExportAllDataSet
from math import floor


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

    data_set = ExportAllDataSet()
    ders = ders_programi_data

    for child in cls:
        ders_etkinlik = ders.DersEtkinligi.objects.get(unitime_id=child.get('id'))
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
                duration = start * data_set._SLOT_SURESI / 60

                saat = "%02d" % floor(duration)
                ders_etkinlik.baslangic_saat = str(saat)
                dakika = "%02d" % (60 *(duration %1))
                ders_etkinlik.baslangic_dakika = dakika


                duration = start + length
                duration = duration * data_set._SLOT_SURESI / 60
                saat = "%02d" % floor(duration)
                ders_etkinlik.bitis_saat = str(saat)
                dakika = "%02d" % (60 * (duration % 1))
                ders_etkinlik.bitis_dakika = dakika

        ders_etkinlik.save()

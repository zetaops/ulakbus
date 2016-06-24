
from ..models import AkademikTakvim, ObjectDoesNotExist, Unit


def get_akademik_takvim(unit):
    try:
        akademik_takvim = AkademikTakvim.objects.get(birim_id=unit.key)
        return akademik_takvim
    except ObjectDoesNotExist:
        yoksis_key = unit.parent_unit_no
        birim = Unit.objects.get(yoksis_no=yoksis_key)
        return get_akademik_takvim(birim)
# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models.akademik_faaliyet import AkademikFaaliyet

from ulakbus.models.akademik_faaliyet import AkademikFaaliyetTuru

__author__ = 'Anıl Can Aydın'

def akademik_performans_hesapla():
    aft = AkademikFaaliyetTuru.objects.filter()
    data = {}
    for t in aft:
        num = AkademikFaaliyet.objects.filter(tur=t).count()
        data[t.key] = str(num)
    return data
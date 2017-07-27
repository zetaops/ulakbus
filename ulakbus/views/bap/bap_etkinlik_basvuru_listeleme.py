# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _


class BAPEtkinlikBasvuruListeleme(CrudView):
    """
    Koordinasyon biriminin etkinlik başvurularını listelediği adımdır. Her bir başvuruyu inceleyip
    karar verebilir.
    """
    class Meta:
        allow_search = True
        model = 'BAPEtkinlikProje'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = None

    def listele(self):
        """
        Koordinasyon biriminin yapılan etkinlik başvurularını listelediği adımdır.
        """
        self.list(list_fields=['bildiri_basligi', 'basvuru_yapan', 'durum'])

    @obj_filter
    def basvuru_islemleri(self, obj, result, **kwargs):
        """
        Default action buttonlar, koordinasyon biriminin etkinlik basvurusundaki eylemlerine göre
        düzenlenmiştir.
        """
        result['actions'] = [
            {'name': _(u'İncele ve Karar Ver'), 'cmd': 'goruntule', 'mode': 'normal',
             'show_as': 'button'},
        ]

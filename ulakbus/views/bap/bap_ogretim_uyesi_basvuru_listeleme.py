# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPProje
from zengine.forms import JsonForm, fields
from zengine.views.crud import CrudView, list_query, obj_filter
from zengine.lib.translation import gettext as _


class OgretimUyesiBasvuruListelemeView(CrudView):

    class Meta:
        allow_search = True
        model = 'BAPProje'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = None

    def basvuru_listele(self):
        self.list(list_fields=['ad', 'durum'])

    def talep_sec(self):
        pass

    def rapor_sec(self):
        pass

    @obj_filter
    def basvuru_islemleri(self, obj, result, **kwargs):
        """
        Default action buttonlar, öğretim üyesinin projedeki eylemlerine göre düzenlenmiştir.

        """
        # todo externaL_wf'ler tamamlandıkça actionlara eklenecek
        result['actions'] = [
            {'name': _(u'Görüntüle'), 'cmd': 'goruntule', 'mode': 'normal', 'show_as': 'button'},
        ]
        if obj.durum == 5:
            result['actions'].append({'name': _(u'Talepler'), 'cmd': 'talepler', 'mode': 'normal',
                                      'show_as': 'button'})
            result['actions'].append({'name': _(u'Raporlar'), 'cmd': 'rapor', 'mode': 'normal',
                                      'show_as': 'button'})

    @list_query
    def list_by_personel_id(self, queryset):
        """
        Öğretim üyesinin kendi projeleri filtrelenmiştir.
        """
        # return queryset.filter(yurutucu_id=self.current.user_id)
        return queryset.filter(yurutucu_id='G2XjlaJMX0FUZX84aoIeiVCqZMR')



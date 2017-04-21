# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.db.connection import cache
from zengine.models import TaskInvitation, WFInstance

from zengine.views.crud import CrudView, obj_filter
from zengine.lib.translation import gettext as _, gettext_lazy as __
from datetime import datetime, timedelta


class BasvuruListeleme(CrudView):
    class Meta:
        model = "BAPProje"

    def karari_ogretim_elemanina_gonder(self):
        user = self.object.yurutucu.user
        role = user.role_set[0].role

        # wfi_list = WFInstance.objects.filter(current_actor=role, name='bap_proje_basvuru').order_by()
        #
        # wfi_l = [wfi for wfi in wfi_list if 'proje_id' in wfi.clean_value()['data']]
        # wfi_list = [wfi for wfi in wfi_l if wfi.clean_value()['data']['proje_id']==self.object.key]
        # wfi = wfi_list[0]

        wfi = WFInstance.objects.filter(current_actor=role, name='bap_proje_basvuru',finished=True).order_by[0]

        wfi.finished = False
        wfi.data['karar'] = self.current.task_data['karar']
        wfi.data['revizyon_gerekce'] = self.current.task_data['revizyon_gerekce'] if wfi.data['karar'] == 'revizyon' else ''
        wfi.step = '"bap_check_point", 1'
        wfi.blocking_save()
        cache.delete(wfi.key)

        role.send_notification(title='',
                               message='',
                               typ=1,
                               url='#/cwf/bap_proje_basvuru/%s' % wfi.key,
                               sender=self.current.user
                               )
        today = datetime.today()

        inv = TaskInvitation(
            instance=wfi,
            role=role,
            wf_name=wfi.wf.name,
            progress=30,
            start_date=today,
            finish_date=today + timedelta(15)
        )
        inv.title = wfi.wf.title
        inv.save()

    @obj_filter
    def basvuru_listeleme(self, obj, result):
        result['actions'] = [
            {'name': _(u'İncele'), 'cmd': 'incele', 'mode': 'normal', 'show_as': 'button'}]

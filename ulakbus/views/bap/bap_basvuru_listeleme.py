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

    def karar_sonrasi_islemler(self):
        user = self.object.yurutucu.user
        role = ilgili_rolu_bul(user)
        today = datetime.today()
        karar = self.current.task_data['karar']

        if karar == 'onayla':
            role.send_notification(message='Projeniz onaylanmıştır',
                                   sender=self.current.user
                                   )
        else:

            wfi_finished_instances = WFInstance.objects.filter(current_actor=role,
                                                               name='bap_proje_basvuru',
                                                               finished=True)
            wfi_list = [wfi for wfi in wfi_finished_instances if
                        wfi._data['data']['bap_proje_id'] == self.object.key]
            wfi = sorted(wfi_list, key=lambda wfi: wfi.timestamp, reverse=True)[0]

            wfi.finished = False
            wfi.data['karar'] = self.current.task_data['karar']
            wfi.data['revizyon_gerekce'] = self.current.task_data['revizyon_gerekce']
            wfi.step = '"bap_check_point", 1'
            wfi.blocking_save()

            cache.delete(wfi.key)

            role.send_notification(title='',
                                   message='',
                                   typ=1,
                                   url='#/cwf/bap_proje_basvuru/%s' % wfi.key,
                                   sender=self.current.user
                                   )
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

    def karar_sonrasi_islem_mesaji(self):
        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Kararınız İletildi'),
            "msg": _(u'%s projesi hakkındaki kararınız %s adlı personele iletilmiştir.') % (
                self.object.ad, self.object.yurutucu.__unicode__())}

    def gecersiz_islem_mesaji(self):
        self.current.output['msgbox'] = {
            'type': 'warning', "title": _(u'Geçersiz İşlem'),
            "msg": _(self.current.task_data['hata_mesaji'])}


    @obj_filter
    def basvuru_listeleme(self, obj, result):
        result['actions'] = [
            {'name': _(u'İncele'), 'cmd': 'incele', 'mode': 'normal', 'show_as': 'button'}]


def ilgili_rolu_bul(user):
    if len(user.role_set) > 1:
        for role_set in user.role_set:
            if role_set.role.abstract_role.key == 'OGRETIM_ELEMANI':
                return role_set.role

    else:
        return user.role_set[0].role

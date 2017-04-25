# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from pyoko.db.connection import cache
from zengine.models import TaskInvitation, WFInstance
from zengine.views.crud import CrudView, obj_filter, list_query
from zengine.lib.translation import gettext as _, gettext_lazy as __
from datetime import datetime, timedelta


class BasvuruListeleme(CrudView):
    class Meta:
        model = "BAPProje"

    def karar_sonrasi_islemler(self):
        """
        Listeden seçilen projenin onaylanmasına karar verilmiş ise proje sahibi öğretim üyesi
        bildirim ile bilgilendirilir. Eğer revizyon kararı verilmiş ise proje başvurusu iş akışı
        instance'ı bulunur ve invitation yollanır. Böylelikle öğretim üyesinin tekrardan iş akışına
        katılması ve projeyi revizyon etmesi sağlanır.

        """

        user = self.object.yurutucu.user
        role = ilgili_rolu_bul(user)
        today = datetime.today()
        karar = self.current.task_data['karar']

        if karar == 'onayla':
            role.send_notification(title=_(u"Proje Onayı"),
                                   message=_(u"Başvurunuz koordinasyon birimi tarafından onaylanarak gündeme alınmıştır."),
                                   typ=1,
                                   url='',
                                   sender=self.current.user
                                   )
        else:

            wfi_finished_instances = WFInstance.objects.filter(name='bap_proje_basvuru',
                                                               finished=True)
            wfi_list = [wfi for wfi in wfi_finished_instances if
                        wfi._data['data']['bap_proje_id'] == self.object.key and wfi._data['pool']['ogretim_uyesi_lane'] == role.key]
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
        """
        Koordinasyon biriminin kararından sonra başarılı işlem mesajı oluşturulur.

        """

        self.current.output['msgbox'] = {
            'type': 'info', "title": _(u'Kararınız İletildi'),
            "msg": _(u'%s projesi hakkındaki kararınız %s adlı personele iletilmiştir.') % (
                self.object.ad, self.object.yurutucu.__unicode__())}

    @obj_filter
    def basvuru_listeleme(self, obj, result):
        result['actions'] = [
            {'name': _(u'İncele'), 'cmd': 'incele', 'mode': 'normal', 'show_as': 'button'}]

    @list_query
    def list_by_ordered(self, queryset):
        return queryset.filter().order_by()


def ilgili_rolu_bul(user):
    """
    Verilen kullanıcı nesnesinin öğretim elemanı abstract rolü ile ilgili rolü bulunur.

    Args:
        user(obj): User nesnesi

    Returns: (obj): Role nesnesi

    """
    if len(user.role_set) > 1:
        for role_set in user.role_set:
            if role_set.role.abstract_role.key == 'OGRETIM_ELEMANI':
                return role_set.role

    else:
        return user.role_set[0].role

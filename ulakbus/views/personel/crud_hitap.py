# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView, view_method, list_query
from zengine.lib.translation import gettext_lazy
from ulakbus.models.personel import Personel
from zengine import signals
from ulakbus.services.zato_wrapper import TcknService, HitapService
from pyoko.lib.utils import un_camel


class ListFormHitap(JsonForm):
    """
    HITAP Sync eklenmis list view formu.
    """
    add = fields.Button(gettext_lazy(u"Ekle"), cmd="add_edit_form")
    sync = fields.Button(gettext_lazy(u"HITAP ile senkronize et"), cmd="sync")


class CrudHitap(CrudView):
    """CrudHitap İş Akışı

    CrudHitap, standart CrudView'a ait save, delete gibi metotların
    Hitap senkronizasyonunu ilgilendiren işlevsellikler ile
    genişletilerek elde edilmiştir.

    Bu iş akışı için senkronizasyon şu şekilde çalışmaktadır:

        - Yerel kayıtlarda yapılan her değişiklik anında Hitap
          ile eşlenecektir.

        - Silinen kayıtlar, ancak Hitap'tan silinme onayı geldikten
          sonra silinecektir. İlgili kayıt öncelikle ``silinecek``
          şeklinde işaretlenir. Hitap'tan silme işlemi ile ilgili olumlu
          sonuç geldikten sonra silinme işlemi gerçekleşir. Kayit
          senkronize olarak işaretlenir.

        - Yeni eklenen kayıtlar, gönderilecek şeklinde işaretlenir.
          Hitap'a gonderilir. Hitap'tan dönen kayıt no ile ilgili
          kayda eklenir ve senkronize şeklinde işaretlenir.

        - Güncellenen kayıtlar ise, güncelleniyor şeklinde işaretlenir.
          Guncellenen kayıt Hitap'a gönderilir. Hitap yeni bir kayıt no
          üretir ve eski kaydı siler. Bu işlem soncunda Hitap yeni bir
          ``kayıt no`` gönderir. Yereldeki kayıt yeni ``kayıt no`` ile
          güncellenir ve senkronize olarak işaretlenir.

    Buna gore ``sync`` field şu değerlerde bulunabilir:

        * 1: Kayıt Hitap ile senkronize
        * 2: Yerel kayıt güncellendi, Hitap güncellenecek
        * 3: Yerel kayıt silindi, Hitap kaydı silinecek
        * 4: Yeni bir yerel kayıt oluşturuldu, Hitap'a gönderilecek.

    """

    def __init__(self, current=None):
        super(CrudHitap, self).__init__(current)
        self.ListForm = ListFormHitap
        if current and 'id' in self.input:
            self.current.task_data['personel_id'] = self.input['id']
            self.current.task_data['personel_tckn'] = Personel.objects.get(self.input['id']).tckn

    @view_method
    def sync(self):
        """Crud Hitap Sync

        Personele ait kayitlari hitap ile sync eder. Zamanlanmis sync islemini
        manuel olarak calistirir.

        """
        service_name = un_camel(self.model_class.__name__, dash='-') + '-sync'
        service = TcknService(service_name=service_name,
                              payload={"tckn": str(self.current.task_data['personel_tckn'])})
        service.zato_request()

    @view_method
    def save(self):
        """Crud Hitap Kaydet

        Nesneyi kaydeder. Eğer kayıt yeni ise ``sync`` alanını 4,
        mevcut kayıt güncellemesi ise 2 olarak işaretler.

        Hemen ardından zato servisi ile değişikliği bildirir.

        """

        self.set_form_data_to_object()
        obj_is_new = not self.object.is_in_db()
        action, self.object.sync = ('ekle', 4) if obj_is_new else ('guncelle', 2)
        self.object.tckn = self.current.task_data['personel_tckn']
        self.object.save()
        self.current.task_data['object_id'] = self.object.key

        service_name = un_camel(self.model_class.__name__, dash='-') + '-' + action
        service = HitapService(service_name=service_name, payload=self.object)
        try:
            result = dict(service.zato_request())
            self.object.kayit_no = result['kayitNo']
            self.object.sync = 1
            self.object.blocking_save()
        except:
            pass

    @view_method
    def delete(self):
        """Crud Hitap Sil

        Nesneyi kaydeder. ``sync`` alanını 3 olarak işaretler.

        Hemen ardından zato servisi ile değişikliği bildirir.

        """

        signals.crud_pre_delete.send(self, current=self.current, object=self.object)

        if 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']
        object_data = self.object._data
        self.object.sync = 3
        self.object.blocking_delete()

        service_name = un_camel(self.model_class.__name__, dash='-') + "-sil"
        service = HitapService(service_name=service_name,
                               payload={"tckn": self.object.tckn, "kayit_no": self.object.kayit_no})
        try:
            service.zato_request()
            self.object.sync = 1
            self.object.blocking_delete()
            signals.crud_post_delete.send(self, current=self.current, object_data=object_data)
            self.set_client_cmd('reload')
        except:
            pass

    @list_query
    def list_by_personel_id(self, queryset):
        return queryset.filter(personel_id=self.current.task_data['personel_id'])

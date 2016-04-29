# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
from zengine.forms import fields, JsonForm
from zengine.views.crud import CrudView, view_method


def zato_service_selector(model, action):
    suffix = {"add": "Ekle",
              "update": "Guncelle",
              "delete": "Sil",
              "get": "Getir",
              "sync": "SenkronizeEt"}[action]

    prefix = model.Meta.hitap_service_prefix
    service_class_name = prefix + suffix

    hitap_service = getattr(
        __import__('ulakbus.services.zato_wrapper', fromlist=[service_class_name]),
        service_class_name)

    return hitap_service


class ListFormHitap(JsonForm):
    """
    Holds list view form elements.

    Used by CrudMeta metaclass to create distinct
    copies for each subclass of CrudView.
    """
    add = fields.Button("Ekle", cmd="add_edit_form")
    sync = fields.Button("HITAP ile senkronize et", cmd="sync")


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

    @view_method
    def sync(self):
        hitap_service = zato_service_selector(self.Meta.Model, 'sync')
        hs = hitap_service(tckn=self.object.tckn)
        response = hs.zato_request()

    def save(self):
        """Crud Hitap Kaydet

        Nesneyi kaydeder. Eğer kayıt yeni ise ``sync`` alanını 4,
        mevcut kayıt güncellemesi ise 2 olarak işaretler.

        Hemen ardından zato servisi ile değişikliği bildirir.

        """

        self.set_form_data_to_object()
        obj_is_new = not self.object.is_in_db()
        action, self.object.sync = ('add', 4) if obj_is_new else ('update', 2)
        self.object.save()

        hitap_service = zato_service_selector(self.Meta.Model, action)
        hs = hitap_service(kayit=self.object)
        try:
            response = hs.zato_request()
            if response['status'] == 'ok':
                self.object.sync = 1
                self.object.save()
        except:
            # try blogundaki islemleri background gondermek
            pass

        if self.next_cmd and obj_is_new:
            self.current.task_data['added_obj'] = self.object.key

    def delete(self):
        """Crud Hitap Sil

        Nesneyi kaydeder. ``sync`` alanını 3 olarak işaretler.

        Hemen ardından zato servisi ile değişikliği bildirir.

        """

        self.current.task_data['deleted_obj'] = self.object.key
        if 'object_id' in self.current.task_data:
            del self.current.task_data['object_id']

        self.object.sync = 3
        hitap_service = zato_service_selector(self.Meta.Model, 'delete')
        hs = hitap_service(kayit=self.object)

        try:
            response = hs.zato_request()
            if response['status'] == 'ok':
                self.object.sync = 1
                self.object.delete()
        except:
            # try blogundaki islemleri background gondermek
            pass

        self.set_client_cmd('reload')

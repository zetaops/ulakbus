# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#

from zengine.views.crud import CrudView

# Modellere karsilik gelen HitapServisleri listesi
zato_service_list = {
    'HizmetMahkeme': {
        "add": "HitapMahkemeBilgileriEkle",
        "update": "HitapMahkemeBilgileriGuncelle",
        "delete": "HitapMahkemeBilgileriSil"
    },
    'HizmetKurs': {
        "add": "HizmetKursEkle",
        "update": "HizmetKursGuncelle",
        "delete": "HizmetKursSil"
    },
}


def zato_service_selector(model, action):
    service_class_name = zato_service_list[model][action]
    hitap_service = getattr(__import__('ulakbus.services.zato_wrapper', fromlist=[service_class_name]),
                            service_class_name)
    return hitap_service


class CrudHitap(CrudView):
    """
    CrudHitap, standart CrudView save, delete gibi hitap senkrizasyonunu ilgilendiren metodlari degistirilerek
    extend edilmistir.

    Sync mekanizmasi su sekilde calisamaktadir:
        - Yerel kayitlarda yapilan her degisiklik aninda Hitap ile eslenecektir.

        - Silinen kayitlar, ancak Hitap tan silinme onayi geldikten sonra silinecektir. Ilgili kayit oncelikle
        silinecek seklinde isaretlenir. Hitaptan silme islemi ile ilgili olumlu sonuc geldikten sonra
        silinme islemi gerceklesir. Kayit senkronize olarak isaretlenir.

        - Yeni eklenen kayitlar, gonderilecek seklinde isaretlenir. Hitap a gonderilir. Hitaptan donen kayit no ilgili
        kayda eklenir ve senkronize seklinde isaretlenir.

        - Guncellenen kayitlar ise, guncelleniyor seklinde isaretlenir. Guncellenen kayit Hitap a gonderilir. Hitap
        yeni bir kayit no uretir ve eski kaydi siler. Bu islem soncunda Hitap yeni kayit no gonderir. Yereldeki kayitda
        kayit no guncellenir ve senkronize olarak isaretlenir.

    Buna gore sync field su degerlerde bulunabilir:
        1: all is good
        2: updated locally, update on hitap
        3: deleted locally, delete from hitap
        4: created locally, send to hitap

    """

    # class Meta:
    # Kullanilacak temel Model WF baslatilinca verilecek. Bu sebeple Model vermiyoruz.

    def save(self):
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

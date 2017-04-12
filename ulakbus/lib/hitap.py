# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.services.zato_wrapper import HitapService
from datetime import datetime


def hitap_save(obj, service_name, meta, index_fields):
    """

    Yeni eklenmiş ya da değiştirilmiş kaydı hitapa yollar. Hitapa
    yolladıktan sonra yereldeki kaydın sync değeri 1 yapılır.
    """
    action = 'ekle' if obj.sync == 2 else 'guncelle'
    service_name = "%s-%s" % (service_name, action)
    service = HitapService(service_name=service_name,
                           payload=obj,
                           auth={"kullanici_ad": "",
                                 "kullanici_sifre": ""})
    try:
        result = service.zato_request()
        obj.kayit_no = result['kayitNo']
        obj.sync = 1
        obj.son_senkronize_tarihi = datetime.now()
        obj.blocking_save(meta=meta, index_fields=index_fields)
    except:
        pass


def hitap_delete(obj, service_name, meta, index_fields):
    """

    Yerelde silinecek olarak işaretlenmiş bir kaydı hitapa yollar
    hitaptan da siler. İşlem bittikten sonra kayıt yerelden de silinir.

    """

    service_name = "%s-sil" % service_name
    service = HitapService(service_name=service_name,
                           payload={"tckn": obj.tckn, "kayit_no": obj.kayit_no},
                           auth={"kullanici_ad": "",
                                 "kullanici_sifre": ""})
    try:
        service.zato_request()
        obj.sync = 1
        obj.blocking_delete(meta=meta, index_fields=index_fields)
    except:
        pass

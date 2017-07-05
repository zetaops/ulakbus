#-*- coding:utf-8 -*-

from ulakbus.models import Personel
from ulakbus.lib.hizmet_sureleri import HizmetSureleri

def personel_izin_belirle():
    """
    Her yıl başı itibariyle çalıştırılacak olan bir zamanlanmış
    görev metodudur. Tüm personelin yıllık ve mazeret izinlerini belirler.
    Returns:

    """
    for p in Personel.objects.all():
        hs = HizmetSureleri(p)
        sure_kontrol = 10 * 360
        fiili_hizmet = hs.fiili_hizmet_getir()
        p.gecen_yil_kalan_izin = p.bu_yil_kalan_izin
        if fiili_hizmet >= sure_kontrol:
            p.bu_yil_kalan_izin = 30
        else:
            p.bu_yil_kalan_izin = 20

        if p.mazeret_izin > 10:
            p.bu_yil_kalan_izin -= p.mazeret_izin

        p.mazeret_izin = 0
        p.save()
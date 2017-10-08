# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def dogrudan_tek_kaynak_uret(context_data, wants_pdf=False):
    """
    Doğrudan tek kaynak template.

    Kullanılabilir değişkenler :
        -> idare            : Hangi daire hazırlıyor, BAP vs.
        -> alim_yapan_birim :

        -> ongorulen_teslim_zamani :
        -> ongorulen_yaklasik_bedel:
        -> satici_unvan            :
        -> satici_tebligat_adresi  :

        -> satici_vergi_dairesi_ve_numarasi:
        -> satici_telefon_ve_faks_numarasi :
        -> satici_eposta_adresi            :
        -> satici_ilgili_kisi              :

        -> ihtiyac_konusu_malin_nitelikleri:
        -> alimin_hangi_kapsamda_yapildigi :

        -> alim_maddesi : Alım maddesi, 21-a,b,c bendine göre bir işeretleme şeklidir.
                          Applied filters on alim_maddesi : string(), lower() (a, b, c)
                          Örnek : a,b,c,A,B,C,"a" vs.
        -> ihale_yetkilisi :
            ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
            -> ad       :
            -> gorev    :
    Args:
        context_data (dict):
        wants_pdf    (bool):
    Returns:
        str: URL
    """
    template = "dogrudan_tek_kaynak.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

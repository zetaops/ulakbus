# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def bap_komisyon_toplanti_tutanagi_uret(context_data, wants_pdf=False):
    """
    BAP Komisyon toplantı tutanağı şablonu için kullanılabilir değişkenler:

    -> karar_tarihi
    -> oturum_no
    -> karar_no
    -> kararlar         : <list> Karar metinleri liste halinde buraya gelir.
    -> baskan           : Toplantı başkanı adı
    -> bap_koordinatoru : BAP Koordinatörü adı
    -> uyeler           : <list> Toplamda 5 toplantı üyesi olmalı. 5 Zorunlu.


    Args:
        context_data (dict):
        wants_pdf    (Bool):
    Returns:
        str: URL
    """
    template = "bap_komisyon_toplanti_tutanagi.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

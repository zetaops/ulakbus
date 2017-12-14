# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def personel_terfi_liste_uret(context_data, wants_pdf=False):
    """
    BAP Komisyon toplantı tutanağı şablonu için kullanılabilir değişkenler:

    -> makam             : Rektörlük veya Genel Sekreterlik
    -> personel_turu     : Akademik veya Idari
    -> kanun_no          : kanun numarasi
    -> kanun_maddeleri   : kanun maddeleri
    -> gun               : belge gunu
    -> ay                : belge ayi
    -> yil               : belgei yili
    -> terfiler          : <list> terfi listesi


    Args:
        context_data (dict):
        wants_pdf    (Bool):
    Returns:
        str: URL
    """
    template = "personel_terfi_liste.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

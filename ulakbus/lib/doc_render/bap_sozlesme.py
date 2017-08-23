# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def bap_sozlesme_uret(context_data, wants_pdf=False):
    """
    BAP Sözleşme Şablonu

    Şablon içinde kullanabileceğiniz değişkenler:
        -> proje_no             : BAP proje numarası
        -> proje_basligi        : BAP proje başlığı
        -> proje_yurutucusu     : BAP proje yürütücüsü (x2 in Template)
        -> proje_butcesi        : BAP proje bütçesi
        -> toplam_destek_tutari : Verilecek desteğin toplam değeri (TL)
        -> sozlesme_imza_tarihi : Sözleşmenin imzalanma tarihi (x2 in Template)
        -> bap_komisyon_baskani : BAP komisyon başkanının adı.
        -> tuketim_malzemeleri  : Proje için gerekecek olan malzemelerin listesi.
            ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
            --> yil          : Malzeme yılı
            --> tur          : Malzeme türü
            --> gerekce      : Malzeme kullanımı için gerekçe.
            --> miktar       : Malzemenin ne kadar olacağı.
            --> birim_fiyat  : Malzemenin birim fiyatı.
            --> toplam_tutar : Malzemenin `miktar`ı ile `birim_fiyat`ının çarpımı.

    Args:
        context_data (dict): Template içinde kullanılacak olan değişkenler.
        wants_pdf (Bool)     : Output olarak PDF isteniyorsa, True olmalı.

    Returns:
        str: Üretilmiş olan dökümanın, URL adresi.

    """

    template = "bap_sozlesme.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

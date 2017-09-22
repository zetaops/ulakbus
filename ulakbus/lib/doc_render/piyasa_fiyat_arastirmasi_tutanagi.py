# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def piyasa_fiyat_arastirmasi_tutanagi_uret(context_data, wants_pdf=False):
    """
    Piyasa fiyat araştırması tutanağı şablonu.

    !!!    Verilerin sıralı olmasına dikkat ediniz....

    -> idare_adi    :
    -> yapilan_isin_adi :
    -> alim_yapan_gorevlilere_iliskin :
    -> ihale_onay_belgesi_tarih_sayi  :

    -> firmalar :
        ### Bu bir liste olmalı. 3 Elemanlı. Yani 3 Firma olabilir. Eksik yazmayın!

    -> malzemeler :
        ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
        --> sira_no :
        --> adi     :
        --> miktar  :
        --> birim   :

        --> f1_birim    : Şirket 1 'in vermiş olduğu birim fiyat.
        --> f1_toplam   : Şirket 1 'in vermiş olduğu toplam fiyat. Birim * Adet.

        --> f2_birim    : Şirket 2'nin vermiş olduğu birim fiyat.
        --> f2_toplam   : Şirket 2'nin vermiş olduğu toplam fiyat. Birim * Adet.

        --> f3_birim    : Şirket 3 için.
        --> f3_toplam   : Şirket 3 için. Birim * Adet. Max. 3 şirket olabilir.

    -> f1_genel_toplam : Firma 1'in teklifinin genel toplamı.
    -> f2_genel_toplam : Firma 2'nin teklifinin genel toplamı.
    -> f3_genel_toplam

    -> malzeme_sayisi   : Kaç kalem malzeme alındığı bilgisi.
    -> uygun_gorulen_firma_adi_adresi : İhaleyi kazanan, firma bilgisi.
    -> uygun_gorulen_teklif_tutari    : İhaleyi ne kadar ile kazandı.

    -> gorevli :
        ### Bu bir liste olmalı. Liste elemanları dict ile şunları içermeli.
        --> ad      : Görevlinin adı
        --> unvan   : Görevlinin ünvanı
        # Örnek erişim >>> gorevli[0].ad
    -> harcama_yetkilisi :
        ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
        --> ad      : Harcama yetkilisinin adı
        --> unvan   : Ünvanı. BAP Koordinatorü vs.
    -> belge_imza_tarihi : Belgenin imzalanma tarihi. En altta yer alıyor.

    Args:
        context_data (dict): Context data
        wants_pdf    (Bool):
    Returns:
        str: URL rendered doc.
    """
    template = "piyasa_fiyat_arastirmasi_tutanagi.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

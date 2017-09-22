# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument
import datetime


def siparis_formu_uret(context_data, wants_pdf=False):
    """
    Sipariş formu için gerekli context data.

    -> isin_niteligi         :
    -> butce_tertibi         :
    -> isin_adi_veya_miktari :
    -> malzemeler            : 1..*
        ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
        --> sira_no :
        --> adi     :
        --> miktar  :
        --> birim   :

    -> yuklenici_firma_adi   : (x2 in Template)
    -> tebligata_esas_adresi :
    -> siparis_bedeli        :
    -> odeme_saymanligi      :
    -> vergi_resim_ve_harclar:
    -> garanti_suresi_ve_sartlar:
    -> yedek_parca_montaj_sartlari:
    -> teslim_suresi         :
    -> belge_yili            : Bulunulan yıl, 2017. (x3 in Template)
    -> gerceklestirme_gorevlisi :
        ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
        --> ad   : Kişi adı, Prof. Someone
        --> unvan: Proje yürütücüsü, BAP Koordinatörü vs.vs.
    -> harcama_yetkilisi :
        ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
        --> ad   : Kişi adı, Prof Someone
        --> unvan: BAP koordinatörü vs.vs.

    Args:
        context_data (dict): Context variables for template engine.
        wants_pdf    (Bool): Output as PDF ?
    Returns:
        str: URL of produced document.
    """
    # Set current year.
    context_data['belge_yili'] = datetime.datetime.now().year
    template = "siparis_formu.odt"

    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

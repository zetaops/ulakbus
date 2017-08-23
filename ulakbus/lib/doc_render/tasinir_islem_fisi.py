# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def tasinir_islem_fisi_uret(context_data, wants_pdf=False):
    """
    Taşınır işlem fişi Şablonu

    Şablon içerisinde kullanabileceğiniz değişkenler:

        -> fis_sira_no : Fişin defterdeki sıra numarası, 2017/122
        -> tahakkuk_no : Fişin tahakkuk numarası,
        -> fis_tarihi  : Fişin oluşturulma tarihi. (x2 in Template)

        -> il_ilce_adi          : İl, ilçe adı.
        -> il_ilce_kodu         : İlin kodu, (06 mesela.)
        -> harcama_birimi_adi   :
        -> harcama_birimi_kodu  :
        -> muhasebe_birimi_adi  :
        -> muhasebe_birimi_kodu :

        -> kabul_komisyonu_tutanagi_tarihi :
        -> kabul_komisyonu_tutanagi_sayisi :
        -> dayanagi_belgenin_tarihi        : Dayanağı olan belgenin tarihi.
        -> dayanagi_belgenin_sayisi        :

        -> islem_cesidi         : Yapılan işlem, (Ör: BAP Satın Alma)
        -> nereden_geldigi      :
        -> kime_verildigi       :
        -> nereye_verildigi     :

        -> gonderilen_harcama_adi               : Gönderilen birim hakkında.
        -> gonderilen_harcama_kodu              :
        -> gonderilen_tasinir_ambari_adi        :
        -> gonderilen_tasinir_ambari_kodu       :
        -> gonderilen_muhasebe_biriminin_adi    :
        -> gonderilen_muhasebe_biriminin_kodu   :

        -> tasinirlar :
            ### Aşağıdaki niteliklere sahip, dict veya object gönderilmeli.
            --> sira_no         :
            --> kodu            :
            --> sicil_no        :
            --> adi             :
            --> ambar_kodu      :
            --> olcu_birimi     :
            --> birim_fiyat     :
            --> miktari         :
            --> tutari          :

        -> genel_bilgilendirme_kod      : Toplam yazılmadan önce alınan taşınır hakkında bilgi.
        -> genel_bilgilendirme_adi      :
        -> genel_bilgilendirme_tutari   :

        -> genel_toplam    :
        -> tif_kurus_farki :

        -> kalem_girdi_sayisi               : (x2 in Template)
        -> tasinir_girdi_sayisi             : (x2 in Template)
        -> tasinir_kayit_yetkilisi_ad       :
        -> tasinir_kayit_yetkilisi_unvan    :
        -> teslim_eden_ad                   :
        -> teslim_eden_unvani               :

    Args:
        context_data (dict) : Context variables for template engine.
        wants_pdf   (Bool)  : Output as PDF?
    Returns:
        str : URL
    """
    template = "tasinir_islem_fisi.odt"
    rd = RenderDocument(template=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

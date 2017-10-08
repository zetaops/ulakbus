# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def mal_ve_hizmet_alimlari_onay_belgesi_uret(context_data, wants_pdf=False):
    """
    Mal ve hizmet alımları onay belgesi template değişkenleri:

    -> i_f_no       : Belgenin sağ üst köşesinde yer alan bir numara.
    -> alimi_yapan_idare_adi    :
    -> belge_tarih_ve_sayisi    :
    -> isin_tanimi              :
    -> isin_niteligi            :
    -> isin_miktari             :
    -> yaklasik_maliyet         :
    -> kullanilabilir_odenek_tutari:
    -> proje_numarasi           :
    -> butce_tertibi            :
    -> alim_usulu               : Alım usulü veya şekli.
    # Bundan sonraki degerler örnek dökümanda çok basit cevaplanmış.
    # Yoktur, düzenlenmeyecektir, verilmeyecektir gibi.
    -> avans_verilme_sartlari   :
    -> ilanin_sekli_ve_adedi    :
    -> sartname_duzenlemesi     :
    -> sozlesme_duzenlemesi     :

    -> alim_ile_ilgili_aciklama : Alım yapan kişinin ve neden alım yapıldığı.
    -> arastirma_gorevlileri    : Piyasa araştırması yapmakla görevli araştırmacı personel.
        ### Bu bir list olmalıdır ve sadece isimleri yer almalıdır.
        ### Örnek kullanım : for gorevli in arastirma_gorevlileri: print (gorevli)

    -> belge_imza_tarihi        : İmzanın atıldıgı kısımda yer alır.
    -> gorevli      :
        ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
        --> ad      : Görevli adı.
        --> unvan   : Görevlinin unvanı. Project Executor vs.
    -> ihale_yetkilisi :
        ### Aşağıdaki attributelara sahip bir dict veya object olmalı.
        --> ad      : İhale yetkilisi ad.
        --> unvan   : Ünvanı

    Args:
        context_data (dict): Template içinde kullanılacak olan değişkenler.
        wants_pdf (Bool)     : Output olarak PDF isteniyorsa, True olmalı.

    Returns:
        str: Üretilmiş olan dökümanın, URL adresi.
    """
    template = "mal_ve_hizmet_alimlari_onay_belgesi.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

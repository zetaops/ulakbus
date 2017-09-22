# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument

def bap_muayene_ve_kabul_komisyonu_tutanagi_uret(context_data, wants_pdf=False):
    """
    BAP muayene ve kabul komisyonu tutanağı şablonu.

    Template içerisinde kullanabileceğiniz değişkenler:

    -> i_f_no                 : Tutanağın sağ üst köşesinde yer alan numara bilgisi.
    -> nereden_geldigi        : Taşnırın nereden geldiği.
    -> dayandigi_belge_tarihi :
    -> dayandigi_belge_sayisi :
    -> muayene_kabul_komisyonu_tutanagi_tarihi: Belgenin oluşma tarihi.

    -> tasinirlar:
        ### Aşağıdaki niteliklere sahip, dict veya object gönderilmeli.
        --> miktari             :
        --> birimi              :
        --> adi_ve_ozellikleri  :

    -> tasinir_sayisi : Toplam taşınır sayısı. Yani kaç kalem taşınır girildi.
    -> baskan:
        ### Aşağıdaki niteliklere sahip, dict veya object gönderilmeli.
        --> adi     : Başkanın adı, Someone.
        --> unvan   : Başkanın ünvanı, Proje Yürütücüsü, Öğretim Görevlisi vs.
    -> uye1 :
        ### Aşağıdaki niteliklere sahip, dict veya object gönderilmeli.
        --> adi     : Üyenin adı
        --> unvan   : Ünvanı
    -> uye2 :
        ### Aşağıdaki niteliklere sahip, dict veya object gönderilmeli.
        --> adi     : Üye adı.
        --> unvan   : Üyenin ünvanı.

    Args:
        context_data (dict) : Context variables for template engine.
        wants_pdf (Bool)    : If client wants the output as PDF, pass True.

    Returns:
        str : URL of rendered document.

    """
    template = "bap_muayene_ve_kabul_komisyon_tutanagi.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

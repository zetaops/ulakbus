# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.lib.document import RenderDocument


def muayene_gorevlendirmesi_uret(context_data, wants_pdf=False):
    """
    Muayene görevlendirmesi dilekçe şablonu üretir.

    Template içerisinde kullanabileceğiniz değişkenler:

        -> dilekce_sayisi           :
        -> dilekce_tarihi           : Oluşturulma tarihi. (x2 in Template)

        -> gerceklestirme_gorevlisi :
            ### Aşağıdaki niteliklere sahip, dict veya object gönderilmeli.
            --> ad      :
            --> unvan   :
        -> harcama_yetkilisi :
            ### Aşağıdaki niteliklere sahip, dict veya object gönderilmeli.
            --> ad      :
            --> unvan   :

        -> muayene_komisyonu_idari_uzman     : Görevlendirilecek kişinin adı.
        -> muayene_komisyonu_teknik_uzman    :
        -> muayene_komisyonu_ambar_gorevlisi :

    Args:
        context_data (dict) : Variables for template engine.
        wants_pdf (Bool)    : Output as PDF?
    Returns:
        str: URL
    """
    template = "muayene_gorevlendirmesi.odt"
    rd = RenderDocument(template_name=template,
                        context=context_data,
                        wants_pdf=wants_pdf)
    return rd.doc_url

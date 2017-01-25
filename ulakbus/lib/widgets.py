# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Personel


def personel_istatistik_bilgileri():
    total_personel = Personel.objects.count()
    erkek_personel = Personel.objects.filter(cinsiyet=1).count()
    kadin_personel = total_personel - erkek_personel

    akademik_personel = Personel.objects.filter(personel_turu=1).count()
    akademik_personel_erkek = Personel.objects.filter(personel_turu=1, cinsiyet=1).count()
    akademik_personel_kadin = akademik_personel - akademik_personel_erkek

    idari_personel = total_personel - akademik_personel
    idari_personel_erkek = erkek_personel - akademik_personel_erkek
    idari_personel_kadin = kadin_personel - akademik_personel_kadin

    prof_total = Personel.objects.filter(unvan=1550).count()
    prof_erkek = Personel.objects.filter(unvan=1550, cinsiyet=1).count()
    prof_kadin = prof_total - prof_erkek

    doc_total = Personel.objects.filter(unvan=1555).count()
    doc_erkek = Personel.objects.filter(unvan=1555, cinsiyet=1).count()
    doc_kadin = doc_total - doc_erkek

    yar_doc_total = Personel.objects.filter(unvan=1565).count()
    yar_doc_erkek = Personel.objects.filter(unvan=1565, cinsiyet=1).count()
    yar_doc_kadin = yar_doc_total - yar_doc_erkek

    ar_gor_total = Personel.objects.filter(unvan=1590).count()
    ar_gor_erkek = Personel.objects.filter(unvan=1590, cinsiyet=1).count()
    ar_gor_kadin = ar_gor_total - ar_gor_erkek

    engelli_personel_total = Personel.objects.filter(engel_orani__gt=0).count()
    engelli_personel_erkek = Personel.objects.filter(engel_orani__gt=0, cinsiyet=1).count()
    engelli_personel_kadin = engelli_personel_total - engelli_personel_erkek

    return {
        "total_personel": total_personel,
        "erkek_personel": erkek_personel,
        "kadin_personel": kadin_personel,
        "akademik_personel": akademik_personel,
        "akademik_personel_erkek": akademik_personel_erkek,
        "akademik_personel_kadin": akademik_personel_kadin,
        "idari_personel": idari_personel,
        "idari_personel_erkek": idari_personel_erkek,
        "idari_personel_kadin": idari_personel_kadin,
        "prof_total": prof_total,
        "prof_erkek": prof_erkek,
        "prof_kadin": prof_kadin,
        "doc_total": doc_total,
        "doc_erkek": doc_erkek,
        "doc_kadin": doc_kadin,
        "yar_doc_total": yar_doc_total,
        "yar_doc_erkek": yar_doc_erkek,
        "yar_doc_kadin": yar_doc_kadin,
        "ar_gor_total": ar_gor_total,
        "ar_gor_erkek": ar_gor_erkek,
        "ar_gor_kadin": ar_gor_kadin,
        "engelli_personel_total": engelli_personel_total,
        "engelli_personel_erkek": engelli_personel_erkek,
        "engelli_personel_kadin": engelli_personel_kadin
    }

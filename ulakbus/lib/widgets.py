# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Personel


def personel_istatistik_bilgileri():
    personel_d = Personel.objects.distinct_values_of('cinsiyet')
    total_personel = personel_d['1'] + personel_d['2']
    erkek_personel = personel_d['1']
    kadin_personel = personel_d['2']

    personel_turu_d = Personel.objects.distinct_values_of('personel_turu')
    akademik_personel = personel_turu_d['1']
    akademik_personel_erkek = Personel.objects.all(personel_turu=1, cinsiyet=1).count()
    akademik_personel_kadin = akademik_personel - akademik_personel_erkek

    idari_personel = total_personel - akademik_personel
    idari_personel_erkek = erkek_personel - akademik_personel_erkek
    idari_personel_kadin = kadin_personel - akademik_personel_kadin

    unvan_d = Personel.objects.distinct_values_of('unvan')
    prof_total = unvan_d['1550'] if '1550' in unvan_d else 0
    prof_erkek = Personel.objects.all(unvan=1550, cinsiyet=1).count()
    prof_kadin = prof_total - prof_erkek

    doc_total = unvan_d['1555'] if '1555' in unvan_d else 0
    doc_erkek = Personel.objects.all(unvan=1555, cinsiyet=1).count()
    doc_kadin = doc_total - doc_erkek

    yar_doc_total = unvan_d['1565'] if '1565' in unvan_d else 0
    yar_doc_erkek = Personel.objects.all(unvan=1565, cinsiyet=1).count()
    yar_doc_kadin = yar_doc_total - yar_doc_erkek

    ar_gor_total = unvan_d['1590'] if '1590' in unvan_d else 0
    ar_gor_erkek = Personel.objects.all(unvan=1590, cinsiyet=1).count()
    ar_gor_kadin = ar_gor_total - ar_gor_erkek

    engelli_personel_total = Personel.objects.filter(engel_orani__gt=0).count()
    engelli_personel_akademik = Personel.objects.filter(engel_orani__gt=0, personel_turu=1).count()
    engelli_personel_idari = engelli_personel_total - engelli_personel_akademik
    engelli_personel_akademik_erkek = Personel.objects.filter(engel_orani__gt=0, cinsiyet=1, personel_turu=1).count()
    engelli_personel_akademik_kadin = engelli_personel_akademik - engelli_personel_akademik_erkek
    engelli_personel_idari_erkek = Personel.objects.filter(engel_orani__gt=0, cinsiyet=1, personel_turu=2).count()
    engelli_personel_idari_kadin = engelli_personel_idari - engelli_personel_idari_erkek

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
        "engelli_personel_akademik": engelli_personel_akademik,
        "engelli_personel_akademik_erkek": engelli_personel_akademik_erkek,
        "engelli_personel_akademik_kadin": engelli_personel_akademik_kadin,
        "engelli_personel_idari": engelli_personel_idari,
        "engelli_personel_idari_erkek": engelli_personel_idari_erkek,
        "engelli_personel_idari_kadin": engelli_personel_idari_kadin
    }

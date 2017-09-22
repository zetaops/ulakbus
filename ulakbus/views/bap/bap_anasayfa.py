# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus import settings
from ulakbus.models import BAPDuyuru
from ulakbus.models import BAPSatinAlma

from zengine.views.crud import CrudView
from zengine.lib.translation import gettext as _


class BAPAnasayfa(CrudView):
    def anasayfa_goster(self):
        self.output['menu'] = {
            "title": _(u"Menü"),
            "items": [
                {
                    "text": _(u"Anasayfa"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_anasayfa"
                },
                {
                    "text": _(u"Projeler"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_proje_arama"
                },
                {
                    "text": _(u"Yardım"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_hakkinda"
                },
                {
                    "text": _(u"Belgeler"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_hakkinda"
                },
                {
                    "text": _(u"Mevzuat"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_hakkinda"
                },
                {
                    "text": _(u"BAP Komisyonu"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_komisyon_uyeleri"
                },
                {
                    "text": _(u"BAP Hakkında"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_hakkinda"
                },
                {
                    "text": _(u"BAP Raporları"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_hakkinda"
                },
                {
                    "text": _(u"İletişim"),
                    "hasChild": False,
                    "param": "id",
                    "wf": "bap_iletisim"
                }
            ]
        }
        self.output['top_action_buttons'] = [
            {
                "text": _(u"Yeni Başvuru"),
                "param": "id",
                "wf": "bap_proje_basvuru"
            },
            {
                "text": _(u"Başvurum Ne Durumda"),
                "param": "id",
                "wf": "bap_ogretim_uyesi_basvuru_listeleme"
            },
            {
                "text": _(u"Makina, Teçhizat Ara"),
                "param": "id",
                "wf": "bap_makine_techizat_ara"
            },
            {
                "text": _(u"Proje Arşivi Ara"),
                "param": "id",
                "wf": "bap_proje_arama"
            },
            {
                "text": _(u"Firma Kayıt"),
                "param": "id",
                "wf": "bap_firma_kayit"
            }
        ]
        bidding_announcements = []
        for sa in BAPSatinAlma.objects.all(duyuruda=True).order_by('teklife_acilma_tarihi'):
            bidding_announcements.append({
                "text": sa.ad,
                "object_id": sa.key,
                "wf": 'bap_satin_alma_duyuru_goruntule'
            })

        self.output['bidding'] = {
           "announcements": bidding_announcements,
           "more": {
               "text": _(u"Daha Fazla..."),
               "wf": "bap_satin_alma_duyuru_listele"
           }
        }
        announcements = []
        for an in BAPDuyuru.objects.all(yayinlanmis_mi=True).order_by('eklenme_tarihi'):
            announcements.append({
                "text": an.duyuru_baslik,
                "object_id": an.key,
                "wf": "bap_duyurulari_goruntule"
            })
        self.output['general'] = {
           "announcements": announcements,
           "more": {
               "text": _(u"Daha Fazla..."),
               "wf": "bap_duyurulari_goruntule"
           }
        }
        self.output['university_title'] = settings.UNIVERSITY_NAME
        self.output['university_logo'] = settings.UNIVERSITY_LOGO


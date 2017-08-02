# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import BAPEtkinlikProje
from ulakbus.views.bap.bap_etkinlik_basvuru_inceleme import EtkinlikBasvuruInceleForm

from zengine.forms import fields
from zengine.views.crud import CrudView, list_query, obj_filter
from zengine.lib.translation import gettext as _


class OEEtkinlikBasvuruListeleme(CrudView):
    """
    Öğretim üyesinin etkinlik başvurularını listeleyeceği, başvuruları bireysel olarak
    görüntüleyebileceği, seçilen başvuru için dekanlık izin dilekçesi çıkarabileceği iş akışı
    adımıdır.
    """

    class Meta:
        allow_search = True
        model = 'BAPEtkinlikProje'

    def __init__(self, current=None):
        CrudView.__init__(self, current)
        self.ListForm.add = None

    def listele(self):
        """
        Öğretim üyesinin yapmış olduğu etkinlik başvurularını incelediği adımdır.
        """
        self.list(list_fields=['bildiri_basligi', 'durum'])

    def goruntule(self):
        """
        Öğretim üyesinin yapmış olduğu etkinlik başvurusunu detaylı olarak görüntülediği adımdır.
        """
        key = self.input['object_id']
        self.show()
        form = EtkinlikBasvuruInceleForm(title=_(u"Etkinlik Başvuru Detayları"))
        form.listeye_don = fields.Button(_(u"Listeye Dön"))
        butceler = BAPEtkinlikProje.objects.get(key).EtkinlikButce
        for butce in butceler:
            form.Butce(talep_turu=butce.talep_turu, istenen_tutar=butce.istenen_tutar)
        self.form_out(form)
        self.current.output["meta"]["allow_actions"] = False
        self.current.output["meta"]["allow_add_listnode"] = False

    def dilekce_olustur(self):
        """
        Öğretim üyesinin dekanlık izin dilekçesini oluşturduğu adımdır.
        """
        self.set_client_cmd('download')
        # todo: Döküman classı yazılınca oradan donecek url buraya taşınacak
        self.current.output['download_url'] = "FILE_URL_FROM_DOCUMENT_CLASS"

    @obj_filter
    def basvuru_islemleri(self, obj, result, **kwargs):
        """
        Default action buttonlar, öğretim üyesinin etkinlik basvurusundaki eylemlerine göre
        düzenlenmiştir.
        """
        result['actions'] = [
            {'name': _(u'Görüntüle'), 'cmd': 'goruntule', 'mode': 'normal', 'show_as': 'button'},
            {'name': _(u'Dilekçe Oluştur'), 'cmd': 'dilekce', 'mode': 'normal', 'show_as': 'button'}
        ]


    @list_query
    def list_by_personel_id(self, queryset):
        """
        Öğretim üyesinin kendi etkinlikleri filtrelenmiştir.
        """
        return queryset.filter(basvuru_yapan=self.current.user.personel.okutman)


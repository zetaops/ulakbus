# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.forms import JsonForm, fields
from zengine.lib.translation import gettext as _, gettext_lazy as __
from collections import OrderedDict
from ulakbus.views.bap.bap_basvuru_inceleme import BasvuruInceleme


class ProjeOzetForm(JsonForm):
    """
    Öğretim görevlisisin projeyi detaylı incelemesini sağlayan form.
    """
    listeye_don = fields.Button(_(u"Listeye Dön"), cmd='listeye_don')
    detay = fields.Button(_(u"Detay"), cmd='detay')


class OgrGenelProjeForm(JsonForm):
    """
    Öğretim görevlisinin projeyi incelerken kategoriler arasında geçiş
    yapabileceği form.

    """
    genel = fields.Button(_(u"Genel"), cmd='genel')
    detay = fields.Button(_(u"Detay"), cmd='olanak')
    butce = fields.Button(_(u"Bütçe"), cmd='butce_plani')
    proje_calisanlari = fields.Button(_(u"Proje Çalışanları"), cmd='proje_calisanlari')
    is_plani = fields.Button(_(u"İş Planı"), cmd='is_plani')
    listeye_don = fields.Button(__(u"Listeye Dön"), cmd='iptal')


class OgrBasvuruInceleme(BasvuruInceleme):
    class Meta:
        model = "BAPProje"

    def __init__(self, current):
        BasvuruInceleme.__init__(self, current)
        self.genel_form = OgrGenelProjeForm

    def proje_ozet_goster(self):
        """
        Proje hakkında genel bilgileri gösterir.

        """
        proje_ozeti = OrderedDict([
            ('Proje Adı', self.object.ad),
            ('Proje Yürütücüsü', self.object.yurutucu.__unicode__()),
            ('Proje Süresi(Ay)', str(self.object.sure)),
            ('Teklif Edilen Bütçe', str(self.object.teklif_edilen_butce)),
            ('Anahtar Kelimeler', self.object.anahtar_kelimeler),
            ('Konu ve Kapsam', self.object.konu_ve_kapsam),
        ])
        self.output['object'] = proje_ozeti
        self.form_out(ProjeOzetForm(title=__('Proje Özeti')))

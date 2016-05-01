# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
#
# Personele ait hizmet kayıtlarının gösterilmesini ve yazdırılmasını içeren WF
from ulakbus.models.personel import Personel
from ulakbus.views.personel.crud_hitap import zato_service_selector
from ulakbus.views.reports.base import Reporter
from zengine.forms import fields
from ulakbus.models.hitap import HizmetKayitlari
from collections import OrderedDict
import datetime

from zengine.views.crud import view_method


class ReportWithSync(Reporter.ReportForm):
    """
    HITAP Sync eklenmis rapor formu.
    """
    printout = fields.Button("Yazdır", cmd="printout")
    sync = fields.Button("HITAP ile senkronize et", cmd="sync")

class HizmetCetveli(Reporter):
    TITLE = "Hizmet Cetveli Listesi"

    def __init__(self, current=None):
        self.ReportForm = ReportWithSync
        super(HizmetCetveli, self).__init__(current)

        if self.cmd == 'sync':
            self.sync()

    def get_objects(self):
        if 'id' in self.input:
            self.current.task_data['personel_id'] = self.input['id']
            self.current.task_data['personel_tckn'] = Personel.objects.get(self.input['id']).tckn

        hk_list = []
        for hk in HizmetKayitlari.objects.filter(personel_id=self.current.task_data['personel_id']).order_by('order_date'):
                hk_record = OrderedDict({})
                hk_record['Görevleri'] = hk.gorev.title()
                hk_record['H. Sınıf'] = hk.get_hizmet_sinifi_display()
                hk_record['K. Der.'] = str(hk.kadro_derece)
                hk_record['G. A.'] = "%i/%i" % (hk.odeme_derece,hk.odeme_kademe)
                hk_record['K. H.'] = "%i/%i" % (hk.kazanilmis_hak_ayligi_derece,hk.kazanilmis_hak_ayligi_kademe)
                hk_record['E. M.'] = "%i/%i" % (hk.emekli_derece,hk.emekli_kademe)
                hk_record['Başlangıç Tar.'] = str(hk.baslama_tarihi) if hk.baslama_tarihi!=datetime.date(1900,1,1) else ''
                hk_record['Bitiş Tar.'] = str(hk.bitis_tarihi) if hk.bitis_tarihi!=datetime.date(1900,1,1) else ''
                hk_record['Sebep'] = str(hk.sebep_kod)
                hk_list.append(hk_record)
        return hk_list

    def sync(self):
        hitap_service = zato_service_selector(HizmetKayitlari, 'sync')
        hs = hitap_service(tckn=str(self.current.task_data['personel_tckn']))
        hs.zato_request()

    def clear_cmd(self):
        self.current.input['cmd'] = 'show'
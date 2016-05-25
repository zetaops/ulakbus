# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from ulakbus.models import User, Personel
from zengine.lib.test_utils import BaseTestCase


class TestCase(BaseTestCase):

    def test_terfisi_gelen_personel(self):

        usr = User.objects.get(username='personel_isleri_1')
        self.prepare_client('/terfisi_gelen_personel_listesi', user=usr)
        self.client.post()
        idari_forms = {'baslangic_tarihi': '20.05.2016',
                       'bitis_tarihi': '30.05.2016',
                       'devam': 1,
                       'personel_turu': 2}
        resp = self.client.post(form=idari_forms)
        ter_gel_id_per = resp.json['forms']['model']['Personel']
        assert len(ter_gel_id_per) == 13

        idari_per_db = len(Personel.objects.filter(personel_turu=2))

        assert idari_per_db - len(ter_gel_id_per) == 7

        ter_gel_id_per[1]['sec'] = True
        ter_gel_id_per[5]['sec'] = True

        terfi_duz_forms = {'Personel': ter_gel_id_per,
                           'duzenle': 1}

        resp = self.client.post(cmd="terfi_liste_duzenle", form=terfi_duz_forms)

        resp.json['forms']['model']['Personel'][0]['yeni_gorev_ayligi_derece'] = 2
        resp.json['forms']['model']['Personel'][1]['yeni_kazanilmis_hak_derece'] = 3

        ter_gel_id_per = resp.json['forms']['model']['Personel']

        resp = self.client.post(cmd='kaydet', form={'Personel': ter_gel_id_per,
                                             'devam': 1})

        ter_gel_id_per = resp.json['forms']['model']['Personel']

        assert ter_gel_id_per[1]['yeni_gorev_ayligi'] == '2/7(7)' and\
               ter_gel_id_per[5]['yeni_kazanilmis_hak'] == '3/5(5)'

        resp = self.client.post(cmd='onaya_gonder', form={'Personel': ter_gel_id_per,
                                                          'kaydet': 1})

        assert resp.json['msgbox']['title'] == "Personeller Onay Icin Gonderildi!"
        self.client.set_path('/logout')

        usr = User.objects.get(username='genel_sekreter_1')
        self.prepare_client('/terfisi_gelen_personel_listesi', user=usr)
        resp = self.client.post()

        assert len(resp.json['forms']['model']['Personel']) == len(ter_gel_id_per)

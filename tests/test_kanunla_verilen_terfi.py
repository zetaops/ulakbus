#-*- coding: utf-8 -*-
"""
"""

#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.lib.test_utils import BaseTestCase
from zengine.messaging.model import Message
from ulakbus.models import User, Personel
import time
import random

class TestCase(BaseTestCase):

    def terfi_test(self):
        """
            Kanunla verilen terfi workflow'a ait testleri içerir
        Returns:

        """

        def kademe_derece_duzenle():
            """
                Parametre olarak girilen kademe değerine göre personelin
                derecesinin ne olacağını return eder.
            """

            if terfi_form["ga_kademe"] >= 3:
                terfi_form["ga_kademe"] = 1
                terfi_form["ga_derece"] -= 1
            else:
                terfi_form["ga_kademe"] += 1

            if terfi_form["kh_kademe"] >= 3:
                terfi_form["kh_kademe"] = 1
                terfi_form["kh_derece"] -= 1
            else:
                terfi_form["kh_kademe"] += 1

            if terfi_form["em_kademe"] >= 3:
                terfi_form["em_kademe"] = 1
                terfi_form["em_derece"] -= 1
            else:
                terfi_form["em_kademe"] += 1



        usr = User.objects.get(username='mithat')
        personel = Personel.objects.filter()[random.randint(0,3000)]
        self.prepare_client('kanunla_verilen_terfi', user=usr)
        self.client.post()

        terfi_form = {
            "ga_kademe" : personel.gorev_ayligi_kademe,
            "ga_derece" : personel.gorev_ayligi_derece,
            "kh_kademe" : personel.kazanilmis_hak_kademe,
            "kh_derece" : personel.kazanilmis_hak_derece,
            "em_kademe" : personel.emekli_muktesebat_kademe,
            "em_derece" : personel.emekli_muktesebat_derece
        }

        kademe_derece_duzenle()

        resp = self.client.post(cmd="terfi_kaydet", form=terfi_form)

        assert resp.json["msgbox"]["title"]
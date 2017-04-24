#-*- coding: utf-8 -*-
"""
"""

#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.lib.test_utils import BaseTestCase
from zengine.messaging.model import Message
from ulakbus.models import User, Personel, HitapSebep
import time
import random

class TestCase(BaseTestCase):

    def test_terfi(self):
        """
            Kanunla verilen terfi workflow'a ait testleri içerir
        Returns:

        """

        def kademe_derece_duzenle(terfi_form):
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
        personel_id = personel.key
        self.prepare_client('kanunla_verilen_terfi', user=usr)
        self.client.post(cmd="terfi_form", id=personel.key)
        mesaj_sayisi = Message.objects.count()

        terfi_form = {
            "ga_kademe" : personel.gorev_ayligi_kademe,
            "ga_derece" : personel.gorev_ayligi_derece,
            "kh_kademe" : personel.kazanilmis_hak_kademe,
            "kh_derece" : personel.kazanilmis_hak_derece,
            "em_kademe" : personel.emekli_muktesebat_kademe,
            "em_derece" : personel.emekli_muktesebat_derece
        }

        kademe_derece_duzenle(terfi_form)

        self.client.post(cmd="terfi_bilgileri_kaydet", form=terfi_form)

        hizmet_cetveli_form = {
            "terfi_sebep_id" : HitapSebep.objects.get(sebep_no=6),
            "baslama_tarihi" : "10.04.2017",
            "bitis_tarihi" : "25.04.2017",
            "kurum_onay_tarihi" : "09.04.2017"
        }

        resp = self.client.post(cmd="hizmet_cetveli_kayit")

        assert resp.json["msgbox"]["title"] == u'Onaya Gönderildi'

        assert Message.objects.count() == mesaj_sayisi +1

        mesaj_sayisi += 1

        # Terfisi yapılan personel eğer idari personel ise onay makamı genel sekreterliktir.
        # Terfisi yapılan personel eğer akademik personel ise onay makamı rektörlüktür.

        if personel.personel_turu == 1:
            usr = User.objects.get(username='rektor')
        else:
            usr = User.objects.get(username='genel_sekreter')

        self.prepare_client('kanunla_verilen_terfi', user=usr)

        resp = self.client.post(cmd='terfi_kaydet')

        assert resp.json["msgbox"]["title"] == u"Terfi İşlemi Gerçekleştirildi"

        assert Message.objects.count() == mesaj_sayisi + 2

        personel = Personel.objects.get(personel_id)

        assert personel.gorev_ayligi_kademe == terfi_form["ga_kademe"]

        assert personel.gorev_ayligi_derece == terfi_form["ga_derece"]

        assert personel.kazanilmis_hak_kademe == terfi_form["kh_kademe"]

        assert personel.kazanilmis_hak_derece == terfi_form["kh_derece"]

        assert personel.emekli_muktesebat_kademe == terfi_form["em_kademe"]

        assert personel.emekli_muktesebat_derece == terfi_form["em_derece"]
# -*-  coding: utf-8 -*-
#
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.models import Demirbas, DemirbasRezervasyon
from zengine.lib.test_utils import BaseTestCase
from ulakbus.models.auth import User
from ulakbus.models.personel import Personel


class TestCase(BaseTestCase):

    def test_demirbas(self):
        user = User.objects.get(username="ulakbus")
        self.prepare_client('/demirbas', user=user)
        self.client.post()

        demirbas_sayisi_baslangic = Demirbas.objects.count()

        # Demirbaş ekle
        self.client.post(cmd='add_edit_form')

        form = {
            'ad': "Sandalye",
            'birim_id': "M2bJNCtvMmzCNnvG8BpFISK6KTs",
            'demirbas_no': "123qwe",
            'kurum_kodu': "123qwe",
            'marka': "marka",
            'model': "model",
            'muhasebe_kodu': "123qwe",
            'notlar': "notlar",
            'olculer': "12x22x32",
            'satin_alinma_fiyati': 650,
            'satin_alinma_tarihi': "24.03.2017",
            'teslim_alinma_tarihi': "24.03.2017",
            'tur': "Mobilya",
            'url': "asd.com",
            'yeri': "Oda"
        }

        self.client.post(form=form)

        demirbas_sayisi_ekleme_sonrasi = Demirbas.objects.count()

        assert demirbas_sayisi_ekleme_sonrasi == demirbas_sayisi_baslangic + 1

        d = Demirbas.objects.get(ad="Sandalye")

        # Bemirbaş düzenle
        self.client.post(object_id=d.key, cmd='add_edit_form')

        onceki_marka = form['marka']
        form['marka'] = "Bir başka marka"

        self.client.post(form=form)

        d = Demirbas.objects.get(ad="Sandalye")

        assert d.marka != onceki_marka

        # Görüntüle

        self.client.post(object_id=d.key, cmd='goster')

        self.client.post(object_key=d.key, cmd='rezervasyon')

        rezervasyon_sayisi_baslangic = DemirbasRezervasyon.objects.filter(
            rezerve_edilen_demirbas=d).count()

        form = {
            'rezervasyon_baslama_tarihi': "22.3.2017",
            'rezervasyon_bitis_tarihi': "29.3.2017",
            'rezerve_eden_id': "1goyiKX6pME423arQBIdrY6ETao"
        }

        resp = self.client.post(form=form, cmd='kaydet_ve_kontrol')

        assert resp.json['forms']['schema']['title'] == "Rezervasyon Kaydı Başarılı"

        assert DemirbasRezervasyon.objects.filter(rezerve_edilen_demirbas=d).count() == \
               rezervasyon_sayisi_baslangic + 1

        self.client.post(object_id=d.key, cmd='goster')

        self.client.post(object_key=d.key, cmd='rezervasyon')

        form = {
            'rezervasyon_baslama_tarihi': "23.3.2017",
            'rezervasyon_bitis_tarihi': "28.3.2017",
            'rezerve_eden_id': "1goyiKX6pME423arQBIdrY6ETao"
        }

        resp = self.client.post(form=form, cmd='kaydet_ve_kontrol')

        assert DemirbasRezervasyon.objects.filter(rezerve_edilen_demirbas=d).count() == \
               rezervasyon_sayisi_baslangic + 1

        self.prepare_client('/demirbas', user=user)
        self.client.post()

        # Demirbaş Sil
        self.client.post(object_id=d.key, cmd='confirm_deletion')

        self.client.post(cmd='delete')

        assert demirbas_sayisi_baslangic == Demirbas.objects.count()

        DemirbasRezervasyon.objects.filter(rezerve_edilen_demirbas=d).delete()







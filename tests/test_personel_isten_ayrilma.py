# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko.exceptions import ObjectDoesNotExist
from ulakbus.models import Personel, Role
from zengine.lib.test_utils import BaseTestCase
from zengine.models import WFInstance, TaskInvitation
import pytest


class TestCase(BaseTestCase):
    def test_personel_isten_ayrilma(self):
        personel_id = "1goyiKX6pME423arQBIdrY6ETao"
        task_invitation_key = '48hKXEfHUoHVr7Tcq3n0vwTJVGi'
        wf_instance_key = 'WAm11pIPnF5va2bBKpc19uT8t7z'
        personel = Personel.objects.get(personel_id)
        onceki_isten_ayrilma_bilgileri_sayisi = len(personel.IstenAyrilma)
        silinecek_rol = personel.user.role_set[0].role
        yeni_rol_key = 'LTTdUyzC62KdGoP770GhTlOZq5p'    # personel_isleri_2

        assert not silinecek_rol.deleted

        wf_instance = WFInstance.objects.get(wf_instance_key)

        assert wf_instance.current_actor == silinecek_rol

        task_inv = TaskInvitation.objects.get(task_invitation_key)

        assert task_inv.role == silinecek_rol

        for i in range(2):
            self.prepare_client("personel_isten_ayrilma", username='personel_isleri_1')
            resp = self.client.post(id=personel_id, model="Personel", param="personel_id",
                                    wf="personel_isten_ayrilma")
            if 'IstenAyrilmaBilgileri' in resp.json['forms']['model']:
                assert len(resp.json['forms']['model']['IstenAyrilmaBilgileri']) == \
                    onceki_isten_ayrilma_bilgileri_sayisi
            else:
                assert resp.json['forms']['form'][0]['helpvalue'] == \
                       u"Personele ait silinmiş kayıt bulunmamaktadır."

            self.client.post(form={'isten_ayril': 1})

            personel_ayrilma_form = {'notlar': 'Vasıfsız eleman',
                                     'ayrilma_tarih': '25.01.2017',
                                     'ayrilma_sebeb': 'Ss2cdtxjID1n9kV7dw0dDiAIIKf',
                                     'devam_buton': 1}

            resp = self.client.post(wf="personel_isten_ayrilma", form=personel_ayrilma_form)

            assert resp.json['forms']['schema']['title'] == u'Çisem Güçlü personelini silme işlemi'

            if i == 0:
                self.client.post(wf='personel_isten_ayrilma', form={'hayir': 1}, flow='iptal')
            else:
                self.client.post(wf='personel_isten_ayrilma', form={'evet': 1})
                resp = self.client.post(wf="personel_isten_ayrilma", form={
                    'YeniRoller': [{'eski_role': "Daire Personeli | personel_isleri_7",
                                    'wf_name': "terfisi_gelen_personel_listesi",
                                    'yeni_role': yeni_rol_key}],
                    'bitir_buton': 1,

                })

                assert resp.json['msgbox']['title'] == u'Ayrılma İşlemi Başarıyla Gerçekleşti'
                assert resp.json['msgbox']['msg'] == u'Çisem Güçlü adlı personel işten ayrıldı.'

        self.prepare_client("personel_isten_ayrilma", username='personel_isleri_1')
        resp = self.client.post(id=personel_id, model="Personel", param="personel_id",
                                wf="personel_isten_ayrilma")

        assert len(resp.json['forms']['model']['IstenAyrilmaBilgileri']) == \
            onceki_isten_ayrilma_bilgileri_sayisi + 1

        wf_instance.reload()
        task_inv.reload()
        personel.reload()
        deleted_role = personel.user.role_set[0].role
        yeni_role = Role.objects.get(yeni_rol_key)

        assert wf_instance.current_actor.key == yeni_role.key
        assert task_inv.role.key == yeni_role.key

        with pytest.raises(ObjectDoesNotExist):
            Role.objects.get(deleted_role.key)
        assert personel.arsiv

        personel.arsiv = False
        personel.notlar = ''
        personel.save()

        r = Role.objects.filter(key=deleted_role.key, deleted=True)[0]
        r.deleted = False
        r.deleted_at = None
        r.blocking_save()

        wf_instance.current_actor = r
        wf_instance.blocking_save()

        task_inv.role = r
        task_inv.blocking_save()

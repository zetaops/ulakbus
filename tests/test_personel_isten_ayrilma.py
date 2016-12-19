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
        """
            Bir personel seçilir ve işten ayrılma wf adımları işletilir.
        """
        # Personele ait workflow instance key
        wf_instance_key = 'WAm11pIPnF5va2bBKpc19uT8t7z'
        # Personele ait task invitation key
        task_invitation_key = 'WfetcaKmDsIE6RrIeRUoBaj4ypQ'
        # İşten ayrılacak personelin id si
        personel_id = "RngBQlVfKwyFHcqcmXRvlxipK6x"

        self.prepare_client("personel_isten_ayrilma", username='personel_isleri_2')

        personel = Personel.objects.get(personel_id)

        deleted_role = personel.user.role_user_set[0].role

        assert not deleted_role.deleted

        wf_instance = WFInstance.objects.get(wf_instance_key)
        assert wf_instance.current_actor == deleted_role

        task_inv = TaskInvitation.objects.get(task_invitation_key)
        assert task_inv.role == deleted_role

        # İşten ayrılacak olan personel seçilir
        self.client.post(id=personel_id, model="Personel", param="personel_id",
                         wf="personel_isten_ayrilma")

        # İşten ayrılma onayı
        aciklama = "İlgili personel işten ayrılmıştır. Onaylanmıştır"
        self.client.post(wf="personel_isten_ayrilma", form=dict(notlar=aciklama,
                                                                devam_buton=1))

        # İlgili personelin bilgileri kontrol amacıyla veritabanından çekilir
        personel.reload()

        # İşten ayrılma işleminin yapılıp yapılmadığının kontrolü
        assert personel.notlar == aciklama

        resp = self.client.post(wf="personel_isten_ayrilma", form={
            'YeniRoller': [{'eski_role': "Daire Personeli | personel_isleri_1",
                            'wf_name': "terfisi_gelen_personel_listesi",
                            'yeni_role': "LTTdUyzC62KdGoP770GhTlOZq5p"}],
            'bitir_buton': 1,

        })

        yeni_role = Role.objects.get('LTTdUyzC62KdGoP770GhTlOZq5p')

        assert resp.json['msgbox']['msg'] == "Personel işten ayrıldı"

        wf_instance.reload()
        task_inv.reload()
        personel.reload()
        deleted_role = personel.user.role_user_set[0].role

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

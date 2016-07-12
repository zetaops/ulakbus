# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

__author__ = 'Mithat Raşit Özçıkrıkcı'

from ulakbus.models import User, Personel
from zengine.lib.test_utils import BaseTestCase

class TestCase(BaseTestCase):
    def test_personel_isten_ayrilma(self):
        """
            Bir personel seçilir ve işten ayrılma wf adımları işletilir.
        """

        user_id = "UuXR8pmKQNzfaPHB2K5wxhC7WDo"
        user = User.objects.get(user_id)
        self.prepare_client("personel_isten_ayrilma", user=user)

        # İşten ayrılacak personelin id si
        personel_id = "Gf4QZ29j93N4B3a7T5CXlW0V7WA"

        # İşten ayrılacak olan personel seçilir
        self.client.post(id=personel_id, model="Personel", param="personel_id", wf="personel_isten_ayrilma")

        # İşten ayrılma onayı
        aciklama = "İlgili personel işten ayrılmıştır. Onaylanmıştır"
        self.client.post(cmd="onayla", wf="personel_isten_ayrilma", form=dict(notlar=aciklama))

        # İlgili personelin bilgileri kontrol amacıyla veritabanından çekilir
        personel = Personel.objects.get(personel_id)

        # İşten ayrılma işleminin yapılıp yapılmadığının kontrolü
        assert personel.arsiv
        assert personel.notlar == aciklama
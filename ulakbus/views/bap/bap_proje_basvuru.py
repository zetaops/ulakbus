# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.views.crud import CrudView


class ProjeBasvuru(CrudView):
    class Meta:
        model = "BAPProje"

    def proje_bilgisi_gir(self):
        pass

    def hata_mesaji_goster(self):
        pass

    def proje_sonucu_goster(self):
        pass

    def proje_bilgilerini_kontrol_et(self):
        pass

    def ogretim_uyesine_hata_geri_bildirimi_gonder(self):
        pass

    def ogretim_uyesine_bilgilendirme_mesaji_gonder(self):
        pass

    def komisyona_sun(self):
        pass

    def proje_bilgilerini_kontrol_et_komisyon(self):
        pass

    def reddet(self):
        pass

    def onayla(self):
        pass

    def geri_bildirim_gonder(self):
        pass

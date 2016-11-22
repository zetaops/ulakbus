# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView

class UlakbusView(CrudView):

    def mesaj_kutusu_goster(self, title, msg_type='warning'):
        """
        Hatalı işlem, başarılı işlem gibi bir çok yerde kullanılan mesaj kutularını
        her defasında tanımlamak yerine bu method yardımıyla kullanılmasını sağlar.
        Current task data içerisinde 'msg' olduğunu varsayar ve bu mesajı gösterir.
        Default msgbox type'ı warning olarak belirlenmiştir.

        Args:
            title (string): Mesaj kutusunun başlığı
            type (string): Mesaj kutusunun tipi (warning, info)

        """
        self.current.output['msgbox'] = {
            'type': msg_type, "title": title,
            "msg": self.current.task_data['msg']}
        self.current.task_data['msg'] = None
# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.views.crud import CrudView

class DigerViews(CrudView):
    def bap_yardim(self):
        msg = "Yardım alanı kurum tarafından eklenecektir."
        title = "Bap Yardım"
        self.current.msg_box(msg=msg, title=title)

    def bap_belgeler(self):
        msg = "İlgili BAP belgeleri kurum tarafından sisteme eklenecektir."
        title = "Bap Belgeler"
        self.current.msg_box(msg=msg, title=title)

    def bap_mevzuat(self):
        msg = "Mevzuat bilgisi kurum tarafından sisteme eklenecektir."
        title = "Bap Mevzuat"
        self.current.msg_box(msg=msg, title=title)

    def bap_hakkinda(self):
        msg = "Hakkında bilgisi kurum tarafından sisteme eklenecektir."
        title = "BAP Hakkında"
        self.current.msg_box(msg=msg, title=title)

    def bap_raporlari(self):
        msg = "BAP raporları kurum tarafından sisteme eklenecektir."
        title = "BAP Raporları"
        self.current.msg_box(msg=msg, title=title)

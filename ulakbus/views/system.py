# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from zengine.views.base import SimpleView


class Menu(SimpleView):
    def show_view(self):
        self.output = {
            'personel': [
                ['İzinler', '/crud/Izin']
            ],
            'ogrenci': [],
            'genel': [
                ['Personel', '/crud/Personel'],

            ]
        }


# -*-  coding: utf-8 -*-
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model
from zengine.forms import fields
from . import RoomType, Okutman, Room, Sube


class DersEtkinligi(Model):
    solved = fields.Boolean()
    unitime_id = fields.Integer() #class id
    unit_yoksis_no = fields.Integer()
    room_type = RoomType()
    okutman = Okutman("Ogretim Elemani")
    sube = Sube()

    # to be calculated
    room = Room()
    gun = fields.String("Gun")
    baslangic_saat = fields.String("Baslangic Saat")
    baslangic_dakika = fields.String("Baslangic Dakika")
    bitis_saat = fields.String("Bitis Saat")
    bitis_dakika = fields.String("Bitis Dakika")

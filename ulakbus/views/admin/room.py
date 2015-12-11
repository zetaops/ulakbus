# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.


from pyoko import form
from zengine.views.crud import CrudView, obj_filter

from zengine.lib.forms import JsonForm
from ulakbus.models.buildings_rooms import RoomFeature, RoomOption, ROOM_FEATURE_TYPES, Room, OPTIONS, VALUE

__author__ = 'Ali Riza Keles'


class FeatureForm(JsonForm):
    features = RoomFeature.objects.filter()
    feature_choices = []
    for f in features:
        feature_choices.append((f.key, f.feature_name))

    # Select from existing features
    features = form.Integer(choices=program_choices)
    sec = form.Button("Sec", cmd="select_val")

    # or save a new feature
    feature = form.Integer("Yeni Ozellik", choices=ROOM_FEATURE_TYPES)
    type = form.Integer("Type", choices=ROOM_FEATURE_TYPES)
    save = form.Button("Kaydet", cmd="save_new_feature")


class OptionForm(JsonForm):
    val_00 = form.String("Val")
    val_01 = form.String("Val")
    val_02 = form.String("Val")
    val_03 = form.String("Val")
    val_04 = form.String("Val")
    val_05 = form.String("Val")
    val_06 = form.String("Val")
    val_07 = form.String("Val")
    val_08 = form.String("Val")
    val_09 = form.String("Val")
    kaydet = form.Button("Kaydet", cmd="save_options")


class RoomFeatures(CrudView):
    class Meta:
        # CrudViev icin kullanilacak temel Model
        model = 'RoomFeatureOptionVals'

    def select_feature(self):
        self.form_out(FeatureForm(current=self.current))

    def save_new_feature(self):
        new_feature = RoomFeature()
        new_feature.feature_name = self.current.input['feature']
        new_feature.type = self.current.input['type']
        new_feature.save()

    def select_feature_options(self):
        if new_feature.type == OPTIONS:
            self.form_out(OptionForm(current=self.current))
        else:
            self.current

    def select_val(self):
        self.current.input['selected_feature'] = self.current.task_data['']


class Room(CrudView):
    class Meta:
        model = 'Room'

    @obj_filter
    def room_features(self, result):
        result['actions'].extend([{'name': 'Oda Ozellikleri', 'wf': 'room_features', 'show_as': 'button'}])
        return result

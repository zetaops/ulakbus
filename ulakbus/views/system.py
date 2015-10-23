# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from collections import defaultdict
from pyoko.model import model_registry
from zengine.auth.permissions import get_workflows
from zengine.views.base import BaseView
from zengine.config import settings


class Menu(BaseView):
    def __init__(self, current):
        super(Menu, self).__init__(current)
        self.output = self.get_crud_menus()
        self.output['genel'].update(self.get_workflow_menus())


def get_crud_menus(self):
    results = defaultdict(list)
    for user_type in settings.CRUD_MENUS:
        for model_data in settings.CRUD_MENUS[user_type]:
            model = model_registry.get_model(model_data['name'])
            field_name = model_data['field'] if 'field' in model_data else user_type
            verbose_name = (model_data['verbose_name'] if 'verbose_name' in model_data
                            else model.Meta.verbose_name_plural)
            crud_path = 'crud/%s/?%s=' % (model_data['name'], field_name)
            results[user_type].append((verbose_name, crud_path))
    return dict(results)


def get_workflow_menus(self):
    get_wf_menu = lambda: (wf.spec.wf_name, '/%s?id=' % wf.spec.name)
    results = defaultdict(list)
    for wf in get_workflows():
        if 'object' in wf.spec.wf_properties:
            results[wf.spec.wf_properties['object']].append(get_wf_menu())
        else:
            results['genel'].append(get_wf_menu())
    return dict(results)

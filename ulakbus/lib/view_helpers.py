# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from datetime import datetime
from ulakbus.lib.common import guncel_donem_degiskenlerini_getir
from ulakbus.models.ogrenci import Donem
def prepare_choices_for_model(model, **kwargs):
    """Model için Seçenekler Hazırla

    Args:
        model: Model
        **kwargs: Keyword argümanları

    Returns:
        Keyword argümanlara göre filtrelenmiş modelin,
        key ve __unicode__ method değerlerini

    """

    return [(m.key, m.__unicode__()) for m in model.objects.filter(**kwargs)]


def convert_model_object_titlemap_item(m):
    """
    Callable nesneler ile titlemap uretirken, callable method geriye name, value
    keylerine sahip bir dict dondurmeli. Bu method verilen nesnenin key ve unicode
    methodlarindan bir dict dondurur.

    Args:
        m (Model): model instance
    Returns:
        (dict) name value keyleri ve karsilik gelen degerlerden olusan dict

    """
    return {"name": m.__unicode__(), "value": m.key}

class WFValues(object):
    """
    WF çalıştırılırken wf current'ının task_data'sına başlangıçta istenilen dataların konulmasını
    sağlayan method. Böylelikle tüm adımlar aynı datayı kullanır tutarsızlık ortadan kalkar.
    """
    def assign_wf_initial_values(self,current):

        donem_fields = guncel_donem_degiskenlerini_getir(Donem.guncel_donem())
        current.task_data['wf_initial_values'] = {'guncel_donem': donem_fields,
                                                  'started': True,
                                                  'start_date': datetime.now().strftime(
                                                      "%Y-%m-%d %H:%M:%S"),
                                                  'finish_date': None,
                                                  'finished': False}
# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from datetime import datetime
from ulakbus.lib.cache import GuncelDonem, ChoicesFromModel
import hashlib


def prepare_choices_for_model(model, **kwargs):
    """Model için Seçenekler Hazırla

    Args:
        model: Model
        **kwargs: Keyword argümanları

    Returns:
        Keyword argümanlara göre filtrelenmiş modelin,
        key ve __unicode__ method değerlerini

    """
    kw_string = "".join(["%s%s" % (k, v) for k, v in sorted(kwargs.items())])
    cache_key = hashlib.sha256("%s:%s" % (model._get_bucket_name(), kw_string)).hexdigest()

    cache = ChoicesFromModel(cache_key)
    return cache.get() or cache.set(
        [(m.key, m.__unicode__()) for m in model.objects.order_by().all(**kwargs)],
        lifetime=3600
    )


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
    WF başlangıcında, tüm iş akışı boyunca kullanılacak dataların
    set edilmesini sağlayan methodları içeren class.
    """

    @staticmethod
    def assign_wf_initial_values(current):
        """
        WF çalıştırılırken wf current'ının task_data'sına başlangıçta istenilen
        dataların konulmasını ve tüm adımlarda bu dataların kullanılmasını sağlar.

        Args:
            current (Current): current nesnesi
        """

        current.task_data['wf_initial_values'] = {
            'guncel_donem': GuncelDonem().get_or_set(),
            'started': True,
            'start_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

# -*-  coding: utf-8 -*-
"""
"""


# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

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

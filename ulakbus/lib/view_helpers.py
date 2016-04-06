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


def prepare_titlemap_for_model(model, **kwargs):
    """Model için Typeahead Seçenekleri Hazırla

    Args:
        model: Model
        **kwargs: Keyword argümanları

    Returns:
        Keyword argümanlara göre filtrelenmiş modelin,
        key ve __unicode__ method değerlerini

    """

<<<<<<< a9760f6370eb487f3300775585100fc3a42ba0db
    return [(m.key, m.__unicode__()) for m in model.objects.filter(**kwargs)]
=======
    return [{"value": m.key, "name": m.__unicode__()} for m in model.objects.filter(**kwargs)]
>>>>>>> prepare_choices_for_model lib altına taşındı, referanslar düzeltildi

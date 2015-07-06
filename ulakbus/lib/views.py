# -*-  coding: utf-8 -*-
"""Base view classes"""
# -
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
__author__ = "Evren Esat Ozkan"


class BaseView(object):
    """
    this class constitute a base for all view classes.
    """
    def __init__(self, current):
        self.current = current


class SimpleView(BaseView):
    """
    simple form based views can be build  up on this class.
    we call self._do() method if client sends a 'do' command,
    otherwise show the form by calling self._show() method.

    """
    def __init__(self, current):
        super(SimpleView, self).__init__(current)
        if current['request'].context['data'].get('cmd', '') == 'do':
            self._do()
        else:
            self._show()


    def _do(self):
        """
        You should override this method in your class
        """
        raise NotImplementedError


    def _show(self):
        """
        You should override this method in your class
        """
        raise NotImplementedError

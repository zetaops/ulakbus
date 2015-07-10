# -*-  coding: utf-8 -*-
"""Base view classes"""
# -
# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from falcon import HTTPNotFound
from pyoko.model import Model

__author__ = "Evren Esat Ozkan"


class BaseView(object):
    """
    this class constitute a base for all view classes.
    """
    def __init__(self, current):
        self.current = current
        self.input = current.input
        self.output = current.output


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


class CrudView(BaseView):
    """
    A base class for "Create List Show Update Delete" type of views.

    :type object: Model | None
    """
    MODEL = Model


    def __init__(self, current):
        super(CrudView, self).__init__(current)
        self.object_id = self.input.get('object_id')
        if self.object_id:
            try:
                self.object = self.MODEL.objects.get(self.object_id)
            except:
                raise HTTPNotFound()
        else:
            self.object = None
        {
            'list': self._list,
            'show': self._show,
            'add': self._add,
            'edit': self._edit,
            'delete': self._delete,
            'save': self._save,
        }[current.input['cmd']]()


    def _show(self):
        self.output['object'] = self.object.clean_value()




    def _list(self):
        """
        You should override this method in your class
        """
        # TODO: add pagination
        # TODO: use models
        for obj in self.MODEL.objects.filter():
            data = obj.data
            self.output['objects'].append({"data": data, "key": obj.key})

    def _edit(self):
        """
        You should override this method in your class
        """
        raise NotImplementedError

    def _add(self):
        """
        You should override this method in your class
        """
        raise NotImplementedError

    def _save(self):
        """
        You should override this method in your class
        """
        raise NotImplementedError

    def _delete(self):
        """
        You should override this method in your class
        """
        raise NotImplementedError

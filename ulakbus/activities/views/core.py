# -*-  coding: utf-8 -*-
"""General Core views"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
from ulakbus.lib.views import SimpleView

from falcon.errors import HTTPBadRequest

# from ulakbus.modules.forms import get_form
# from ulakbus.modules.auth.student import authenticate


class Dashboard(SimpleView):

    def _do(self):
        self._show()
        # try:
        #     login_credentials = self.current.request.context.jsonin.login_crd
        # except KeyError:
        #     raise HTTPBadRequest("Missing login data")
        # user = authenticate(login_credentials)
        # is_login_successful = bool(user)
        # if is_login_successful:
        #     self.current.request.context.jsonout = {'success': True}
        #     self.current.request.session['user'] = user
        # self.current.task.data['is_login_successful'] = is_login_successful

    def _show(self):
        # if 'user' not in self.current.request.session:
        #     self.current.request.context['result']['forms'] = get_form(
        #         'student_login_form')
        # else:
        #     self.current.request.context[
        #         'show_user_message'] = "Zaten giriş yapmış durumdasınız"
        self.current.request.context['result']['screen'] = "dashboard"

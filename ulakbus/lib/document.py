# -*- coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from ulakbus.services.zato_wrapper import ZatoService
from ulakbus.models.document import Template
from pyoko.conf import settings
from pyoko.exceptions import ObjectDoesNotExist


class RenderDocument(ZatoService):
    """
    Render service.
    d = RenderDocument(template_name, context={'title': 'Fancy Doc Titile',
                                                            'content':'Some content'})
    print d.doc_url
    """

    def __init__(self, template_name, context=None, wants_pdf=False):
        """

        Args:
            template_name (str) : Template name on redis.
            context (dict)      : Context data for Jinja2
            wants_pdf (bool)    : Wants pdf output.
        """
        super(RenderDocument, self).__init__('document-render.render-document', None)
        self.file_name = template_name
        if context is not None:
            self.context = context
        else:
            raise ValueError("Template için gerçerli bir context belirtilmelidir.")

        self.wants_pdf = wants_pdf
        self.doc_url = ""
        self.render()

    def _get_template(self):
        """
        Get template information from database.

        Returns:
            dict: Template information.
        """
        try:
            t = Template.objects.get(name=self.file_name)
            return {"template": "{}{}".format(settings.S3_PUBLIC_URL, t.template),
                    "modify_date": "{}".format(t.modify_date)}
        except ObjectDoesNotExist:
            raise ValueError("%s geçerli bir template değildir. "
                             "Lütfen template dosyanızı kontol edin.")

    def render(self):
        """
        Make a zato_request and render document.

        Returns:
            str: Response of zato_request. It's URL of produced document.
        """
        template_info = self._get_template()

        payload = {"template": template_info['template'],
                   "context": self.context,
                   "wants_pdf": self.wants_pdf,
                   "modify_date": template_info['modify_date']
                   }

        self.payload = payload

        self.doc_url = self.zato_request()

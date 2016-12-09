#-*- coding: utf-8 -*-

from zato.common import SMTPMessage
from zato.server.service import Service
import httplib
from pyoko.lib.utils import dash_camel


class EPostaYolla(Service):

    HAS_CHANNEL = True

    @classmethod
    def get_name(cls):
        super(EPostaYolla, cls)
        return dash_camel(cls.__name__)

    def handle(self):

        default_e_mail = self.request.payload['default_e_mail']
        e_posta =self.request.payload['e_posta']
        message = self.request.payload['message']
        subject = self.request.payload['subject']

        # Obtain a connection
        conn = self.email.smtp.get('Ulakbus-Mail').conn

        # Create a regular e-mail
        msg = SMTPMessage()
        msg.subject = subject
        msg.to = e_posta
        msg.from_ = default_e_mail
        msg.body = message

        # Send the message
        conn.send(msg)

        self.response.status_code = httplib.OK
        self.response.payload = {'status': 'ok', 'result': 'Success'}
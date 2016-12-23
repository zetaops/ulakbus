#-*- coding: utf-8 -*-

from zato.common import SMTPMessage
import httplib
from ulakbus.services.ulakbus_service import UlakbusService


class EPostaYolla(UlakbusService):

    HAS_CHANNEL = True

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
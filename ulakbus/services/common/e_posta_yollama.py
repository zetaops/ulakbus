#-*- coding: utf-8 -*-

from zato.common import SMTPMessage
from zato.server.service import Service
from zengine.lib.cache import Cache
import httplib

class E_PostaYolla(Service):

    def handle(self):

        e_posta =self.request.payload['e_posta']
        message = self.request.payload['message']

        # Obtain a connection
        conn = self.email.smtp.get('Ulakbus-Mail').conn

        # Create a regular e-mail
        msg = SMTPMessage()
        msg.subject = 'Ulakbüs Aktivasyon Maili'
        msg.to = e_posta
        msg.from_ = 'postmaster@mg.ulakbus.net'
        msg.body = 'E-Posta adresinizi doğrulamak için ' \
                    'aşağıdaki linke tıklayınız:\n\n %s' % message

        # Send the message
        conn.send(msg)

        self.response.status_code = httplib.OK
        self.response.payload = {'status': 'ok', 'result': 'Success'}
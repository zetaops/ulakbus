#-*- coding: utf-8 -*-

from zato.common import SMTPMessage
from zato.server.service import Service
from zengine.lib.cache import Cache

class E_PostaYolla(Service):

    def handle(self):

        wf_name = self.request.payload['wf_name']
        e_posta =self.request.payload['e_posta']
        bilgi = self.request.payload['bilgi']
        aktivasyon_kodu = self.request.payload['aktivasyon_kodu']

        # Obtain a connection
        conn = self.email.smtp.get('Ulakbus-Mail').conn

        # Create a regular e-mail
        msg = SMTPMessage()
        msg.subject = 'Ulakbüs Aktivasyon Maili'
        msg.to = e_posta
        msg.from_ = 'postmaster@mg.ulakbus.net'
        msg.body = 'E-Posta adresinizi doğrulamak için ' \
                    'aşağıdaki linke tıklayınız:\n\n %s' \
                    % ('http://dev.zetaops.io/#/%s/object_id=%s'
                       %(wf_name,aktivasyon_kodu) )

        Cache(aktivasyon_kodu).set(bilgi,7200)

        # Send the message
        conn.send(msg)


# from zato.server.service import Service
# from ulakbus.views.common import profil_sayfasi_goruntuleme
# import smtplib
# from zengine.lib.cache import Cache
#
# class E_PostaYolla(Service):
#     """Ders programı planlamasını arka planda başlatır."""
#
#     def handle(self):
#         wf_name = self.request.payload['wf_name']
#         e_posta =self.request.payload['e_posta']
#         # bilgi = self.request.payload['bilgi']
#         aktivasyon_kodu = self.request.payload['aktivasyon_kodu']
#
#
#
#         fromaddr = 'furkanuyar92@gmail.com'
#         toaddr = e_posta
#         msg = 'Subject: Ulakbüs Aktivasyon Maili\n\nE-Posta adresinizi doğrulamak için ' \
#               'aşağıdaki linke tıklayınız:\n\n %s' \
#                % ('http://dev.zetaops.io/#/%s/object_id=%s' %(wf_name,aktivasyon_kodu) )
#         username = 'furkanuyar92'
#         password = profil_sayfasi_goruntuleme.P
#         server = smtplib.SMTP('smtp.gmail.com:587')
#         server.ehlo()
#         server.starttls()
#         server.login(username, password)
#         server.sendmail(fromaddr, toaddr, msg)
#         server.quit()

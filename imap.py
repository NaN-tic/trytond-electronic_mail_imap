# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.pyson import Eval

import email
import chardet
import logging

__all__ = ['IMAPServer']
__metaclass__ = PoolMeta


class IMAPServer:
    __name__ = 'imap.server'

    mailbox = fields.Many2One('electronic.mail.mailbox', 'Mailbox',
        required=True)

    @classmethod
    def __setup__(cls):
        super(IMAPServer, cls).__setup__()
        cls._buttons.update({
            'get_mails': {
                'invisible': Eval('state') == 'draft',
                },
            })

    @classmethod
    @ModelView.button
    def get_emails(cls, servers):
        "Get emails from server and save like ElectronicMail module"
        ElectronicMail = Pool().get('electronic.mail')
        for server in servers:
            try:
                imapper = cls.connect(server)
                messages = cls.fetch(imapper, server)
            except Exception, e:
                cls.raise_user_error('general_error', e)
            logging.getLogger('IMAPServer').info(
                    'Process %s email(s) from %s' % (
                    len(messages),
                    server.name,
                    ))
            for message in messages:
                msg = message[0][1]
                if not isinstance(msg, str):
                    encoding = chardet.detect(message)
                    message = message.decode(encoding.get('encoding'))
                # Warning: 'message_from_string' doesn't always work correctly
                # on unicode, we must use utf-8 strings.
                if isinstance(msg, unicode):
                    msg = msg.encode('utf-8')
                mail = email.message_from_string(msg)
                ElectronicMail.create_from_email(mail, servers.mailbox)

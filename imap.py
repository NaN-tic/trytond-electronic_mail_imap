# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.pyson import Eval

from email import message_from_string
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
        cls._error_messages.update({
                'invalid_state_server': 'IMAP server "%s" is in draft state',
                })
        cls._buttons.update({
            'get_emails': {
                'invisible': Eval('state') == 'draft',
                },
            })

    @classmethod
    @ModelView.button
    def get_emails(cls, servers):
        "Get emails from server and save like ElectronicMail module"
        ElectronicMail = Pool().get('electronic.mail')
        mails = {}
        for server in servers:
            mails[server.id] = []
            if server.state != 'draft':
                imapper = cls.connect(server)
                messages = cls.fetch(imapper, server)
                logging.getLogger('IMAPServer').info(
                        'Process %s email(s) from %s' % (
                        len(messages),
                        server.name,
                        ))
                for message_id, message in messages.iteritems():
                    msg = message[0][1]
                    if not isinstance(msg, str):
                        encoding = chardet.detect(msg)
                        msg = msg.decode(encoding.get('encoding'))
                    # Warning: 'message_from_string' doesn't always work
                    # correctly on unicode, we must use utf-8 strings.
                    if isinstance(msg, unicode):
                        msg = msg.encode('utf-8')
                    mail = message_from_string(msg)
                    mails[server.id].append(ElectronicMail.create_from_email(
                            mail, server.mailbox))
            else:
                cls.raise_user_error('invalid_state_server',
                    error_args=(server.state,))
        return mails

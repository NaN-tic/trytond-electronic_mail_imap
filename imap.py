# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields
from trytond.pyson import Eval
from email import message_from_string
import chardet
import logging

__all__ = ['IMAPServer']


class IMAPServer(metaclass=PoolMeta):
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
            'get_mails': {
                'invisible': Eval('state') == 'draft',
                },
            })

    @classmethod
    @ModelView.button
    def get_mails(cls, servers):
        "Get mails from server and save like ElectronicMail module"
        cls.fetch_mails(servers)

    @classmethod
    def fetch_mails(cls, servers):
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
                for message_id, message in messages.items():
                    msg = message[0][1]
                    if not isinstance(msg, str):
                        encoding = chardet.detect(msg)
                        msg = msg.decode(encoding.get('encoding'))
                    # Warning: 'message_from_string' doesn't always work
                    # correctly on unicode, we must use utf-8 bytes.
                    if isinstance(msg, str):
                        msg = msg.encode('utf-8')
                    mail = message_from_string(msg)
                    if 'message-id' in mail and mail.get('message-id', False):
                        duplicated_mail = ElectronicMail.search([
                            ('message_id', '=', mail.get('message-id')),
                            ])
                        if duplicated_mail:
                            mails[server.id].append(duplicated_mail[0])
                            continue
                    mails[server.id].append(ElectronicMail.create_from_mail(
                            mail, server.mailbox))
            else:
                cls.raise_user_error('invalid_state_server',
                    error_args=(server.state,))
        for server, emails in mails.items():
            if emails:
                ElectronicMail.write(emails, {
                            'flag_received': True,
                            })
        return mails

    @classmethod
    def get_mails_cron(cls):
        """
        Cron get mails:
        - State: active
        """
        servers = cls.search([
                ('state', '=', 'done'),
                ])
        cls.get_mails(servers)
        return True

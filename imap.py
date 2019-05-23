# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields, ModelSQL
from trytond.pyson import Eval
from email import message_from_bytes
import chardet
import logging
import re
from trytond.i18n import gettext
from trytond.exceptions import UserError

__all__ = ['IMAPServer', 'IMAPServerParty', 'Cron']

class Cron(metaclass=PoolMeta):
    __name__ = 'ir.cron'

    @classmethod
    def __setup__(cls):
        super(Cron, cls).__setup__()
        cls.method.selection.extend([
            ('imap.server|get_mails_cron', "Get Mails")
        ])

class IMAPServer(metaclass=PoolMeta):
    __name__ = 'imap.server'


    mailbox = fields.Many2One('electronic.mail.mailbox', 'Mailbox',
        required=True)
    from_parties = fields.Many2Many('imap.server-party.party', 'imap_server',
        'party', 'From Parties', readonly=True)

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
    def get_mails(cls, servers):
        "Get mails from server and save like ElectronicMail module"
        ElectronicMail = Pool().get('electronic.mail')
        mails = {}
        mail_pattern = '\S+@\S+'
        for server in servers:
            mails[server.id] = []
            if server.state != 'draft':
                imapper = cls.connect(server)
                messages = server.fetch(imapper)
                logging.getLogger('IMAPServer').info(
                    'Process %s email(s) from %s' % (
                        len(messages),
                        server.name,
                        ))
                from_parties = set([x.email for x in server.from_parties])
                for message_id, message in messages.items():
                    msg = message[0][1]
                    if not isinstance(msg, str):
                        encoding = chardet.detect(msg)
                        msg = msg.decode(encoding.get('encoding'))
                    # Warning: 'message_from_string' doesn't always work
                    # correctly on unicode, we must use utf-8 strings.
                    if isinstance(msg, str):
                        msg = msg.encode('utf-8')
                    mail = message_from_bytes(msg)
                    if from_parties:
                        mail_from = re.findall(mail_pattern, mail.get('From', ''))
                        mail_to = re.findall(mail_pattern, mail.get('To', ''))
                        mail_cc = re.findall(mail_pattern, mail.get('CC', ''))
                        mail_bcc = re.findall(mail_pattern, mail.get('BCC', ''))
                        mail_reply_to = re.findall(mail_pattern,
                            mail.get('Reply-To', ''))
                        parsed_mail_from = set([x.replace('<', '').replace('>', '') \
                            for x in mail_from])
                        parsed_mail_to = set([x.replace('<', '').replace('>', '') \
                            for x in mail_to])
                        parsed_mail_cc = set([x.replace('<', '').replace('>', '') \
                            for x in mail_cc])
                        parsed_mail_bcc = set([x.replace('<', '').replace('>', '') \
                            for x in mail_bcc])
                        parsed_mail_reply_to = set([x.replace('<', '').replace('>', '') \
                            for x in mail_reply_to])
                        mail_addresses = (parsed_mail_from | parsed_mail_to |
                            parsed_mail_cc | parsed_mail_bcc |
                            parsed_mail_reply_to)
                        if not mail_addresses & from_parties:
                            continue
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
                raise UserError(gettext(
                    'electronic_mail_imap.invalid_state_server',
                    server=server.state))
        for server, emails in mails.items():
            if emails:
                ElectronicMail.write(emails, {
                    'flag_received': True,
                })

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


class IMAPServerParty(ModelSQL):
    'IMAPServer - Party'
    __name__ = 'imap.server-party.party'

    party = fields.Many2One('party.party', 'Party', required=True, select=True,
        ondelete='CASCADE')
    imap_server = fields.Many2One('imap.server', 'IMAPServer', required=True,
        select=True, ondelete='CASCADE')

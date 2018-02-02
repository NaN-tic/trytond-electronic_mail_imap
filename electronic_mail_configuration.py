# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = [
    'ElectronicMailConfiguration',
    'ElectronicMailConfigurationCompany',
    ]


class ElectronicMailConfiguration:
    __name__ = 'electronic.mail.configuration'
    __metaclass__ = PoolMeta

    inbox = fields.Function(fields.Many2One('electronic.mail.mailbox',
            'Inbox', required=True),
        'get_fields', setter='set_fields')


class ElectronicMailConfigurationCompany:
    __name__ = 'electronic.mail.configuration.company'
    __metaclass__ = PoolMeta

    inbox = fields.Many2One('electronic.mail.mailbox', 'Inbox')

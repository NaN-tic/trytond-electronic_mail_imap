# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields
from trytond.pool import PoolMeta

__all__ = [
    'ElectronicMailConfiguration',
    'ElectronicMailConfigurationCompany',
    ]


class ElectronicMailConfiguration(metaclass=PoolMeta):
    __name__ = 'electronic.mail.configuration'

    inbox = fields.Function(fields.Many2One('electronic.mail.mailbox',
            'Inbox', required=True),
        'get_fields', setter='set_fields')


class ElectronicMailConfigurationCompany(metaclass=PoolMeta):
    __name__ = 'electronic.mail.configuration.company'

    inbox = fields.Many2One('electronic.mail.mailbox', 'Inbox')

# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta
from trytond.model import fields


class Party(metaclass=PoolMeta):
    __name__ = 'party.party'

    imap_server = fields.Many2Many('imap.server-party.party', 'party',
        'imap_server', 'IMAP Server')


# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool, PoolMeta
from trytond.model import ModelView, fields, ModelSQL
from trytond.pyson import Eval

__all__ = ['Party']


class Party:
    __name__ = 'party.party'
    __metaclass__ = PoolMeta

    imap_server = fields.Many2Many('imap.server-party.party', 'party',
        'imap_server', 'IMAP Server')


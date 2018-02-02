# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import imap
from . import electronic_mail_configuration

def register():
    Pool.register(
        electronic_mail_configuration.ElectronicMailConfiguration,
        electronic_mail_configuration.ElectronicMailConfigurationCompany,
        imap.IMAPServer,
        module='electronic_mail_imap', type_='model')

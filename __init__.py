# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from .imap import *
from .electronic_mail_configuration import *

def register():
    Pool.register(
        ElectronicMailConfiguration,
        ElectronicMailConfigurationCompany,
        IMAPServer,
        module='electronic_mail_imap', type_='model')

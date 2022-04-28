
# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.modules.imap.tests import (create_mock_imap_conn,
    create_imap_server, create_mock_mails)

try:
    # Python >= 3.3
    from unittest.mock import MagicMock
except ImportError:
    # Python < 3.3
    from mock import MagicMock

from trytond.pool import Pool


class ElectronicMailImapTestCase(ModuleTestCase):
    'Test ElectronicMailImap module'
    module = 'electronic_mail_imap'

    @with_transaction()
    def test_get_mails(self):
        pool = Pool()
        IMAPServer = pool.get('imap.server')
        ElectronicMail = pool.get('electronic.mail')
        Mailbox = pool.get('electronic.mail.mailbox')
        Party = pool.get('party.party')
        ContactMechanism = pool.get('party.contact_mechanism')
        party_to_sniff = Party()
        party_to_sniff.name = 'receiver'
        party_to_sniff.save()
        contact_mechanism = ContactMechanism()
        contact_mechanism.type = 'email'
        contact_mechanism.value = 'sender@example.com'
        contact_mechanism.party = party_to_sniff
        contact_mechanism.save()
        mailbox = Mailbox(name='Test Mailbox')
        mailbox.save()
        server = create_imap_server(pool)
        server.mailbox = mailbox
        server.state = 'done'
        server.from_parties = tuple([party_to_sniff])
        server.save()
        mails = create_mock_mails()
        mock_conn = create_mock_imap_conn(ssl=server.ssl, mails=mails)
        IMAPServer.get_server = MagicMock(return_value=mock_conn)
        IMAPServer.get_mails([server])
        received_mails = ElectronicMail.search([])
        # Check if all mails was created
        self.assertEqual(len(received_mails), len(mails))
        for mail in received_mails:
            self.assertEqual(mail.subject, 'My test Email')
        self.assertNotEqual(received_mails[0].message_id,
            received_mails[1].message_id)
        self.assertEqual(received_mails[0].rec_name, 'My test Email (ID: 1)')
        self.assertEqual(received_mails[1].rec_name, 'My test Email (ID: 2)')

        # Check that repeated emails are not stored
        IMAPServer.get_mails([server])
        received_mails = ElectronicMail.search([])
        self.assertEqual(len(received_mails), 2)
        message = mails['1'][1][0][1].replace(
            'Message-ID: 1', 'Message-ID: 3')
        mails.update({
            '3': ('OK', (('3', message),))
            })
        mock_conn = create_mock_imap_conn(ssl=server.ssl, mails=mails)
        mock_conn.from_parties = tuple([party_to_sniff])
        IMAPServer.get_server = MagicMock(return_value=mock_conn)
        IMAPServer.get_mails([server])
        received_mails = ElectronicMail.search([])
        self.assertEqual(len(received_mails), 3)


del ModuleTestCase

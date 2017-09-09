#!/usr/bin/env python3

import logging
from unittest import TestCase, mock
from eh_docbot import util, auth


class TestEhAuth(TestCase):

    def setUp(self):
        # allow the logs to go out
        logging.basicConfig(level=logging.DEBUG)
        print()
        self.session = mock.MagicMock()
        self.session.content = 'HTML'
        self.bs4_find = mock.MagicMock(return_value={'action': 'URL'})
        self.bs4 = mock.MagicMock()
        self.bs4.return_value.find = self.bs4_find
        self.bs4_mock = mock.patch('eh_docbot.auth.BeautifulSoup', self.bs4)
        self.time_mock = mock.patch('time.sleep')
        self.bs4_mock.start()
        self.time_mock.start()

    def tearDown(self):
        self.bs4_mock.stop()
        self.time_mock.stop()

    def test_auth_get(self):
        self.session.cookies = {'ipb_session_id': 'b0b135'}
        auth.auth_wiki(self.session)


class TestWikiAuth(TestCase):
    pass


if '__main__' == __name__:
    unittest.main(buffer=True)


# -*- coding: utf-8 -*-
# Copyright (c) 2013 Tomasz Wójcik <tomek@bthlabs.pl>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""
test_conn
=========

This module contains test suite for the *SMTP* class.
"""

from envelopes.conn import SMTP
from envelopes.envelope import Envelope
from lib.testing import BaseTestCase


class Test_SMTPConnection(BaseTestCase):
    def setUp(self):
        self._patch_smtplib()

    def test_constructor(self):
        conn = SMTP('localhost', port=587, login='spam',
                    password='eggs', tls=True, timeout=10)

        assert conn._conn is None
        assert conn._host == 'localhost'
        assert conn._port == 587
        assert conn._login == 'spam'
        assert conn._password == 'eggs'
        assert conn._tls is True
        assert conn._timeout == 10

    def test_constructor_all_kwargs(self):
        conn = SMTP(host='localhost', port=587, login='spam',
                    password='eggs', tls=True)

        assert conn._conn is None
        assert conn._host == 'localhost'
        assert conn._port == 587
        assert conn._login == 'spam'
        assert conn._password == 'eggs'
        assert conn._tls is True

    def test_connect(self):
        conn = SMTP('localhost')
        conn._connect()
        assert conn._conn is not None

        old_conn = conn._conn
        conn._connect()
        assert old_conn == conn._conn

    def test_connect_replace_current(self):
        conn = SMTP('localhost')
        conn._connect()
        assert conn._conn is not None

        old_conn = conn._conn
        conn._connect(replace_current=True)
        assert conn._conn is not None
        assert conn._conn != old_conn

    def test_connect_starttls(self):
        conn = SMTP('localhost', tls=False)
        conn._connect()
        assert conn._conn is not None
        assert len(conn._conn._call_stack.get('starttls', [])) == 0

        conn = SMTP('localhost', tls=True)
        conn._connect()
        assert conn._conn is not None
        assert len(conn._conn._call_stack.get('starttls', [])) == 1

    def test_connect_login(self):
        conn = SMTP('localhost')
        conn._connect()
        assert conn._conn is not None
        assert len(conn._conn._call_stack.get('login', [])) == 0

        conn = SMTP('localhost', login='spam')
        conn._connect()
        assert conn._conn is not None
        assert len(conn._conn._call_stack.get('login', [])) == 1

        call_args = conn._conn._call_stack['login'][0][0]
        assert len(call_args) == 2
        assert call_args[0] == conn._login
        assert call_args[1] == ''

        conn = SMTP('localhost', login='spam', password='eggs')
        conn._connect()
        assert conn._conn is not None
        assert len(conn._conn._call_stack.get('login', [])) == 1

        call_args = conn._conn._call_stack['login'][0][0]
        assert len(call_args) == 2
        assert call_args[0] == conn._login
        assert call_args[1] == conn._password

    def test_is_connected(self):
        conn = SMTP('localhost')
        assert conn.is_connected is False

        conn._connect()
        assert conn.is_connected is True
        assert len(conn._conn._call_stack.get('noop', [])) == 1

    def test_send(self):
        conn = SMTP('localhost')

        msg = self._dummy_message()
        envelope = Envelope(**msg)
        mime_msg = envelope.to_mime_message()

        conn.send(envelope)
        assert conn._conn is not None
        assert len(conn._conn._call_stack.get('sendmail', [])) == 1

        call_args = conn._conn._call_stack['sendmail'][0][0]
        assert len(call_args) == 3
        assert call_args[0] == mime_msg['From']
        assert call_args[1] == [envelope._addrs_to_header([addr]) for addr in envelope._to + envelope._cc + envelope._bcc]
        assert call_args[2] != ''

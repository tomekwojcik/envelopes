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
envelopes.conn
==============

This module contains SMTP connection wrapper.
"""

import smtplib
import socket

TimeoutException = socket.timeout

__all__ = ['SMTP', 'GMailSMTP', 'SendGridSMTP', 'MailcatcherSMTP',
           'TimeoutException']


class SMTP(object):
    """Wrapper around :py:class:`smtplib.SMTP` class."""

    def __init__(self, host=None, port=25, login=None, password=None,
                 tls=False, timeout=None):
        self._conn = None
        self._host = host
        self._port = port
        self._login = login
        self._password = password
        self._tls = tls
        self._timeout = timeout

    @property
    def is_connected(self):
        """Returns *True* if the SMTP connection is initialized and
        connected. Otherwise returns *False*"""
        try:
            self._conn.noop()
        except (AttributeError, smtplib.SMTPServerDisconnected):
            return False
        else:
            return True

    def _connect(self, replace_current=False):
        if self._conn is None or replace_current:
            try:
                self._conn.quit()
            except (AttributeError, smtplib.SMTPServerDisconnected):
                pass

            if self._timeout:
                self._conn = smtplib.SMTP(self._host, self._port,
                                          timeout=self._timeout)
            else:
                self._conn = smtplib.SMTP(self._host, self._port)

        if self._tls:
            self._conn.starttls()

        if self._login:
            self._conn.login(self._login, self._password or '')

    def send(self, envelope):
        """Sends an *envelope*."""
        if not self.is_connected:
            self._connect()

        msg = envelope.to_mime_message()
        to_addrs = [envelope._addrs_to_header([addr]) for addr in envelope._to + envelope._cc + envelope._bcc]

        return self._conn.sendmail(msg['From'], to_addrs, msg.as_string())


class GMailSMTP(SMTP):
    """Subclass of :py:class:`SMTP` preconfigured for GMail SMTP."""

    GMAIL_SMTP_HOST = 'smtp.googlemail.com'
    GMAIL_SMTP_TLS = True

    def __init__(self, login=None, password=None):
        super(GMailSMTP, self).__init__(
            self.GMAIL_SMTP_HOST, tls=self.GMAIL_SMTP_TLS, login=login,
            password=password
        )


class SendGridSMTP(SMTP):
    """Subclass of :py:class:`SMTP` preconfigured for SendGrid SMTP."""

    SENDGRID_SMTP_HOST = 'smtp.sendgrid.net'
    SENDGRID_SMTP_PORT = 587
    SENDGRID_SMTP_TLS = False

    def __init__(self, login=None, password=None):
        super(SendGridSMTP, self).__init__(
            self.SENDGRID_SMTP_HOST, port=self.SENDGRID_SMTP_PORT,
            tls=self.SENDGRID_SMTP_TLS, login=login,
            password=password
        )


class MailcatcherSMTP(SMTP):
    """Subclass of :py:class:`SMTP` preconfigured for local Mailcatcher
    SMTP."""

    MAILCATCHER_SMTP_HOST = 'localhost'

    def __init__(self, port=1025):
        super(MailcatcherSMTP, self).__init__(
            self.MAILCATCHER_SMTP_HOST, port=port
        )

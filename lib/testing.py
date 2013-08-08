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
lib.testing
===========

Various utilities used in testing.
"""

import codecs
import json
import os
import smtplib
import tempfile

HTML_BODY = u"""<html>
<head></head>
<body><p>I'm a helicopter!</p></body>
</html>"""

TEXT_BODY = u"""I'm a helicopter!"""


class MockSMTP(object):
    """A class that mocks ``smtp.SMTP``."""

    debuglevel = 0
    file = None
    helo_resp = None
    ehlo_msg = "ehlo"
    ehlo_resp = None
    does_esmtp = 0
    default_port = smtplib.SMTP_PORT

    def __init__(self, host='', port=0, local_hostname=None, timeout=0):
        self._host = host
        self._port = port
        self._local_hostname = local_hostname
        self._timeout = timeout
        self._call_stack = {}

    def __append_call(self, method, args, kwargs):
        if method not in self._call_stack:
            self._call_stack[method] = []

        self._call_stack[method].append((args, kwargs))

    def set_debuglevel(self, debuglevel):
        self.debuglevel = debuglevel

    def _get_socket(self, port, host, timeout):
        return None

    def connect(self, host='localhost', port=0):
        self.__append_call('connect', [], dict(host=host, port=port))

    def send(self, str):
        self.__append_call('connect', [str], {})

    def putcmd(self, cmd, args=""):
        self.__append_call('connect', [cmd], dict(args=args))

    def getreply(self):
        self.__append_call('getreply', [], dict())

    def docmd(self, cmd, args=""):
        self.__append_call('docmd', [cmd], dict(args=args))

    def helo(self, name=''):
        self.__append_call('helo', [], dict(name=name))

    def ehlo(self, name=''):
        self.__append_call('ehlo', [], dict(name=name))

    def has_extn(self, opt):
        self.__append_call('has_extn', [opt], dict())

    def help(self, args=''):
        self.__append_call('help', [], dict(args=args))

    def rset(self):
        self.__append_call('rset', [], dict())

    def noop(self):
        self.__append_call('noop', [], dict())

    def mail(self, sender, options=[]):
        self.__append_call('mail', [sender], dict(options=options))

    def rcpt(self, recip, options=[]):
        self.__append_call('rcpt', [recip], dict(options=options))

    def data(self, msg):
        self.__append_call('data', [msg], dict())

    def verify(self, address):
        self.__append_call('verify', [address], dict())

    vrfy = verify

    def expn(self, address):
        self.__append_call('expn', [address], dict())

    def ehlo_or_helo_if_needed(self):
        self.__append_call('ehlo_or_helo_if_needed', [], dict())

    def login(self, user, password):
        self.__append_call('login', [user, password], dict())

    def starttls(self, keyfile=None, certfile=None):
        self.__append_call('starttls', [], dict(keyfile=keyfile,
                                                certfile=certfile))

    def sendmail(self, from_addr, to_addrs, msg, mail_options=[],
                 rcpt_options=[]):
        _args = [from_addr, to_addrs, msg]
        _kwargs = dict(mail_options=mail_options, rcpt_options=rcpt_options)
        self.__append_call('sendmail', _args, _kwargs)

    def close(self):
        self.__append_call('close', [], dict())

    def quit(self):
        self.__append_call('quit', [], dict())


class BaseTestCase(object):
    """Base class for Envelopes test cases."""

    @classmethod
    def setUpClass(cls):
        cls._tempfiles = []

    @classmethod
    def tearDownClass(cls):
        for tempfile in cls._tempfiles:
            os.unlink(tempfile)

    def tearDown(self):
        self._unpatch_smtplib()

    def _patch_smtplib(self):
        self._orig_smtp = smtplib.SMTP
        smtplib.SMTP = MockSMTP

    def _unpatch_smtplib(self):
        if hasattr(self, '_orig_smtp'):
            smtplib.SMTP = self._orig_smtp

    def _dummy_message(self):
        return dict({
            'to_addr': ('to@example.com', 'Example To'),
            'from_addr': ('from@example.com', 'Example From'),
            'subject': "I'm a helicopter!",
            'html_body': HTML_BODY,
            'text_body': TEXT_BODY,
            'cc_addr': [
                'cc1@example.com',
                'Example CC2 <cc2@example.com>',
                ('cc3@example.com', 'Example CC3')
            ],
            'bcc_addr': [
                'bcc1@example.com',
                'Example BCC2 <bcc2@example.com>',
                ('bcc3@example.com', 'Example BCC3')
            ],
            'headers': {
                'Reply-To': 'reply-to@example.com',
                'X-Mailer': 'Envelopes by BTHLabs'
            },
            'charset': 'utf-8'
        })

    def _tempfile(self, **kwargs):
        fd, path = tempfile.mkstemp(**kwargs)
        os.close(fd)
        self._tempfiles.append(path)

        return path

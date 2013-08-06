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
test_envelope
=============

This module contains test suite for the *Envelope* class.
"""

import os

from envelopes.envelope import Envelope, MessageEncodeError
from lib.testing import BaseTestCase


class Test_Envelope(BaseTestCase):
    def setUp(self):
        self._patch_smtplib()

    def test_constructor(self):
        msg = self._dummy_message()
        envelope = Envelope(**msg)

        assert envelope._to == [msg['to_addr'], msg['to_name']]
        assert envelope._from == [msg['from_addr'], msg['from_name']]
        assert envelope._subject == msg['subject']
        assert len(envelope._parts) == 2

        text_part = envelope._parts[0]
        assert text_part[0] == 'text/plain'
        assert text_part[1] == msg['text_body']
        assert text_part[2] == msg['charset']

        html_part = envelope._parts[1]
        assert html_part[0] == 'text/html'
        assert html_part[1] == msg['html_body']
        assert html_part[2] == msg['charset']

        assert envelope._cc == msg['cc_addrs']
        assert envelope._bcc == msg['bcc_addrs']
        assert envelope._headers == msg['headers']
        assert envelope._charset == msg['charset']

    def test_addr_tuple_to_addr(self):
        addr = Envelope()._addr_tuple_to_addr(('test@example.com', 'Test'))
        assert addr == 'Test <test@example.com>'

        addr = Envelope(charset='utf-8')._addr_tuple_to_addr((
            'test@example.com', ))
        assert addr == 'test@example.com'

    def test_addrs_to_header(self):
        addrs = [
            'test1@example.com',
            'Test2 <test2@example.com>',
            ('test3@example.com', 'Test3'),
        ]

        header = Envelope()._addrs_to_header(addrs)
        ok_header = (
            'test1@example.com,'
            'Test2 <test2@example.com>,'
            'Test3 <test3@example.com>'
        )

        assert header == ok_header

        try:
            header = Envelope()._addrs_to_header([1])
        except MessageEncodeError, exc:
            assert exc.message == '1 is not a valid address'
        except:
            raise
        else:
            assert False, "MessageEncodeError not raised"

    def test_raise(self):
        try:
            Envelope()._raise(RuntimeError, u'ęóąśłżźćń')
        except RuntimeError, exc:
            assert exc.message == u'ęóąśłżźćń'.encode('utf-8')
        except:
            raise
        else:
            assert 'RuntimeError not raised'

    def test_to_mime_message_with_data(self):
        msg = self._dummy_message()
        envelope = Envelope(**msg)

        mime_msg = envelope.to_mime_message()
        assert mime_msg is not None

        assert mime_msg['Subject'] == msg['subject']
        assert mime_msg['To'] == 'Example To <to@example.com>'
        assert mime_msg['From'] == 'Example From <from@example.com>'

        cc_header = (
            'cc1@example.com,'
            'Example CC2 <cc2@example.com>,'
            'Example CC3 <cc3@example.com>'
        )
        assert mime_msg['CC'] == cc_header

        bcc_header = (
            'bcc1@example.com,'
            'Example BCC2 <bcc2@example.com>,'
            'Example BCC3 <bcc3@example.com>'
        )
        assert mime_msg['BCC'] == bcc_header

        assert mime_msg['Reply-To'] == msg['headers']['Reply-To']
        assert mime_msg['X-Mailer'] == msg['headers']['X-Mailer']

        mime_msg_parts = [part for part in mime_msg.walk()]
        assert len(mime_msg_parts) == 3
        text_part, html_part = mime_msg_parts[1:]

        assert text_part.get_content_type() == 'text/plain'
        assert text_part.get_payload() == msg['text_body']

        assert html_part.get_content_type() == 'text/html'
        assert html_part.get_payload() == msg['html_body']

    def test_to_mime_message_with_no_data(self):
        envelope = Envelope()
        mime_msg = envelope.to_mime_message()

        assert mime_msg['Subject'] == ''
        assert mime_msg['To'] == ''
        assert mime_msg['From'] == ''

        assert 'CC' not in mime_msg
        assert 'BCC' not in mime_msg

        mime_msg_parts = [part for part in mime_msg.walk()]
        assert len(mime_msg_parts) == 1

    def test_to_mime_message_unicode(self):
        msg = {
            'to_addr': 'to@example.com',
            'to_name': u'ęóąśłżźćń',
            'from_addr': 'from@example.com',
            'from_name': u'ęóąśłżźćń',
            'subject': u'ęóąśłżźćń',
            'html_body': u'ęóąśłżźćń',
            'text_body': u'ęóąśłżźćń',
            'cc_addrs': [
                ('cc@example.com', u'ęóąśłżźćń')
            ],
            'bcc_addrs': [
                ('bcc@example.com', u'ęóąśłżźćń')
            ],
            'headers': {
                'X-Test': u'ęóąśłżźćń'
            },
            'charset': 'utf-8'
        }

        envelope = Envelope(**msg)

        mime_msg = envelope.to_mime_message()
        assert mime_msg is not None

        assert mime_msg['Subject'] == msg['subject'].encode('utf-8')
        assert mime_msg['To'] == u'ęóąśłżźćń <to@example.com>'.encode('utf-8')
        assert mime_msg['From'] == u'ęóąśłżźćń <from@example.com>'.\
            encode('utf-8')

        cc_header = u'ęóąśłżźćń <cc@example.com>'
        assert mime_msg['CC'] == cc_header.encode('utf-8')

        bcc_header = u'ęóąśłżźćń <bcc@example.com>'
        assert mime_msg['BCC'] == bcc_header.encode('utf-8')

        assert mime_msg['X-Test'] == msg['headers']['X-Test'].encode('utf-8')

        mime_msg_parts = [part for part in mime_msg.walk()]
        assert len(mime_msg_parts) == 3
        text_part, html_part = mime_msg_parts[1:]

        assert text_part.get_content_type() == 'text/plain'
        assert text_part.get_payload() == msg['text_body'].encode('utf-8')

        assert html_part.get_content_type() == 'text/html'
        assert html_part.get_payload() == msg['html_body'].encode('utf-8')

    def test_send(self):
        envelope = Envelope(
            from_addr='spam@example.com',
            to_addr='eggs@example.com',
            subject='Testing envelopes!',
            text_body='Just a testy test.'
        )

        conn, result = envelope.send(host='localhost')
        assert conn._conn is not None
        assert len(conn._conn._call_stack.get('sendmail', [])) == 1

    def test_to_addr_property(self):
        envelope = Envelope(**self._dummy_message())
        assert envelope.to_addr == envelope._to[0]

        envelope.to_addr = 'new@example.com'
        assert envelope.to_addr == 'new@example.com'

    def test_to_name_property(self):
        envelope = Envelope(**self._dummy_message())
        assert envelope.to_name == envelope._to[1]

        envelope.to_name = 'new@example.com'
        assert envelope.to_name == 'new@example.com'

    def test_from_addr_property(self):
        envelope = Envelope(**self._dummy_message())
        assert envelope.from_addr == envelope._from[0]

        envelope.from_addr = 'new@example.com'
        assert envelope.from_addr == 'new@example.com'

    def test_from_name_property(self):
        envelope = Envelope(**self._dummy_message())
        assert envelope.from_name == envelope._from[1]

        envelope.from_name = 'new@example.com'
        assert envelope.from_name == 'new@example.com'

    def test_cc_property(self):
        msg = self._dummy_message()

        envelope = Envelope(**msg)
        assert envelope.cc == envelope._cc

        msg.pop('cc_addrs')
        envelope = Envelope(**msg)
        assert envelope.cc == []

    def test_add_cc(self):
        msg = self._dummy_message()
        msg.pop('cc_addrs')

        envelope = Envelope(**msg)
        envelope.add_cc('cc@example.com')
        assert envelope.cc == ['cc@example.com']

    def test_clear_cc(self):
        msg = self._dummy_message()

        envelope = Envelope(**msg)
        envelope.clear_cc()
        assert envelope.cc == []

    def test_bcc_property(self):
        msg = self._dummy_message()

        envelope = Envelope(**msg)
        assert envelope.bcc == envelope._bcc

        msg.pop('bcc_addrs')
        envelope = Envelope(**msg)
        assert envelope.bcc == []

    def test_add_bcc(self):
        msg = self._dummy_message()
        msg.pop('bcc_addrs')

        envelope = Envelope(**msg)
        envelope.add_bcc('bcc@example.com')
        assert envelope.bcc == ['bcc@example.com']

    def test_clear_bcc(self):
        msg = self._dummy_message()

        envelope = Envelope(**msg)
        envelope.clear_bcc()
        assert envelope.bcc == []

    def test_charset_property(self):
        envelope = Envelope()
        assert envelope.charset == envelope._charset

        envelope.charset = 'latin2'
        assert envelope._charset == 'latin2'

    def test_headers_property(self):
        msg = self._dummy_message()
        envelope = Envelope(**msg)

        assert envelope.headers == msg['headers']

    def test_add_header(self):
        msg = self._dummy_message()
        msg.pop('headers')
        envelope = Envelope(**msg)

        envelope.add_header('X-Spam', 'eggs')
        assert envelope.headers == {'X-Spam': 'eggs'}

    def test_clear_headers(self):
        msg = self._dummy_message()
        envelope = Envelope(**msg)

        envelope.clear_headers()
        assert envelope.headers == {}

    def test_add_attachment(self):
        msg = self._dummy_message()
        envelope = Envelope(**msg)

        _jpg = self._tempfile(suffix='.jpg')
        envelope.add_attachment(_jpg)

        _mp3 = self._tempfile(suffix='.mp3')
        envelope.add_attachment(_mp3)

        _pdf = self._tempfile(suffix='.pdf')
        envelope.add_attachment(_pdf)

        _something = self._tempfile(suffix='.something', prefix=u'ęóąśłżźćń')
        envelope.add_attachment(_something)

        _octet = self._tempfile(suffix='.txt')
        envelope.add_attachment(_octet, mimetype='application/octet-stream')

        assert len(envelope._parts) == 7

        assert envelope._parts[0][0] == 'text/plain'
        assert envelope._parts[1][0] == 'text/html'

        assert envelope._parts[2][0] == 'image/jpeg'
        assert envelope._parts[2][1]['Content-Disposition'] ==\
            'attachment; filename="%s"' % os.path.basename(_jpg)

        assert envelope._parts[3][0] == 'audio/mpeg'
        assert envelope._parts[3][1]['Content-Disposition'] ==\
            'attachment; filename="%s"' % os.path.basename(_mp3)

        assert envelope._parts[4][0] == 'application/pdf'
        assert envelope._parts[4][1]['Content-Disposition'] ==\
            'attachment; filename="%s"' % os.path.basename(_pdf)

        assert envelope._parts[5][0] == 'application/octet-stream'
        assert envelope._parts[5][1]['Content-Disposition'] ==\
            'attachment; filename="%s"' %\
            os.path.basename(_something.encode('utf-8'))

        assert envelope._parts[6][0] == 'application/octet-stream'
        assert envelope._parts[6][1]['Content-Disposition'] ==\
            'attachment; filename="%s"' % os.path.basename(_octet)

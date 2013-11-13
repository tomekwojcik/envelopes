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
envelopes.envelope
==================

This module contains the Envelope class.
"""

import sys

if sys.version_info[0] == 2:
    from email import Encoders as email_encoders
elif sys.version_info[0] == 3:
    from email import encoders as email_encoders
    basestring = str

    def unicode(_str, _charset):
        return str(_str.encode(_charset), _charset)
else:
    raise RuntimeError('Unsupported Python version: %d.%d.%d' % (
        sys.version_info[0], sys.version_info[1], sys.version_info[2]
    ))

from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mimetypes
import os
import re

from .conn import SMTP
from .compat import encoded


class MessageEncodeError(Exception):
    pass

class Envelope(object):
    """
    The Envelope class.

    **Address formats**

    The following formats are supported for e-mail addresses:

    * ``"user@server.com"`` - just the e-mail address part as a string,
    * ``"Some User <user@server.com>"`` - name and e-mail address parts as a string,
    * ``("user@server.com", "Some User")`` - e-mail address and name parts as a tuple.

    Whenever you come to manipulate addresses feel free to use any (or all) of
    the formats above.

    :param to_addr: ``To`` address or list of ``To`` addresses
    :param from_addr: ``From`` address
    :param subject: message subject
    :param html_body: optional HTML part of the message
    :param text_body: optional plain text part of the message
    :param cc_addr: optional single CC address or list of CC addresses
    :param bcc_addr: optional single BCC address or list of BCC addresses
    :param headers: optional dictionary of headers
    :param charset: message charset
    """

    ADDR_FORMAT = '%s <%s>'
    ADDR_REGEXP = re.compile(r'^(.*) <([^@]+@[^@]+)>$')

    def __init__(self, to_addr=None, from_addr=None, subject=None,
                 html_body=None, text_body=None, cc_addr=None, bcc_addr=None,
                 headers=None, charset='utf-8'):
        if to_addr:
            if isinstance(to_addr, list):
                self._to = to_addr
            else:
                self._to = [to_addr]
        else:
            self._to = []

        self._from = from_addr
        self._subject = subject
        self._parts = []

        if text_body:
            self._parts.append(('text/plain', text_body, charset))

        if html_body:
            self._parts.append(('text/html', html_body, charset))

        if cc_addr:
            if isinstance(cc_addr, list):
                self._cc = cc_addr
            else:
                self._cc = [cc_addr]
        else:
            self._cc = []

        if bcc_addr:
            if isinstance(bcc_addr, list):
                self._bcc = bcc_addr
            else:
                self._bcc = [bcc_addr]
        else:
            self._bcc = []

        if headers:
            self._headers = headers
        else:
            self._headers = {}

        self._charset = charset

        self._addr_format = unicode(self.ADDR_FORMAT, charset)

    def __repr__(self):
        return u'<Envelope from="%s" to="%s" subject="%s">' % (
            self._addrs_to_header([self._from]),
            self._addrs_to_header(self._to),
            self._subject
        )

    @property
    def to_addr(self):
        """List of ``To`` addresses."""
        return self._to

    def add_to_addr(self, to_addr):
        """Adds a ``To`` address."""
        self._to.append(to_addr)

    def clear_to_addr(self):
        """Clears list of ``To`` addresses."""
        self._to = []

    @property
    def from_addr(self):
        return self._from

    @from_addr.setter
    def from_addr(self, from_addr):
        self._from = from_addr

    @property
    def cc_addr(self):
        """List of CC addresses."""
        return self._cc

    def add_cc_addr(self, cc_addr):
        """Adds a CC address."""
        self._cc.append(cc_addr)

    def clear_cc_addr(self):
        """Clears list of CC addresses."""
        self._cc = []

    @property
    def bcc_addr(self):
        """List of BCC addresses."""
        return self._bcc

    def add_bcc_addr(self, bcc_addr):
        """Adds a BCC address."""
        self._bcc.append(bcc_addr)

    def clear_bcc_addr(self):
        """Clears list of BCC addresses."""
        self._bcc = []

    @property
    def charset(self):
        """Message charset."""
        return self._charset

    @charset.setter
    def charset(self, charset):
        self._charset = charset

        self._addr_format = unicode(self.ADDR_FORMAT, charset)

    def _addr_tuple_to_addr(self, addr_tuple):
        addr = ''

        if len(addr_tuple) == 2 and addr_tuple[1]:
            addr = self._addr_format % (
                self._header(addr_tuple[1] or ''),
                addr_tuple[0] or ''
            )
        elif addr_tuple[0]:
            addr = addr_tuple[0]

        return addr

    @property
    def headers(self):
        """Dictionary of custom headers."""
        return self._headers

    def add_header(self, key, value):
        """Adds a custom header."""
        self._headers[key] = value

    def clear_headers(self):
        """Clears custom headers."""
        self._headers = {}

    def _addrs_to_header(self, addrs):
        _addrs = []
        for addr in addrs:
            if not addr:
                continue

            if isinstance(addr, basestring):
                if self._is_ascii(addr):
                    _addrs.append(self._encoded(addr))
                else:
                    # these headers need special care when encoding, see:
                    #   http://tools.ietf.org/html/rfc2047#section-8
                    # Need to break apart the name from the address if there are
                    # non-ascii chars
                    m = self.ADDR_REGEXP.match(addr)
                    if m:
                        t = (m.group(2), m.group(1))
                        _addrs.append(self._addr_tuple_to_addr(t))
                    else:
                        # What can we do? Just pass along what the user gave us and hope they did it right
                        _addrs.append(self._encoded(addr))
            elif isinstance(addr, tuple):
                _addrs.append(self._addr_tuple_to_addr(addr))
            else:
                self._raise(MessageEncodeError,
                            '%s is not a valid address' % str(addr))

        _header = ','.join(_addrs)
        return _header

    def _raise(self, exc_class, message):
        raise exc_class(self._encoded(message))

    def _header(self, _str):
        if self._is_ascii(_str):
            return _str
        return Header(_str, self._charset).encode()

    def _is_ascii(self, _str):
        return all(ord(c) < 128 for c in _str)

    def _encoded(self, _str):
        return encoded(_str, self._charset)

    def to_mime_message(self):
        """Returns the envelope as
        :py:class:`email.mime.multipart.MIMEMultipart`."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = self._header(self._subject or '')

        msg['From'] = self._encoded(self._addrs_to_header([self._from]))
        msg['To'] = self._encoded(self._addrs_to_header(self._to))

        if self._cc:
            msg['CC'] = self._addrs_to_header(self._cc)

        if self._headers:
            for key, value in self._headers.items():
                msg[key] = self._header(value)

        for part in self._parts:
            type_maj, type_min = part[0].split('/')
            if type_maj == 'text' and type_min in ('html', 'plain'):
                msg.attach(MIMEText(part[1], type_min, self._charset))
            else:
                msg.attach(part[1])

        return msg

    def add_attachment(self, file_path, mimetype=None):
        """Attaches a file located at *file_path* to the envelope. If
        *mimetype* is not specified an attempt to guess it is made. If nothing
        is guessed then `application/octet-stream` is used."""
        if not mimetype:
            mimetype, _ = mimetypes.guess_type(file_path)

        if mimetype is None:
            mimetype = 'application/octet-stream'

        type_maj, type_min = mimetype.split('/')
        with open(file_path, 'rb') as fh:
            part_data = fh.read()

            part = MIMEBase(type_maj, type_min)
            part.set_payload(part_data)
            email_encoders.encode_base64(part)

            part_filename = os.path.basename(self._encoded(file_path))
            part.add_header('Content-Disposition', 'attachment; filename="%s"'
                            % part_filename)

            self._parts.append((mimetype, part))

    def send(self, *args, **kwargs):
        """Sends the envelope using a freshly created SMTP connection. *args*
        and *kwargs* are passed directly to :py:class:`envelopes.conn.SMTP`
        constructor.

        Returns a tuple of SMTP object and whatever its send method returns."""
        conn = SMTP(*args, **kwargs)
        send_result = conn.send(self)
        return conn, send_result

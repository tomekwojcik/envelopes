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

from email import Encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import mimetypes
import os

from .conn import SMTP


class MessageEncodeError(Exception):
    pass


class Envelope(object):
    """
    The Envelope class.

    **CC and BCC address formats**

    The following address formats are supported for CC and BCC addresses:

    * ``"user@server.com"`` - just the e-mail address part as a string,
    * ``"Some User <user@server.com>"`` - name and e-mail address parts as a string,
    * ``("user@server.com", "Some User")`` - e-mail address and name parts as a tuple.

    Whenever you come to manipulate either CC or BCC addresses feel free to use
    any (or all) of the formats above.

    :param to_addr: address part of ``To`` header (e.g. ``to@example.com``)
    :param to_name: optional name part of ``To`` header (e.g. ``To Example``)
    :param from_addr: address part of ``From`` header
        (e.g. ``from@example.com``)
    :param from_name: optional name part of ``From`` header
        (e.g. ``From Example``)
    :param subject: message subject
    :param html_body: optional HTML part of the message
    :param text_body: optional plain text part of the message
    :param cc_addrs: optional list of CC address
    :param bcc_addrs: optional list of BCC address
    :param headers: optional dictionary of headers
    :param charset: message charset
    """

    ADDR_FORMAT = '%s <%s>'

    def __init__(self, to_addr=None, to_name=None, from_addr=None,
                 from_name=None, subject=None, html_body=None, text_body=None,
                 cc_addrs=None, bcc_addrs=None, headers=None, charset='utf-8'):
        self._to = [to_addr, to_name]
        self._from = [from_addr, from_name]
        self._subject = subject
        self._parts = []

        if text_body:
            self._parts.append(('text/plain', text_body, charset))

        if html_body:
            self._parts.append(('text/html', html_body, charset))

        if cc_addrs:
            self._cc = cc_addrs
        else:
            self._cc = []

        if bcc_addrs:
            self._bcc = bcc_addrs
        else:
            self._bcc = []

        if headers:
            self._headers = headers
        else:
            self._headers = {}

        self._charset = charset

        self._addr_format = unicode(self.ADDR_FORMAT, charset)

    @property
    def to_addr(self):
        """Address part of the ``To`` address."""
        return self._to[0]

    @to_addr.setter
    def to_addr(self, to_addr):
        self._to[0] = to_addr

    @property
    def to_name(self):
        """Name part of the ``To`` address."""
        return self._to[1]

    @to_name.setter
    def to_name(self, to_name):
        self._to[1] = to_name

    @property
    def from_addr(self):
        """Address part of the ``From`` address."""
        return self._from[0]

    @from_addr.setter
    def from_addr(self, from_addr):
        self._from[0] = from_addr

    @property
    def from_name(self):
        """Name part of the ``From`` address."""
        return self._from[1]

    @from_name.setter
    def from_name(self, from_name):
        self._from[1] = from_name

    @property
    def cc(self):
        """List of CC addresses."""
        return self._cc

    def add_cc(self, cc_addr):
        """Adds a CC address."""
        self._cc.append(cc_addr)

    def clear_cc(self):
        """Clears list of CC addresses."""
        self._cc = []

    @property
    def bcc(self):
        """List of BCC addresses."""
        return self._bcc

    def add_bcc(self, bcc_addr):
        """Adds a BCC address."""
        self._bcc.append(bcc_addr)

    def clear_bcc(self):
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
                addr_tuple[1] or '',
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
                _addrs.append(addr)
            elif isinstance(addr, tuple):
                _addrs.append(self._addr_tuple_to_addr(addr))
            else:
                self._raise(MessageEncodeError,
                            '%s is not a valid address' % str(addr))

        _header = unicode(',', self._charset).join(_addrs)
        return _header

    def _raise(self, exc_class, message):
        if isinstance(message, unicode):
            msg = message
        else:
            msg = unicode(message, self._charset)

        raise exc_class(msg.encode(self._charset))

    def to_mime_message(self):
        """Returns the envelope as
        :py:class:`email.mime.multipart.MIMEMultipart`."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = (self._subject or '').encode(self._charset)

        msg['From'] = self._addr_tuple_to_addr(self._from).\
            encode(self._charset)
        msg['To'] = self._addr_tuple_to_addr(self._to).encode(self._charset)

        if self._cc:
            msg['CC'] = self._addrs_to_header(self._cc).encode(self._charset)

        if self._bcc:
            msg['BCC'] = self._addrs_to_header(self._bcc).encode(self._charset)

        if self._headers:
            for key, value in self._headers.iteritems():
                msg[key] = value.encode(self._charset)

        for part in self._parts:
            type_maj, type_min = part[0].split('/')
            if type_maj == 'text' and type_min in ('html', 'plain'):
                msg.attach(MIMEText(part[1].encode(self._charset), type_min))
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
            Encoders.encode_base64(part)

            part_filename = os.path.basename(file_path.encode(self._charset))
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

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

import sys
sys.path = ['.'] + sys.path

from envelopes import Envelope, SMTP
import envelopes.connstack
from flask import Flask, jsonify
import os


app = Flask(__name__)
app.config['DEBUG'] = True

conn = SMTP('127.0.0.1', 1025)


@app.before_request
def app_before_request():
    envelopes.connstack.push_connection(conn)


@app.after_request
def app_after_request(response):
    envelopes.connstack.pop_connection()
    return response


@app.route('/mail', methods=['POST'])
def post_mail():
    envelope = Envelope(
        from_addr='%s@localhost' % os.getlogin(),
        to_addr='%s@localhost' % os.getlogin(),
        subject='Envelopes in Flask demo',
        text_body="I'm a helicopter!"
    )

    smtp = envelopes.connstack.get_current_connection()
    smtp.send(envelope)

    return jsonify(dict(status='ok'))

if __name__ == '__main__':
    app.run()

# -*- coding: utf-8 -*-
# Copyright 2012 Vincent Driessen. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY VINCENT DRIESSEN ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL VINCENT DRIESSEN OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Vincent Driessen.
#

"""
envelopes.connstack
===================

This module implements SMTP connection stack management.
"""

from contextlib import contextmanager
from .local import LocalStack, release_local


class NoSMTPConnectionException(Exception):
    pass


@contextmanager
def Connection(connection):
    push_connection(connection)
    try:
        yield
    finally:
        popped = pop_connection()
        assert popped == connection, \
            'Unexpected SMTP connection was popped off the stack. ' \
            'Check your SMTP connection setup.'


def push_connection(connection):
    """Pushes the given connection on the stack."""
    _connection_stack.push(connection)


def pop_connection():
    """Pops the topmost connection from the stack."""
    return _connection_stack.pop()


def use_connection(connection):
    """Clears the stack and uses the given connection.  Protects against mixed
    use of use_connection() and stacked connection contexts.
    """
    assert len(_connection_stack) <= 1, \
        'You should not mix Connection contexts with use_connection().'
    release_local(_connection_stack)
    push_connection(connection)


def get_current_connection():
    """Returns the current SMTP connection (i.e. the topmost on the
    connection stack).
    """
    return _connection_stack.top


def resolve_connection(connection=None):
    """Convenience function to resolve the given or the current connection.
    Raises an exception if it cannot resolve a connection now.
    """
    if connection is not None:
        return connection

    connection = get_current_connection()
    if connection is None:
        raise NoSMTPConnectionException(
            'Could not resolve an SMTP connection.')
    return connection


_connection_stack = LocalStack()

__all__ = [
    'Connection', 'get_current_connection', 'push_connection',
    'pop_connection', 'use_connection'
]

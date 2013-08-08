Envelopes
=========

.. image:: https://travis-ci.org/tomekwojcik/envelopes.png?branch=master
    :target: https://travis-ci.org/tomekwojcik/envelopes

Mailing for human beings.

About
-----

Envelopes is a wrapper for Python's *email* and *smtplib* modules. It aims to
make working with outgoing e-mail in Python simple and fun.

Short example
-------------

.. sourcecode:: python

    from envelopes import Envelope

    envelope = Envelope(
        from_addr=(u'from@example.com', u'From Example'),
        to_addr=(u'to@example.com', u'To Example'),
        subject=u'Envelopes demo',
        text_body=u"I'm a helicopter!"
    )
    envelope.add_attachment('/Users/bilbo/Pictures/helicopter.jpg')
    envelope.send('smtp.googlemail.com', login='from@example.com',
                  password='password', tls=True)

Features
--------

Envelopes allows you to easily:

* Provide e-mail addresses with or without name part.
* Set text, HTML or both bodies according to your needs.
* Provide any number of CC and BCC addresses.
* Set standard (e.g. ``Reply-To``) and custom (e.g. ``X-Mailer``) headers.
* Attach files of any kind without hassle.
* Use any charset natively supported by Python's *unicode* type in addresses,
  bodies, headers and attachment file names.

Project status
--------------

This is the first public release of the code. It was extracted from a few minor
production apps.

Envelopes has been developed and tested with Python 2.7. Tests for other
versions will follow shortly after the release.

Author
------

Envelopes is developed by `Tomasz Wójcik <http://www.bthlabs.pl/>`_.

License
-------

Envelopes is licensed under the MIT License.

Source code and issues
----------------------

Source code is available on GitHub at:
`tomekwojcik/envelopes <https://github.com/tomekwojcik/envelopes>`_.

To file issue reports and feature requests use the project's issue tracker on
GitHub.

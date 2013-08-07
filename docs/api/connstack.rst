Connection stack
================

The connection stack allows you to use Envelopes' SMTP connection wrapper in
threaded apps. Consult the example Flask app to see it in action.

Code of this module has been adapted from `RQ <http://python-rq.org/>`_ by
`Vincent Driessen <http://nvie.com/about/>`_.

.. autofunction:: envelopes.connstack.get_current_connection

.. autofunction:: envelopes.connstack.pop_connection

.. autofunction:: envelopes.connstack.push_connection

.. autofunction:: envelopes.connstack.resolve_connection

.. autofunction:: envelopes.connstack.use_connection

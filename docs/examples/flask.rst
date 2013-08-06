Envelopes in Flask example
--------------------------

The following code is an example of using Envelopes in Flask apps.

**NOTE**: Due to Flask's threaded nature it's important to wrap
:py:class:`envelopes.conn.SMTP` object in connection stack.

.. sourcecode:: python

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

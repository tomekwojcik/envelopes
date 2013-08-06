Envelopes in Celery example
---------------------------

The following code is an example of using Envelopes in Celery apps.

.. sourcecode:: python

    from celery import Celery
    from envelopes import Envelope

    celery = Celery('envelopes_demo')
    celery.conf.BROKER_URL = 'amqp://guest@localhost//'


    @celery.task
    def send_envelope():
        envelope = Envelope(
            from_addr='%s@localhost' % os.getlogin(),
            to_addr='%s@localhost' % os.getlogin(),
            subject='Envelopes in Celery demo',
            text_body="I'm a helicopter!"
        )
        envelope.send('localhost', port=1025)

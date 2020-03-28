:orphan:

====================
Integration Examples
====================

:code:`pyngrok` is useful in any number of integrations to let us test things locally without having to deploy,
for instance to test locally without having to deploy or configure anything. Below are some common usage examples.

Flask
-----
In :code:`server.py`, where our Flask app is initialized, we should add a variable that let's us configure from an
environment variable whether or not we want to tunnel to :code:`localhost` with :code:`ngrok`. We can initializes
the :code:`ngrok` tunnel in this same place.

.. code-block:: python

    import os
    import sys

    from flask import Flask
    from pyngrok import ngrok

    # Initialize the Flask app for a simple web server
    app = Flask(__name__)
    app.config['USE_NGROK'] = os.environ.get('USE_NGROK', 'False') == 'True'

    if app.config['USE_NGROK']
        # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port)
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, port))

Now Flask can be started by the usual means and setting :code:`USE_NGROK`.

.. code-block:: sh

    USE_NGROK=True FLASK_APP=server.py flask run

Django
------

In :code:`settings.py`, we should add a variable that let's us configure from an environment variable whether or not
we want to tunnel to :code:`localhost` with :code:`ngrok`.

.. code-block:: python

    import os

    USE_NGROK = os.environ.get('USE_NGROK', 'False') == 'True'

If this flag is set, we want to initialize :code:`pyngrok` when Django is booting. An easy place to do this is in
one of an :code:`apps.py` file `extending AppConfig <https://docs.djangoproject.com/en/3.0/ref/applications/#django.apps.AppConfig.ready>`_.

.. code-block:: python

    import sys
    from urllib.parse import urlparse

    from django.apps import AppConfig
    from django.conf import settings

    class CommonConfig(AppConfig):
        name = 'myproject.common'
        verbose_name = 'Common'

        def ready(self):
            if settings.DEV_SERVER and settings.USE_NGROK:
                # pyngrok will only be installed, and should only ever be initialized, in a dev environment
                from pyngrok import ngrok

                # Get the dev server port (defaults to 8000 for Django, can be overridden with the
                # last arg when calling `runserver`)
                addrport = urlparse('http://{}'.format(sys.argv[-1]))
                port = addrport.port if addrport.netloc and addrport.port else 8000

                # Open a ngrok tunnel to the dev server
                public_url = ngrok.connect(port).rstrip("/")
                print('ngrok tunnel "{}" -> "http://127.0.0.1:{}/"'.format(public_url, port))

                # Update any base URLs or webhooks to use the public ngrok URL
                settings.PROJECT_HOST = public_url
                CommonConfig.init_webhooks(public_url)

        @staticmethod
        def init_webhooks(callback_url):
            # Update inbound traffic via APIs to use the public-facing ngrok URL
            pass

Now Django can be started by the usual means and setting :code:`USE_NGROK`.

.. code-block:: sh

    USE_NGROK=True python manage.py runserver

AWS Lambda (Local)
------------------
Lambdas deployed to AWS can easily be developed locally using :code:`pyngrok` and extending the
`Flask example shown above <#flask>`_. In addition to effortless local development, this gives us flexibility
to write tests, leverage a CI, manage revisions, etc.

To start, we make Flask routes in to a shim that funnels requests to the Lambda handlers instead.

.. code-block:: python

    @app.route("/foo")
    def route_foo():
        event = {
            "someQueryParam": request.args.get("someQueryParam")
        }

        return json.dumps(aqi_route.lambda_handler(event, {}))

For a complete example of how we can leverage all these utilities together for to rapidly and reliable develop, test,
and deploy AWS Lambda's, see `the Air Quality Bot repository <https://github.com/alexdlaird/air-quality-bot>`_,
starting in :code:`devserver.py`.

Python HTTP Server
------------------
Python's `http.server module <https://docs.python.org/3/library/http.server.html>`_ also makes for a useful development
server. We can use :code:`pyngrok` to expose it to the web via a tunnel, as show in :code:`server.py` here:

.. code-block:: python

    import os

    from http.server import HTTPServer, BaseHTTPRequestHandler
    from pyngrok import ngrok

    def run(port, server_class=HTTPServer, handler_class=BaseHTTPRequestHandler):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)

        public_url = ngrok.connect(port)
        print('ngrok tunnel "{}" -> "http://127.0.0.1:{}/"'.format(public_url, port))

        try:
            # Block until CTRL-C or some other terminating event
            httpd.serve_forever()
        except KeyboardInterrupt:
           print(' Shutting down server.')

           httpd.socket.close()

    if __name__ == '__main__':
        port = os.environ.get("PORT", 80)

        run(port)

We can then run this script to start the server.

.. code-block:: sh

    python server.py

Python TCP Socket
-----------------
TBD

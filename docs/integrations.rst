:orphan:

====================
Integration Examples
====================

:code:`pyngrok` is useful in any number of integrations to let us test things locally without having to deploy,
for instance to test locally without having to deploy or configure anything. Below are some common usage examples.

Flask
-----

In :code:`server.py`, `where our Flask app is initialized <https://flask.palletsprojects.com/en/1.1.x/quickstart/#a-minimal-application)>`_,
we should add a variable that let's us configure from an environment variable whether or not we want to tunnel to
:code:`localhost` with :code:`ngrok`. We can initialize the :code:`ngrok` tunnel in this same place.

.. code-block:: python

    import os
    import sys

    from flask import Flask
    from pyngrok import ngrok

    # Initialize the Flask app for a simple web server
    app = Flask(__name__)
    app.config["USE_NGROK"] = os.environ.get("USE_NGROK", "False") == "True"

    if app.config["USE_NGROK"]:
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

In `settings.py <https://docs.djangoproject.com/en/3.0/topics/settings/>`_ of `our Django project's <https://docs.djangoproject.com/en/3.0/intro/tutorial01/#creating-a-project>`_,
we should add a variable that let's us configure from an environment variable whether or not we want to tunnel to
:code:`localhost` with :code:`ngrok`.

.. code-block:: python

    import os

    USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"

If this flag is set, we want to initialize :code:`pyngrok` when Django is booting. An easy place to do this is in
one of an :code:`apps.py` file `extending AppConfig <https://docs.djangoproject.com/en/3.0/ref/applications/#django.apps.AppConfig.ready>`_.

.. code-block:: python

    import sys
    from urllib.parse import urlparse

    from django.apps import AppConfig
    from django.conf import settings


    class CommonConfig(AppConfig):
        name = "myproject.common"
        verbose_name = "Common"

        def ready(self):
            if settings.USE_NGROK:
                # pyngrok will only be installed, and should only ever be initialized, in a dev environment
                from pyngrok import ngrok

                # Get the dev server port (defaults to 8000 for Django, can be overridden with the
                # last arg when calling `runserver`)
                addrport = urlparse("http://{}".format(sys.argv[-1]))
                port = addrport.port if addrport.netloc and addrport.port else 8000

                # Open a ngrok tunnel to the dev server
                public_url = ngrok.connect(port).rstrip("/")
                print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, port))

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

FastAPI
-------

In :code:`server.py`, `where our FastAPI app is initialized <https://fastapi.tiangolo.com/tutorial/first-steps/>`_, we should add a variable that let's us configure from an
environment variable whether or not we want to tunnel to :code:`localhost` with :code:`ngrok`. We can initialize
the :code:`ngrok` tunnel in this same place.

.. code-block:: python

    import os
    import sys

    from fastapi import FastAPI
    from pydantic import BaseSettings
    from pyngrok import ngrok


    # Initialize basic settings
    class Settings(BaseSettings):
        USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"


    settings = Settings()

    # Initialize the FastAPI app for a simple web server
    app = FastAPI()

    if settings.USE_NGROK:
        # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port)
        print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, port))

Now FastAPI can be started by the usual means, with Uvicorn, and setting :code:`USE_NGROK`.

.. code-block:: sh

    USE_NGROK=True uvicorn server:app --reload

AWS Lambda (Local)
------------------

Lambdas deployed to AWS can easily be developed locally using :code:`pyngrok` and extending the
`Flask example shown above <#flask>`_. In addition to effortless local development, this gives us flexibility
to write tests, leverage a CI, manage revisions, etc.

To start, we make Flask routes in to a shim that funnels requests to the Lambda handlers instead.

.. code-block:: python

    import json
    from flask import Flask, request

    ...

    @app.route("/foo")
    def route_foo():
        event = {
            "someQueryParam": request.args.get("someQueryParam")
        }

        return json.dumps(route_foo.lambda_handler(event, {}))

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

    port = os.environ.get("PORT", 80)

    server_address = ("", port)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)

    public_url = ngrok.connect(port)
    print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}/\"".format(public_url, port))

    try:
        # Block until CTRL-C or some other terminating event
        httpd.serve_forever()
    except KeyboardInterrupt:
       print(" Shutting down server.")

       httpd.socket.close()

We can then run this script to start the server.

.. code-block:: sh

    python server.py

Python TCP Server and Client
----------------------------

Here is an example of a simple TCP ping/pong server. It opens a local socket, uses :code:`ngrok` to tunnel to that
socket, then the client/server communicate via the publicly exposed address.

For this code to run, we first need to go to
`ngrok's Reserved TCP Addresses <https://dashboard.ngrok.com/reserved>`_ and make a reservation. Set the HOST and PORT
environment variables pointing to that reserved address.

Now create :code:`server.py` with the following code:

.. code-block:: python

    import os
    import socket

    from pyngrok import ngrok

    host = os.environ.get("HOST")
    port = int(os.environ.get("PORT"))

    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Bind a local socket to the port
    server_address = ("", port)
    sock.bind(server_address)
    sock.listen(1)

    # Open a ngrok tunnel to the socket
    public_url = ngrok.connect(port, "tcp", options={"remote_addr": "{}:{}".format(host, port)})
    print("ngrok tunnel \"{}\" -> \"tcp://127.0.0.1:{}/\"".format(public_url, port))

    while True:
        connection = None
        try:
            # Wait for a connection
            print("\nWaiting for a connection ...")
            connection, client_address = sock.accept()

            print("... connection established from {}".format(client_address))

            # Receive the message, send a response
            while True:
                data = connection.recv(1024)
                if data:
                    print("Received: {}".format(data.decode("utf-8")))

                    message = "pong"
                    print("Sending: {}".format(message))
                    connection.sendall(message.encode("utf-8"))
                else:
                    break
        except KeyboardInterrupt:
            print(" Shutting down server.")

            if connection:
                connection.close()
            break

    sock.close()

In a terminal window, we can now start our socket server:

.. code-block:: sh

    HOST="1.tcp.ngrok.io" PORT=12345 python server.py

It's now waiting for incoming connections, so let's write a client to connect to it and send it something.

Create :code:`client.py` with the following code:

.. code-block:: python

    import os
    import socket

    host = os.environ.get("HOST")
    port = int(os.environ.get("PORT"))

    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server with the socket via our ngrok tunnel
    server_address = (host, port)
    sock.connect(server_address)
    print("Connected to {}:{}".format(host, port))

    # Send the message
    message = "ping"
    print("Sending: {}".format(message))
    sock.sendall(message.encode("utf-8"))

    # Await a response
    data_received = 0
    data_expected = len(message)

    while data_received < data_expected:
        data = sock.recv(1024)
        data_received += len(data)
        print("Received: {}".format(data.decode("utf-8")))

    sock.close()

In another terminal window, we can run our client:

.. code-block:: sh

    HOST="1.tcp.ngrok.io" PORT=12345 python client.py

And that's it! Data was sent and received from a socket via our :code:`ngrok` tunnel.

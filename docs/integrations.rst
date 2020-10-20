====================
Integration Examples
====================

``pyngrok`` is useful in any number of integrations to let us test things locally without having to deploy,
for instance to test locally without having to deploy or configure anything. Below are some common usage examples.

Flask
-----

In ``server.py``, `where our Flask app is initialized <https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/#the-application-factory>`_,
we should add a variable that let's us configure from an environment variable whether we want to open a tunnel
to ``localhost`` with ``ngrok`` when the dev server starts. We can initialize the ``pyngrok`` tunnel in this
same place.

.. code-block:: python

    import os
    import sys

    from flask import Flask

    def init_webhooks(base_url):
        # Update inbound traffic via APIs to use the public-facing ngrok URL
        pass

    def create_app():
        app = Flask(__name__)

        # Initialize our ngrok settings into Flask
        app.config.from_mapping(
            BASE_URL="http://localhost:5000",
            USE_NGROK=os.environ.get("USE_NGROK", "False") == "True" and os.environ.get("WERKZEUG_RUN_MAIN") != "true"
        )

        if app.config.get("ENV") == "development" and app.config["USE_NGROK"]:
            # pyngrok will only be installed, and should only ever be initialized, in a dev environment
            from pyngrok import ngrok

            # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
            # when starting the server
            port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 5000

            # Open a ngrok tunnel to the dev server
            public_url = ngrok.connect(port).public_url
            print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

            # Update any base URLs or webhooks to use the public ngrok URL
            app.config["BASE_URL"] = public_url
            init_webhooks(public_url)

        # ... Initialize Blueprints and the rest of our app

        return app

Now Flask can be started in development by the usual means, setting ``USE_NGROK`` to open a tunnel.

.. code-block:: sh

    USE_NGROK=True FLASK_ENV=development FLASK_APP=server.py flask run

Django
------

In `settings.py <https://docs.djangoproject.com/en/3.0/topics/settings/>`_ of
`our Django project <https://docs.djangoproject.com/en/3.0/intro/tutorial01/#creating-a-project>`_, we should add a
variable that let's us configure from an environment variable whether we want to open a tunnel to
``localhost`` with ``ngrok`` when the dev server starts.

.. code-block:: python

    import os
    import sys

    # ... The rest of our Django settings

    BASE_URL = "http://localhost:8000"

    DEV_SERVER = len(sys.argv) > 1 and sys.argv[1] == "runserver"

    USE_NGROK = os.environ.get("USE_NGROK", "False") == "True" and os.environ.get("RUN_MAIN", None) != "true"

If this flag is set, we want to initialize ``pyngrok`` when Django is booting from its dev server. An easy place
to do this is one of our ``apps.py`` by `extending AppConfig <https://docs.djangoproject.com/en/3.0/ref/applications/#django.apps.AppConfig.ready>`_.

.. code-block:: python

    import sys
    from urllib.parse import urlparse

    from django.apps import AppConfig
    from django.conf import settings


    class CommonConfig(AppConfig):
        name = "myproject.common"
        verbose_name = "Common"

        def ready(self):
            if settings.DEV_SERVER and settings.USE_NGROK:
                # pyngrok will only be installed, and should only ever be initialized, in a dev environment
                from pyngrok import ngrok

                # Get the dev server port (defaults to 8000 for Django, can be overridden with the
                # last arg when calling `runserver`)
                addrport = urlparse("http://{}".format(sys.argv[-1]))
                port = addrport.port if addrport.netloc and addrport.port else 8000

                # Open a ngrok tunnel to the dev server
                public_url = ngrok.connect(port).public_url
                print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

                # Update any base URLs or webhooks to use the public ngrok URL
                settings.BASE_URL = public_url
                CommonConfig.init_webhooks(public_url)

        @staticmethod
        def init_webhooks(base_url):
            # Update inbound traffic via APIs to use the public-facing ngrok URL
            pass

Now the Django dev server can be started by the usual means, setting ``USE_NGROK`` to open a tunnel.

.. code-block:: sh

    USE_NGROK=True python manage.py runserver

FastAPI
-------

In ``server.py``, `where our FastAPI app is initialized <https://fastapi.tiangolo.com/tutorial/first-steps/>`_,
we should add a variable that let's us configure from an environment variable whether we want to tunnel to
``localhost`` with ``ngrok``. We can initialize the ``pyngrok`` tunnel in this same place.

.. code-block:: python

    import os
    import sys

    from fastapi import FastAPI
    from fastapi.logger import logger
    from pydantic import BaseSettings


    class Settings(BaseSettings):
        # ... The rest of our FastAPI settings

        BASE_URL = "http://localhost:8000"
        USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"


    settings = Settings()


    def init_webhooks(base_url):
        # Update inbound traffic via APIs to use the public-facing ngrok URL
        pass


    # Initialize the FastAPI app for a simple web server
    app = FastAPI()

    if settings.USE_NGROK:
        # pyngrok should only ever be installed or initialized in a dev environment when this flag is set
        from pyngrok import ngrok

        # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else 8000

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url
        logger.info("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

        # Update any base URLs or webhooks to use the public ngrok URL
        settings.BASE_URL = public_url
        init_webhooks(public_url)

    # ... Initialize routers and the rest of our app

Now FastAPI can be started by the usual means, with `Uvicorn <https://www.uvicorn.org/#usage>`_, setting
``USE_NGROK`` to open a tunnel.

.. code-block:: sh

    USE_NGROK=True uvicorn server:app

Google Colaboratory
-------------------

Using ``ngrok`` in a `Google Colab Notebook <https://colab.research.google.com/notebooks/intro.ipynb#recent=true>`_
takes just two code cells with ``pyngrok``. Install ``pyngrok`` as a dependency in our Notebook by create a code
block like this:

.. code-block:: sh

    !pip install pyngrok

Colab SSH Example
"""""""""""""""""

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1_ZDG69zjD-6j1dbGbrzAQkyrtlUfdr88?usp=sharing
   :alt: Open SSH Example in Colab

With an SSH server setup and running (as shown fully in the linked example), all we need to do is create another code cell
that uses ``pyngrok`` to open a tunnel to that server.

.. code-block:: python

    import getpass

    from pyngrok import ngrok, conf

    print("Enter your authtoken, which can be copied from https://dashboard.ngrok.com/auth")
    conf.get_default().auth_token = getpass.getpass()

    # Open a TCP ngrok tunnel to the SSH server
    connection_string = ngrok.connect(22, "tcp").public_url

    ssh_url, port = connection_string.strip("tcp://").split(":")
    print(f" * ngrok tunnel available, access with `ssh root@{ssh_url} -p{port}`")

Colab HTTP Example
""""""""""""""""""

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1F-b8Vv_jaThi55_z0VLYLw3DDVnPYZMp?usp=sharing
   :alt: Open HTTP Example in Colab

It can also be useful to expose a web server, process HTTP requests, etc. from within our Notebook. This code block
assumes we have also added ``!pip install flask`` to our dependency code block.

.. code-block:: python

    import os
    import threading

    from flask import Flask
    from pyngrok import ngrok

    os.environ["FLASK_ENV"] = "development"

    app = Flask(__name__)
    port = 5000

    # Open a ngrok tunnel to the HTTP server
    public_url = ngrok.connect(port).public_url
    print(" * ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

    # Update any base URLs to use the public ngrok URL
    app.config["BASE_URL"] = public_url

    # ... Update inbound traffic via APIs to use the public-facing ngrok URL


    # Define Flask routes
    @app.route("/")
    def index():
        return "Hello from Colab!"

    # Start the Flask server in a new thread
    threading.Thread(target=app.run, kwargs={"use_reloader": False}).start()

End-to-End Testing
------------------

Some testing use-cases might mean we want to temporarily expose a route via a ``pyngrok`` tunnel to fully
validate a workflow. For example, an internal end-to-end tester, a step in a pre-deployment validation pipeline, or a
service that automatically updates a status page.

Whatever the case may be, extending `unittest.TestCase <https://docs.python.org/3/library/unittest.html#unittest.TestCase>`_
and adding our own fixtures that start the dev server and open a ``pyngrok`` tunnel is relatively simple. This
snippet builds on the `Flask example above <#flask>`_, but it could be easily modified to work with Django or another
framework if its dev server was started/stopped in the ``start_dev_server()`` and ``stop_dev_server()`` methods
and ``PORT`` was changed.

.. code-block:: python

    import unittest
    import threading

    from flask import request
    from pyngrok import ngrok
    from urllib import request

    from server import create_app


    class PyngrokTestCase(unittest.TestCase):
        # Default Flask port
        PORT = 5000

        @classmethod
        def start_dev_server(cls):
            app = create_app()

            def shutdown():
                request.environ.get("werkzeug.server.shutdown")()

            @app.route("/shutdown", methods=["POST"])
            def route_shutdown():
                shutdown()
                return "", 204

            threading.Thread(target=app.run).start()

        @classmethod
        def stop_dev_server(cls):
            req = request.Request("http://localhost:5000/shutdown", method="POST")
            request.urlopen(req)

        @classmethod
        def init_webhooks(cls, base_url):
            webhook_url = "{}/foo".format(base_url)

            # ... Update inbound traffic via APIs to use the public-facing ngrok URL

        @classmethod
        def init_pyngrok(cls):
            # Open a ngrok tunnel to the dev server
            public_url = ngrok.connect(PORT).public_url

            # Update any base URLs or webhooks to use the public ngrok URL
            cls.init_webhooks(public_url)

        @classmethod
        def setUpClass(cls):
            cls.start_dev_server()

            cls.init_pyngrok()

        @classmethod
        def tearDownClass(cls):
            cls.stop_dev_server()

Now, any test that needs a ``pyngrok`` tunnel can simply extend ``PyngrokTestCase`` to inherit these fixtures.
If we want the ``pyngrok`` tunnel to remain open across numerous tests, it may be more efficient to
`setup these fixtures at the suite or module level instead <https://docs.python.org/3/library/unittest.html#class-and-module-fixtures>`_,
which would also be a simple change.

AWS Lambda (Local)
------------------

Lambdas deployed to AWS can be easily developed locally using ``pyngrok`` and extending the
`Flask example shown above <#flask>`_. In addition to effortless local development, this gives us more flexibility when
writing tests, leveraging a CI, managing revisions, etc.

Let's assume we have a file ``foo_GET.py`` in our ``lambdas`` module and, when deployed, it handles requests to
``GET /foo``. Locally, we can use a Flask route as a shim to funnel requests to this same Lambda handler.

To start, add ``app.register_blueprint(lambda_routes.bp)`` to ``server.py`` from the example above. The create
``lambda_routes.py`` as shown below to handle the routing:

.. code-block:: python

    import json
    from flask import Blueprint, request

    from lambdas.foo_GET import lambda_function as foo_GET

    bp = Blueprint("lambda_routes", __name__)

    @bp.route("/foo")
    def route_foo():
        # This becomes the event in the Lambda handler
        event = {
            "someQueryParam": request.args.get("someQueryParam")
        }

        return json.dumps(foo_GET.lambda_handler(event, {}))

For a complete example of how we can leverage all these things together to rapidly and reliably develop, test,
and deploy AWS Lambda's, check out `the Air Quality Bot repository <https://github.com/alexdlaird/air-quality-bot>`_
and have a look at the ``Makefile`` and ``devserver.py``.

Python HTTP Server
------------------

Python's `http.server module <https://docs.python.org/3/library/http.server.html>`_ also makes for a useful development
server. We can use ``pyngrok`` to expose it to the web via a tunnel, as show in ``server.py`` here:

.. code-block:: python

    import os

    from http.server import HTTPServer, BaseHTTPRequestHandler
    from pyngrok import ngrok

    port = os.environ.get("PORT", 80)

    server_address = ("", port)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)

    public_url = ngrok.connect(port).public_url
    print("ngrok tunnel \"{}\" -> \"http://127.0.0.1:{}\"".format(public_url, port))

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

Here is an example of a simple TCP ping/pong server. It opens a local socket, uses ``ngrok`` to tunnel to that
socket, then the client/server communicate via the publicly exposed address.

For this code to run, we first need to go to
`ngrok's Reserved TCP Addresses <https://dashboard.ngrok.com/reserved>`_ and make a reservation. Set the HOST and PORT
environment variables pointing to that reserved address.

Now create ``server.py`` with the following code:

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
    public_url = ngrok.connect(port, "tcp", remote_addr="{}:{}".format(host, port)}).public_url
    print("ngrok tunnel \"{}\" -> \"tcp://127.0.0.1:{}\"".format(public_url, port))

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

Create ``client.py`` with the following code:

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

And that's it! Data was sent and received from a socket via our ``ngrok`` tunnel.

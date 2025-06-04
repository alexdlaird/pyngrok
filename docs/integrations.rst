====================
Integration Examples
====================

``pyngrok`` is useful in any number of integrations, for instance to test locally without having to deploy or configure
anything. Below are some common usage examples.

Flask
-----
.. image:: https://img.shields.io/badge/Clone_on_GitHub-black?logo=github
   :target: https://github.com/alexdlaird/pyngrok-example-flask

This example project is also setup to `show Docker usage <#docker>`_.

In ``server.py``, `where your Flask app is initialized <https://flask.palletsprojects.com/en/1.1.x/tutorial/factory/#the-application-factory>`_,
you should add a variable that let's you configure from an environment variable whether you want to open a tunnel
to ``localhost`` with ``ngrok`` when the dev server starts. You can initialize the ``pyngrok`` tunnel in this
same place.

.. code-block:: python

    import os
    import sys

    from flask import Flask

    def init_webhooks(base_url):
        # ... Implement updates necessary so inbound traffic uses the public-facing ngrok URL
        pass

    def create_app():
        app = Flask(__name__)

        # Initialize your ngrok settings into Flask
        app.config.from_mapping(
            BASE_URL="http://localhost:5000",
            USE_NGROK=os.environ.get("USE_NGROK", "False") == "True" and os.environ.get("WERKZEUG_RUN_MAIN") != "true"
        )

        if app.config["USE_NGROK"]:
            # Only import pyngrok and install if we're actually going to use it
            from pyngrok import ngrok

            # Get the dev server port (defaults to 5000 for Flask, can be overridden with `--port`
            # when starting the server
            port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "5000"

            # Open a ngrok tunnel to the dev server
            public_url = ngrok.connect(port).public_url
            print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

            # Update any base URLs or webhooks to use the public ngrok URL
            app.config["BASE_URL"] = public_url
            init_webhooks(public_url)

        # ... Implement Blueprints and the rest of your app

        return app

Now Flask can be started in development by the usual means, setting ``USE_NGROK`` to open a tunnel.

.. code-block:: sh

    USE_NGROK=True NGROK_AUTHTOKEN=<AUTHTOKEN> \
        FLASK_APP=server.py \
        flask run

Django
------
.. image:: https://img.shields.io/badge/Clone_on_GitHub-black?logo=github
   :target: https://github.com/alexdlaird/pyngrok-example-django

In `settings.py <https://docs.djangoproject.com/en/3.0/topics/settings/>`_ of
`your Django project <https://docs.djangoproject.com/en/3.0/intro/tutorial01/#creating-a-project>`_, you should add a
variable that let's you configure from an environment variable whether you want to open a tunnel to
``localhost`` with ``ngrok`` when the dev server starts.

.. code-block:: python

    import os
    import sys

    # ... Implement the rest of your Django settings

    BASE_URL = "http://localhost:8000"

    USE_NGROK = os.environ.get("USE_NGROK", "False") == "True" and os.environ.get("RUN_MAIN", None) != "true"

If this flag is set, you want to initialize ``pyngrok`` when Django is booting from its dev server. An easy place
to do this is one of your ``apps.py`` by `extending AppConfig <https://docs.djangoproject.com/en/3.0/ref/applications/#django.apps.AppConfig.ready>`_.

.. code-block:: python

    import os
    import sys
    from urllib.parse import urlparse

    from django.apps import AppConfig
    from django.conf import settings


    class CommonConfig(AppConfig):
        name = "myproject.common"
        verbose_name = "Common"

        def ready(self):
            if settings.USE_NGROK:
                # Only import pyngrok and install if we're actually going to use it
                from pyngrok import ngrok

                # Get the dev server port (defaults to 8000 for Django, can be overridden with the
                # last arg when calling `runserver`)
                addrport = urlparse(f"http://{sys.argv[-1]}")
                port = addrport.port if addrport.netloc and addrport.port else "8000"

                # Open a ngrok tunnel to the dev server
                public_url = ngrok.connect(port).public_url
                print(f"ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

                # Update any base URLs or webhooks to use the public ngrok URL
                settings.BASE_URL = public_url
                CommonConfig.init_webhooks(public_url)

        @staticmethod
        def init_webhooks(base_url):
            # ... Implement updates necessary so inbound traffic uses the public-facing ngrok URL
            pass

Now the Django dev server can be started by the usual means, setting ``USE_NGROK`` to open a tunnel.

.. code-block:: sh

    USE_NGROK=True NGROK_AUTHTOKEN=<AUTHTOKEN> \
        python manage.py runserver

FastAPI
-------
.. image:: https://img.shields.io/badge/Clone_on_GitHub-black?logo=github
   :target: https://github.com/alexdlaird/pyngrok-example-fastapi

In ``server.py``, `where your FastAPI app is initialized <https://fastapi.tiangolo.com/tutorial/first-steps/>`_,
you should add a variable that let's you configure from an environment variable whether you want to tunnel to
``localhost`` with ``ngrok``. You can initialize the ``pyngrok`` tunnel in this same place.

.. code-block:: python

    import os
    import sys

    from fastapi import FastAPI
    from fastapi.logger import logger
    from pydantic import BaseSettings


    class Settings(BaseSettings):
        # ... Implement the rest of your FastAPI settings

        BASE_URL = "http://localhost:8000"
        USE_NGROK = os.environ.get("USE_NGROK", "False") == "True"


    settings = Settings()


    def init_webhooks(base_url):
        # ... Implement updates necessary so inbound traffic uses the public-facing ngrok URL
        pass


    # Initialize the FastAPI app for a simple web server
    app = FastAPI()

    if settings.USE_NGROK:
        # Only import pyngrok and install if we're actually going to use it
        from pyngrok import ngrok

        # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
        # when starting the server
        port = sys.argv[sys.argv.index("--port") + 1] if "--port" in sys.argv else "8000"

        # Open a ngrok tunnel to the dev server
        public_url = ngrok.connect(port).public_url
        logger.info(f"ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

        # Update any base URLs or webhooks to use the public ngrok URL
        settings.BASE_URL = public_url
        init_webhooks(public_url)

    # ... Implement routers and the rest of your app

Now FastAPI can be started by the usual means, with `Uvicorn <https://www.uvicorn.org/#usage>`_, setting
``USE_NGROK`` to open a tunnel.

.. code-block:: sh

    USE_NGROK=True NGROK_AUTHTOKEN=<AUTHTOKEN> \
        uvicorn server:app

Docker
------

``pyngrok`` provides `pre-built container images on Docker Hub <https://hub.docker.com/r/alexdlaird/pyngrok>`_.

To launch the container in to a Python shell, run:

.. code-block:: shell

    docker run -e NGROK_AUTHTOKEN=<NGROK_AUTHTOKEN> -it alexdlaird/pyngrok

The `pyngrok-example-flask repository <https://github.com/alexdlaird/pyngrok-example-flask>`_ also includes a
``Dockerfile`` and ``make`` commands to run it, if you would like to see a complete example.

Here is an example of how you could launch the container using ``docker-compose.yml``, where you also want a given Python
script to run on startup:

.. code-block:: yaml

    services:
      ngrok:
        image: alexdlaird/pyngrok
        env_file: ".env"
        command:
          - "python /root/my-script.py"
        volumes:
          - ./my-script.py:/root/my-script.py
        ports:
          - 4040:4040

Then launch it with:

.. code-block:: shell

    docker compose up -d

For more usage examples, as well as a breakdown of image tags, head over to `Docker Hub <https://hub.docker.com/r/alexdlaird/pyngrok>`_.

Google Colaboratory
-------------------

Using ``ngrok`` in a `Google Colab Notebook <https://colab.research.google.com/notebooks/intro.ipynb#recent=true>`_
takes just two code cells with ``pyngrok``. Install ``pyngrok`` as a dependency in your Notebook by creating a code
block like this:

.. code-block:: sh

    !pip install pyngrok

Colab SSH Example
"""""""""""""""""

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1_ZDG69zjD-6j1dbGbrzAQkyrtlUfdr88?usp=sharing
   :alt: Open SSH Example in Colab

With an SSH server setup and running (as shown fully in the linked example), all you need to do is create another code
cell that uses ``pyngrok`` to open a tunnel to that server.

.. code-block:: python

    import getpass

    from pyngrok import ngrok, conf

    print("Enter your authtoken, which can be copied from https://dashboard.ngrok.com/get-started/your-authtoken")
    conf.get_default().auth_token = getpass.getpass()

    # Open a TCP ngrok tunnel to the SSH server
    connection_string = ngrok.connect("22", "tcp").public_url

    ssh_url, port = connection_string.strip("tcp://").split(":")
    print(f" * ngrok tunnel available, access with `ssh root@{ssh_url} -p{port}`")

Colab HTTP Example
""""""""""""""""""

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :target: https://colab.research.google.com/drive/1F-b8Vv_jaThi55_z0VLYLw3DDVnPYZMp?usp=sharing
   :alt: Open HTTP Example in Colab

It can also be useful to expose a web server, process HTTP requests, etc. from within your Notebook. This code block
assumes you have also added ``!pip install flask`` to your dependency code block.

.. code-block:: python

    import os
    import threading

    from flask import Flask
    from pyngrok import ngrok

    app = Flask(__name__)
    port = "5000"

    # Open a ngrok tunnel to the HTTP server
    public_url = ngrok.connect(port).public_url
    print(f" * ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

    # Update any base URLs to use the public ngrok URL
    app.config["BASE_URL"] = public_url

    # ... Implement updates necessary so inbound traffic uses the public-facing ngrok URL

    # Define Flask routes
    @app.route("/")
    def index():
        return "Hello from Colab!"

    # Start the Flask server in a new thread
    threading.Thread(target=app.run, kwargs={"use_reloader": False}).start()

End-to-End Testing
------------------

Some testing use-cases might mean you want to temporarily expose a route via a ``pyngrok`` tunnel to fully
validate a workflow. For example, an internal end-to-end tester, a step in a pre-deployment validation pipeline, or a
service that automatically updates a status page.

Whatever the case may be, extending `unittest.TestCase <https://docs.python.org/3/library/unittest.html#unittest.TestCase>`_
and adding your own fixtures that start the dev server and open a ``pyngrok`` tunnel is relatively simple. This
snippet builds on the `Flask example above <#flask>`_, but it could be modified to work with other
frameworks.

.. code-block:: python

    import os
    import signal
    import unittest
    import threading

    from flask import request
    from pyngrok import ngrok
    from urllib import request

    from server import create_app


    class PyngrokTestCase(unittest.TestCase):
        @classmethod
        def start_dev_server(cls):
            app = create_app()

            def shutdown():
                # Newer versions of Werkzeug and Flask don't provide this environment variable
                if "werkzeug.server.shutdown" in request.environ:
                    request.environ.get("werkzeug.server.shutdown")()
                else:
                    # Windows does not provide SIGKILL, go with SIGTERM then
                    sig = getattr(signal, "SIGKILL", signal.SIGTERM)
                    os.kill(os.getpid(), sig)

            @app.route("/shutdown", methods=["POST"])
            def route_shutdown():
                shutdown()
                return "", 204

            threading.Thread(target=app.run).start()

            return app

        @classmethod
        def stop_dev_server(cls):
            req = request.Request("http://localhost:5000/shutdown", method="POST")
            request.urlopen(req)

        @classmethod
        def setUpClass(cls):
            # Ensure a tunnel is opened and webhooks initialized when the dev server is started
            os.environ["USE_NGROK"] = True

            app = cls.start_dev_server()

            cls.base_url = app.config["BASE_URL"]

            # ... Implement other initializes so you can assert against the inbound traffic through your tunnel

        @classmethod
        def tearDownClass(cls):
            cls.stop_dev_server()

            ngrok.kill()

Now, any test that needs to assert against responses through a ``pyngrok`` tunnel can simply extend ``PyngrokTestCase``
to inherit these fixtures. If you want the ``pyngrok`` tunnel to remain open across numerous tests, it may be more
efficient to `setup these fixtures at the suite or module level instead <https://docs.python.org/3/library/unittest.html#class-and-module-fixtures>`_.

AWS Lambda (Local)
------------------

Lambdas deployed to AWS can be easily developed locally using ``pyngrok`` and extending the
`Flask example shown above <#flask>`_. In addition to effortless local development, this gives you more flexibility when
writing tests, leveraging a CI, managing revisions, etc.

Let's assume you have a file ``foo_GET.py`` in your ``lambdas`` module and, when deployed, it handles requests to
``GET /foo``. Locally, you can use a Flask route as a shim to funnel requests to this same Lambda handler.

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

For a complete example of how you can leverage all these things together to rapidly develop, test,
and deploy AWS Lambda's, check out `the Air Quality Bot repository <https://github.com/alexdlaird/air-quality-bot>`_
and have a look at the ``Makefile`` and ``devserver.py``.

Simple HTTP Server
------------------

Python's `http.server module <https://docs.python.org/3/library/http.server.html>`_ also makes for a useful development
server. You can use ``pyngrok`` to expose it to the web via a tunnel, as shown in ``server.py`` here:

.. code-block:: python

    import os

    from http.server import HTTPServer, BaseHTTPRequestHandler
    from pyngrok import ngrok

    port = os.environ.get("PORT", "80")

    server_address = ("", port)
    httpd = HTTPServer(server_address, BaseHTTPRequestHandler)

    public_url = ngrok.connect(port).public_url
    print(f"ngrok tunnel \"{public_url}\" -> \"http://127.0.0.1:{port}\"")

    try:
        # Block until CTRL-C or some other terminating event
        httpd.serve_forever()
    except KeyboardInterrupt:
       print(" Shutting down server.")

       httpd.socket.close()

You can then run this script to start the server.

.. code-block:: sh

    NGROK_AUTHTOKEN=<AUTHTOKEN> python server.py

Simple TCP Server and Client
----------------------------

Here is an example of a simple TCP ping/pong server. It opens a local socket, uses ``ngrok`` to tunnel to that
socket, then the client/server communicate via the publicly exposed address.

For this code to run, you'll first need a reserved TCP address, which you obtain using
`ngrok's API <index.html#ngrok-s-api>`_. Set the ``HOST`` and ``PORT`` environment variables pointing to that reserved
address.

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
    public_url = ngrok.connect(port, "tcp", remote_addr=f"{host}:{port}").public_url
    print(f"ngrok tunnel \"{public_url}\" -> \"tcp://127.0.0.1:{port}\"")

    while True:
        connection = None
        try:
            # Wait for a connection
            print("\nWaiting for a connection ...")
            connection, client_address = sock.accept()

            print(f"... connection established from {client_address}")

            # Receive the message, send a response
            while True:
                data = connection.recv(1024)
                if data:
                    print("Received: {data}".format(data=data.decode("utf-8")))

                    message = "pong"
                    print(f"Sending: {message}")
                    connection.sendall(message.encode("utf-8"))
                else:
                    break
        except KeyboardInterrupt:
            print(" Shutting down server.")

            if connection:
                connection.close()
            break

    sock.close()

In a terminal window, you can now start your socket server:

.. code-block:: sh

    NGROK_AUTHTOKEN=<AUTHTOKEN> \
        HOST="1.tcp.ngrok.io" PORT=12345 \
        python server.py

It's now waiting for incoming connections, so let's write a client to connect to it and send it something.

Create ``client.py`` with the following code:

.. code-block:: python

    import os
    import socket

    host = os.environ.get("HOST")
    port = int(os.environ.get("PORT"))

    # Create a TCP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server with the socket via your ngrok tunnel
    server_address = (host, port)
    sock.connect(server_address)
    print(f"Connected to {host}:{port}")

    # Send the message
    message = "ping"
    print(f"Sending: {message}")
    sock.sendall(message.encode("utf-8"))

    # Await a response
    data_received = 0
    data_expected = len(message)

    while data_received < data_expected:
        data = sock.recv(1024)
        data_received += len(data)
        print("Received: {data}".format(data=data.decode("utf-8")))

    sock.close()

In another terminal window, you can run your client:

.. code-block:: sh

    HOST="1.tcp.ngrok.io" PORT=12345 \
        python client.py

And that's it! Data was sent and received from a socket via your ``ngrok`` tunnel.

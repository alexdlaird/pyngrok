:orphan:

====================
Integration Examples
====================

:code:`pyngrok` is useful in any number of integrations to let you test things locally without having to deploy,
for instance to test locally without having to deploy or configure anything. Below are some common usage examples.

Flask
-----
TBD

Django
------
In :code:`settings.py`, add a variable that let's us control whether we want to use :code:`ngrok` or not from an environment
variable, so for instance:

.. code-block:: python

    USE_NGROK = os.environ.get('USE_NGROK', 'False') == 'True'

If this flag is set, we want to initialize :code:`pyngrok` when Django is booting. An easy place to do this is in
one of our :code:`apps.py` files. Simply add something like the following to `the AppConfig's ready() method <https://docs.djangoproject.com/en/3.0/ref/applications/#django.apps.AppConfig.ready>`_.

.. code-block:: python

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
        pass

Then Django can be started using the usual means, also setting our `ngrok` flag.

.. code-block:: sh

    USE_NGROK=True python manage.py runserver

AWS Lambda (Local)
------------------
TBD

Python HTTP Server
------------------
TBD

Python TCP Socket
-----------------
TBD

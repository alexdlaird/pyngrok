===============
Troubleshooting
===============

``pyngrok`` is a Python wrapper for `ngrok <https://ngrok.com/>`_, so often errors that occur (especially during
startup) are a result of a ``ngrok`` configuration error and not a bug in ``pyngrok``. Hopefully this page can
give you some useful tips to debug these issues.

Test on the Command Line
------------------------

When you install ``pyngrok`` with ``pip install pyngrok``, ``ngrok`` should available from the command
line. First ensure this is true by checking to see if ``pyngrok``'s version of ``ngrok`` is properly setup in
your path. Running ``ngrok`` with no args from the command line should show ``pyngrok`` version at the very
end.

.. code-block:: shell

    bash-3.2$ ngrok
    NAME:
       ngrok - tunnel local ports to public URLs and inspect traffic

    ...

    PYNGROK VERSION:
       5.0.0

.. note::

    If ``PYNGROK VERSION`` is not seen in the output here, something else is managing ``ngrok`` (perhaps
    another ``ngrok`` wrapper installed through `Homebrew <https://brew.sh/>`_ or `npm <https://www.npmjs.com/>`_).
    If you'd prefer ``pyngrok`` manage ``ngrok`` for you, you'll first need to
    `reorder things in your $PATH <https://stackoverflow.com/a/32170849/1128413>`_ to fix this, then you can continue
    troubleshooting on the command line.

With ``PYNGROK VERSION`` shown in your output here, you know things are setup properly. Next try starting
``ngrok`` headless:

.. code-block:: shell

    bash-3.2$ ngrok start --none --log stdout

If that works, try starting a simple HTTP tunnel:

.. code-block:: shell

    bash-3.2$ ngrok http 5000 --log stdout

If neither of these work, the logs should be dumped to the console for you to troubleshoot ``ngrok``
directly. If both of these work, you know ``pyngrok`` is properly installed on your system and able to access
the ``ngrok`` binary, meaning the problem is likely a configuration issue in your Python application.

Enable Logging to the Console
-----------------------------

Printing logs to the console can be a quick way to debug common issues by surfacing their root cause. To do this,
ensure you have a handler streaming logs and your level is set to ``DEBUG``. Here is a simple example:

.. code-block:: python

    import logging

    from pyngrok import ngrok

    # Setup a logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(handler)

    # Then call the pyngrok method throwing the error, for example
    ngrok.connect(5000)


Programmatically Inspect the Logs
---------------------------------

``ngrok`` logs are parsed by the :class:`~pyngrok.process.NgrokProcess`, and you can inspect them by iterating over
its ``logs`` variable or giving it a `log_event_callback <index.html#event-logs>`_.

If you're seeing the :class:`~pyngrok.process.NgrokProcess` fail with a :class:`~pyngrok.exception.PyngrokNgrokError`
exception, these logs are also available on the exception itself. Catch the exception and inspect ``ngrok_logs``
and ``ngrok_error`` for more insight in to where ``ngrok`` is failing.

Test in the Python Console
--------------------------

Try to execute the same code that is giving you an error from the Python console instead. Be sure to pair this with
enabling logging (as illustrated in the section above) so you can see where things are going wrong.

.. code-block:: shell

    ~ ❯❯❯ python
    Python 3.11.4 (main, Jun 20 2023, 17:23:00) [Clang 14.0.3 (clang-1403.0.22.14.1)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import logging
    >>> from pyngrok import ngrok
    >>> logger = logging.getLogger()
    >>> logger.setLevel(logging.DEBUG)
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    >>> logger.addHandler(handler)
    >>> ngrok.connect()
    2023-09-14 08:33:24,465 - pyngrok.ngrok - INFO - Opening tunnel named: http-80-7ce9805f-b438-48d0-92ab-ac305ba14869
    2023-09-14 08:33:24,480 - pyngrok.process - DEBUG - ngrok process starting with PID: 93822
    2023-09-14 08:33:25,165 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg="no configuration paths supplied"
    2023-09-14 08:33:25,165 - pyngrok.process.ngrok - WARNING - t=2023-09-14T08:33:25-0500 lvl=warn msg="ngrok config file found at legacy location, move to XDG location" xdg_path="/Users/alexdlaird/Library/Application Support/ngrok/ngrok.yml" legacy_path=/Users/alexdlaird/.ngrok2/ngrok.yml
    2023-09-14 08:33:25,165 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg="using configuration at default config path" path=/Users/alexdlaird/.ngrok2/ngrok.yml
    2023-09-14 08:33:25,165 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg="open config file" path=/Users/alexdlaird/.ngrok2/ngrok.yml err=nil
    2023-09-14 08:33:25,166 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg="starting web service" obj=web addr=127.0.0.1:4040 allow_hosts=[]
    2023-09-14 08:33:25,516 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg="client session established" obj=tunnels.session obj=csess id=4b243123afe2
    2023-09-14 08:33:25,517 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg="tunnel session started" obj=tunnels.session
    2023-09-14 08:33:25,539 - pyngrok.process - DEBUG - ngrok process has started with API URL: http://127.0.0.1:4040
    2023-09-14 08:33:25,539 - pyngrok.process - DEBUG - Monitor thread will be started
    2023-09-14 08:33:25,539 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg=start pg=/api/tunnels id=96fc3b90b80174d0
    2023-09-14 08:33:25,539 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg=end pg=/api/tunnels id=96fc3b90b80174d0 status=200 dur=286.042µs
    2023-09-14 08:33:25,540 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg=start pg=/api/tunnels id=394a97d2d43ba05b
    2023-09-14 08:33:25,540 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg=end pg=/api/tunnels id=394a97d2d43ba05b status=200 dur=115.208µs
    2023-09-14 08:33:25,540 - pyngrok.ngrok - DEBUG - Creating tunnel with options: {'name': 'http-80-7ce9805f-b438-48d0-92ab-ac305ba14869', 'addr': '80', 'proto': 'http'}
    2023-09-14 08:33:25,541 - pyngrok.ngrok - DEBUG - Making POST request to http://127.0.0.1:4040/api/tunnels with data: b'{"name": "http-80-7ce9805f-b438-48d0-92ab-ac305ba14869", "addr": "80", "proto": "http"}'
    2023-09-14 08:33:25,541 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg=start pg=/api/tunnels id=a3d58985a01eb3b4
    2023-09-14 08:33:25,594 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg="started tunnel" obj=tunnels name=http-80-7ce9805f-b438-48d0-92ab-ac305ba14869 addr=http://localhost:80 url=https://<pub_sub>.ngrok.app
    2023-09-14 08:33:25,594 - pyngrok.process.ngrok - INFO - t=2023-09-14T08:33:25-0500 lvl=info msg=end pg=/api/tunnels id=a3d58985a01eb3b4 status=201 dur=53.108ms
    2023-09-14 08:33:25,595 - pyngrok.ngrok - DEBUG - Response 201: {"name":"http-80-7ce9805f-b438-48d0-92ab-ac305ba14869","ID":"d18a9e4a6237ca6ceb58d96fc9f330fc","uri":"/api/tunnels/http-80-7ce9805f-b438-48d0-92ab-ac305ba14869","public_url":"https://<pub_sub>.ngrok.app","proto":"https","config":{"addr":"http://localhost:80","inspect":true},"metrics":{"conns":{"count":0,"gauge":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0},"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0}}}
    <NgrokTunnel: "https://<pub_sub>.ngrok.app" -> "http://localhost:80">

Check the Inspector at http://localhost:4040
--------------------------------------------

Check to see if you are able to access the `traffic inspection interface <https://ngrok.com/docs#getting-started-inspect>`_
via a web browser. If so, this at least means ``ngrok`` is able to start before throwing the error.

``ngrok`` Documentation
---------------------------

Familiarize yourself with the `ngrok documentation <https://ngrok.com/docs>`_, especially the sections pertaining to
`the config file <https://ngrok.com/docs/ngrok-agent/config>`_ and `the client API <https://ngrok.com/docs/ngrok-agent/api>`_.

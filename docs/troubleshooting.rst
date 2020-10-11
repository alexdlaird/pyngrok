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

    bash-3.2$ python
    Python 3.7.6 (default, Dec 30 2019, 19:38:28)
    [Clang 11.0.0 (clang-1100.0.33.16)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import logging
    >>> from pyngrok import ngrok
    >>> logger = logging.getLogger()
    >>> logger.setLevel(logging.DEBUG)
    >>> handler = logging.StreamHandler()
    >>> handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    >>> logger.addHandler(handler)
    >>> ngrok.connect()
    2020-10-08 22:36:59,533 - pyngrok.ngrok - INFO - Opening tunnel named: http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d
    2020-10-08 22:36:59,543 - pyngrok.process - DEBUG - ngrok process starting with PID: 8241
    2020-10-08 22:36:59,568 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:36:59-0700 lvl=info msg="no configuration paths supplied"
    2020-10-08 22:36:59,569 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:36:59-0700 lvl=info msg="using configuration at default config path" path=/Users/<username>/.ngrok2/ngrok.yml
    2020-10-08 22:36:59,570 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:36:59-0700 lvl=info msg="open config file" path=/Users/<username>/.ngrok2/ngrok.yml err=nil
    2020-10-08 22:36:59,572 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:36:59-0700 lvl=info msg="starting web service" obj=web addr=127.0.0.1:4040
    2020-10-08 22:37:00,036 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg="tunnel session started" obj=tunnels.session
    2020-10-08 22:37:00,036 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg="client session established" obj=csess id=af124e14bcf6
    2020-10-08 22:37:00,048 - pyngrok.process - DEBUG - ngrok process has started with API URL: http://127.0.0.1:4040
    2020-10-08 22:37:00,048 - pyngrok.process - DEBUG - Monitor thread will be started
    2020-10-08 22:37:00,049 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=start pg=/api/tunnels id=ae13ec9c8181c47b
    2020-10-08 22:37:00,049 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=end pg=/api/tunnels id=ae13ec9c8181c47b status=200 dur=295.273µs
    2020-10-08 22:37:00,050 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=start pg=/api/tunnels id=0d996b4b278c5b35
    2020-10-08 22:37:00,050 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=end pg=/api/tunnels id=0d996b4b278c5b35 status=200 dur=87.721µs
    2020-10-08 22:37:00,050 - pyngrok.ngrok - DEBUG - Creating tunnel with options: {'name': 'http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d', 'addr': '80', 'proto': 'http'}
    2020-10-08 22:37:00,051 - pyngrok.ngrok - DEBUG - Making POST request to http://127.0.0.1:4040/api/tunnels with data: b'{"name": "http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d", "addr": "80", "proto": "http"}'
    2020-10-08 22:37:00,052 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=start pg=/api/tunnels id=0576c6624325620b
    2020-10-08 22:37:00,270 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg="started tunnel" obj=tunnels name="http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d (http)" addr=http://localhost:80 url=http://<public_sub>.ngrok.io
    2020-10-08 22:37:00,271 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg="started tunnel" obj=tunnels name=http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d addr=http://localhost:80 url=https://<public_sub>.ngrok.io
    2020-10-08 22:37:00,272 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=end pg=/api/tunnels id=0576c6624325620b status=201 dur=217.126877ms
    2020-10-08 22:37:00,272 - pyngrok.ngrok - DEBUG - Response 201: {"name":"http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d","uri":"/api/tunnels/http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d","public_url":"https://<public_sub>.ngrok.io","proto":"https","config":{"addr":"http://localhost:80","inspect":true},"metrics":{"conns":{"count":0,"gauge":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0},"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0}}}
    2020-10-08 22:37:00,273 - pyngrok.ngrok - DEBUG - Making GET request to http://127.0.0.1:4040/api/tunnels/http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d%20%28http%29 with data: None
    2020-10-08 22:37:00,275 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=start pg="/api/tunnels/http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d (http)" id=6b8012fded209914
    2020-10-08 22:37:00,276 - pyngrok.process.ngrok - INFO - t=2020-10-08T22:37:00-0700 lvl=info msg=end pg="/api/tunnels/http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d (http)" id=6b8012fded209914 status=200 dur=246.304µs
    2020-10-08 22:37:00,277 - pyngrok.ngrok - DEBUG - Response 200: {"name":"http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d (http)","uri":"/api/tunnels/http-80-2c872002-24f6-4fe4-b6ec-3af273f45d1d%20%28http%29","public_url":"http://<public_sub>.ngrok.io","proto":"http","config":{"addr":"http://localhost:80","inspect":true},"metrics":{"conns":{"count":0,"gauge":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0},"http":{"count":0,"rate1":0,"rate5":0,"rate15":0,"p50":0,"p90":0,"p95":0,"p99":0}}}
    <NgrokTunnel: "http://<public_sub>.ngrok.io" -> "http://localhost:80">

Check the Inspector at http://localhost:4040
--------------------------------------------

Check to see if you are able to access the `traffic inspection interface <https://ngrok.com/docs#getting-started-inspect>`_
via a web browser. If so, this at least means ``ngrok`` is able to start before throwing the error.

``ngrok`` Documentation
---------------------------

Familiarize yourself with the `ngrok documentation <https://ngrok.com/docs>`_, especially the sections pertaining to
`the config file <https://ngrok.com/docs#config>`_ and `the client API <https://ngrok.com/docs#client-api>`_.

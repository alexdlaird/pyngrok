# pyngrok - a Python wrapper for ngrok

[![PyPI version](https://badge.fury.io/py/pyngrok.svg)](https://badge.fury.io/py/pyngrok)
[![image](https://img.shields.io/pypi/pyversions/pyngrok.svg)](https://pypi.org/project/pyngrok/)
[![codecov](https://codecov.io/gh/alexdlaird/pyngrok/branch/master/graph/badge.svg)](https://codecov.io/gh/alexdlaird/pyngrok)
[![Build Status](https://travis-ci.org/alexdlaird/pyngrok.svg?branch=master)](https://travis-ci.org/alexdlaird/pyngrok)

## install

`pyngrok` is available on [PyPI](https://pypi.org/project/pyngrok/) and can be installed using `pip`.

```
pip install pyngrok
```

The package comes with support for downloading and using its own version of [ngrok](https://ngrok.com/), or you can
specify a path to a binary when establishing a connection.

## connect

```python
from pyngrok import ngrok

public_url1 = ngrok.connect() # tunnel to port 80
public_url2 = ngrok.connect(5000) # tunnel to port 5000
```

The `connect` method also takes an optional `options` dictionary, which can accept any arbitrary parameter defined in [the ngrok documentation](https://ngrok.com/docs#tunnel-definitions).

Retreiving a list of active `NgrokTunnel` objects is just as easy.

```python
tunnels = ngrok.get_tunnels()
public_url = tunnels[0].public_url # a public ngrok URL that tunnels to port 80 (ex. http://64e3ddef.ngrok.io)
```

The `ngrok` process itself is also available to you in the `NgrokProcess` object. This object also holds reference to the client API URL.

```python
ngrok_process = ngrok.get_ngrok_process()
api_url = ngrok_process.api_url # the ngrok client API URL (usually http://127.0.0.1:4040)
```

After the `ngrok` process is invoked (by calling `connect` or `get_tunnels`), it will remain alive until the Python process terminates. If your app is long-lived, this means the tunnels will stay open until you call
`ngrok.disconnect(5000)` to shutdown a port, `ngrok.kill()` to end the `ngrok` process, or kill the entire process.

If you have a short-lived app, like a CLI, but want the tunnels to remain open until the user terminates, do the following on the `ngrok_process` retrieved above:

```python
ngrok_process.process.wait() # block until CTRL-C or some other terminating event
```

## authtoken

If you have a [`ngrok` account](https://dashboard.ngrok.com), you can set your `authtoken` to enable your account's features with this package.

```python
from pyngrok import ngrok

ngrok.set_auth_token("807ad30a-73be-48d8")
```

## config file

By default, [the `ngrok` config file](https://ngrok.com/docs#config) lives in the `.ngrok2` folder in your home
directory. If you would like to specify a custom config file, pass the `config_path` parameter:

```python
from pyngrok import ngrok

CONFIG_PATH = "/opt/ngrok/config.yml"

ngrok.connect(config_path=CONFIG_PATH)
```

## binary path

If you would like to use your own `ngrok` binary instead of the one that comes with this package, you can
do this in one of two ways. Either pass the `ngrok_path` argument to each command:

```python
from pyngrok import ngrok

NGROK_PATH = "/usr/local/bin/ngrok"

ngrok.get_tunnels(ngrok_path=NGROK_PATH)
```

or override the `DEFAULT_NGROK_PATH` variable:

```python
from pyngrok import ngrok

ngrok.DEFAULT_NGROK_PATH = "/usr/local/bin/ngrok"

ngrok.connect(5000)
```

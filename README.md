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
import time
from pyngrok import ngrok

ngrok.connect() # tunnel to port 80
ngrok.connect(5000) # tunnel to port 5000

# Wait a second to ensure ngrok API has synced
time.sleep(1)

tunnels = ngrok.get_tunnels()
public_url = tunnels[0].public_url # a public ngrok URL that tunnels to port 80 (ex. http://64e3ddef.ngrok.io)

ngrok_process = ngrok.get_ngrok_process()
api_url = ngrok_process.api_url # the ngrok client API URL (usually http://127.0.0.1:4040)
```

You are also able to pass an `options` parameter (dict), as defined in [the ngrok documentation](https://ngrok.com/docs#tunnel-definitions),
when calling `connect`.

The `ngrok` process, after an initiating event (like `connect` or `get_tunnels`) will remain alive until the
Python process terminates. If your app is long-lived, this means the above processes will remain alive until you call
`ngrok.disconnect(5000)` to shutdown a port or `ngrok.kill()` to terminate the entire process.

If you have a short-lived app but want it to remain running until the `ngrok` process terminates (for instance, a CLI
tool), get the `ngrok_process` as shown above and do `ngrok_process.process.wait()`

## authtoken

If you have an `ngrok` account, you can set the `authtoken` to enable your account's features.

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

## custom binary options

If you would like to use your own `ngrok` binary instead of relying on the one that comes with this package, this can
be done one of two ways. You can either pass the `ngrok_path` argument to each command:

```python
from pyngrok import ngrok

NGROK_PATH = "/usr/local/bin/ngrok"

ngrok.get_tunnels(ngrok_path=NGROK_PATH)
```

or you can override the packages `DEFAULT_NGROK_PATH` variable:

```python
from pyngrok import ngrok

ngrok.DEFAULT_NGROK_PATH="/usr/local/bin/ngrok"

ngrok.connect(5000)
```

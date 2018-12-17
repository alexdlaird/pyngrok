[![Build Status](https://travis-ci.org/alexdlaird/pyngrok.svg?branch=master)](https://travis-ci.org/alexdlaird/pyngrok)
[![Python 3](https://pyup.io/repos/github/HeliumEdu/heliumcli/python-3-shield.svg)](https://pyup.io/repos/github/alexdlaird/pyngrok/)
[![PyPI version](https://badge.fury.io/py/pyngrok.svg)](https://badge.fury.io/py/pyngrok)


# pyngrok

## Getting Started

Note: this package is still in early development.

The `pyngrok` package is a [ngrok](https://ngrok.com/) wrapper for Python. The module will download
and use its own `ngrok` binaries if none are provided.

Here is an example of basic usage:

```
public_url = ngrok.connect() # http://localhost:80
public_url = ngrok.connect(5000, "https") # https://localhost:5000

tunnels = ngrok.get_tunnels()
```

More functionality and documentation will be published soon.

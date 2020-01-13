__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "1.4.3"


class PyngrokError(Exception):
    """
    Raised when a general `pyngrok` error has occurred.
    """
    pass


class PyngrokNgrokInstallError(PyngrokError):
    """
    Raised when an error has occurred while downloading and installing the `ngrok` binary.
    """
    pass


class PyngrokNgrokError(PyngrokError):
    """
    Raised when an error occurs interacting directly with the `ngrok` binary.

    :var string error: A description of the error being thrown.
    :var list ngrok_errors: A list of errors reported by the `ngrok` process.
    """

    def __init__(self, error, ngrok_errors=None):
        super(PyngrokNgrokError, self).__init__(error)

        if ngrok_errors is None:
            ngrok_errors = []

        self.ngrok_errors = ngrok_errors


class PyngrokNgrokHTTPError(PyngrokNgrokError):
    """
    Raised when an error occurs making a request to the `ngrok` web interface. The `body`
    contains the error response received from `ngrok`.

    :var string error: A description of the error being thrown.
    :var string url: The request URL that failed.
    :var int status_code: The response status code from `ngrok`.
    :var string message: The response message from `ngrok`.
    :var dict headers: The request headers sent to `ngrok`.
    :var string body: The response body from `ngrok`.
    """

    def __init__(self, error, url, status_code, message, headers, body):
        super(PyngrokNgrokHTTPError, self).__init__(error)

        self.url = url
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body


class PyngrokNgrokURLError(PyngrokNgrokError):
    """
    Raised when an error occurs when trying to initiate an API request.

    :var string error: A description of the error being thrown.
    :var string reason: The reason for the URL error.
    """

    def __init__(self, error, reason):
        super(PyngrokNgrokURLError, self).__init__(error)

        self.reason = reason

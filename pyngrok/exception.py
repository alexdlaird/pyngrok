__author__ = "Alex Laird"
__copyright__ = "Copyright 2020, Alex Laird"
__version__ = "2.0.3"


class PyngrokError(Exception):
    """
    Raised when a general `pyngrok` error has occurred.
    """
    pass


class PyngrokSecurityError(PyngrokError):
    """
    Raised when a `pyngrok` security error has occurred.
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
    :var string ngrok_logs: The `ngrok` logs, which may be useful for debugging the error.
    :var string ngrok_error: The error that caused the `ngrok` process to fail.
    """

    def __init__(self, error, ngrok_logs=None, ngrok_error=None):
        super(PyngrokNgrokError, self).__init__(error)

        if ngrok_logs is None:
            ngrok_logs = []

        self.ngrok_logs = ngrok_logs
        self.ngrok_error = ngrok_error


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

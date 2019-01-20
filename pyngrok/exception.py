__author__ = "Alex Laird"
__copyright__ = "Copyright 2019, Alex Laird"
__version__ = "1.3.0"


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
    """
    pass


class PyngrokNgrokHTTPError(PyngrokNgrokError):
    """
    Raised when an error occurs making a request to the `ngrok` web interface. The `body`
    contains the error response received from `ngrok`.

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

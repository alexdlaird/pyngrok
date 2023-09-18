from typing import Any, Optional, List

__author__ = "Alex Laird"
__copyright__ = "Copyright 2023, Alex Laird"
__version__ = "6.1.1"


class PyngrokError(Exception):
    """
    Raised when a general ``pyngrok`` error has occurred.
    """
    pass


class PyngrokSecurityError(PyngrokError):
    """
    Raised when a ``pyngrok`` security error has occurred.
    """
    pass


class PyngrokNgrokInstallError(PyngrokError):
    """
    Raised when an error has occurred while downloading and installing the ``ngrok`` binary.
    """
    pass


class PyngrokNgrokError(PyngrokError):
    """
    Raised when an error occurs interacting directly with the ``ngrok`` binary.

    :var ngrok_logs: The ``ngrok`` logs, which may be useful for debugging the error.
    :vartype ngrok_logs: list[NgrokLog]
    :var ngrok_error: The error that caused the ``ngrok`` process to fail.
    :vartype ngrok_error: str
    """
    ngrok_logs: List[Any]
    ngrok_error: Optional[str]

    def __init__(self,
                 error: str,
                 ngrok_logs: Optional[List[Any]] = None,
                 ngrok_error: Optional[str] = None) -> None:
        super(PyngrokNgrokError, self).__init__(error)

        if ngrok_logs is None:
            ngrok_logs = []

        self.ngrok_logs = ngrok_logs
        self.ngrok_error = ngrok_error


class PyngrokNgrokHTTPError(PyngrokNgrokError):
    """
    Raised when an error occurs making a request to the ``ngrok`` web interface. The ``body``
    contains the error response received from ``ngrok``.

    :var url: The request URL that failed.
    :vartype url: str
    :var status_code: The response status code from ``ngrok``.
    :vartype status_code: int
    :var message: The response message from ``ngrok``.
    :vartype message: str
    :var headers: The request headers sent to ``ngrok``.
    :vartype headers: dict[str, str]
    :var body: The response body from ``ngrok``.
    :vartype body: str
    """
    ur: str
    status_code: int
    message: Optional[str]
    headers: Any
    body: str

    def __init__(self,
                 error: str,
                 url: str,
                 status_code: int,
                 message: Optional[str],
                 headers: Any,
                 body: str) -> None:
        super(PyngrokNgrokHTTPError, self).__init__(error)

        self.url = url
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body


class PyngrokNgrokURLError(PyngrokNgrokError):
    """
    Raised when an error occurs when trying to initiate an API request.

    :var reason: The reason for the URL error.
    :vartype reason: str
    """
    reason: str

    def __init__(self,
                 error: str,
                 reason: str) -> None:
        super(PyngrokNgrokURLError, self).__init__(error)

        self.reason = reason

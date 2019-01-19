__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.3.0"


class PyngrokError(Exception):
    pass


class PyngrokNgrokInstallError(PyngrokError):
    pass


class PyngrokNgrokError(PyngrokError):
    pass


class PyngrokNgrokHTTPError(PyngrokNgrokError):
    def __init__(self, error, url, status_code, message, headers, body):
        super(PyngrokNgrokError, self).__init__(error)

        self.url = url
        self.status_code = status_code
        self.message = message
        self.headers = headers
        self.body = body

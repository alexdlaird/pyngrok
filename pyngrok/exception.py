__author__ = "Alex Laird"
__copyright__ = "Copyright 2018, Alex Laird"
__version__ = "1.1.0"


class PyngrokError(Exception):
    pass


class PyngrokNgrokInstallError(PyngrokError):
    pass


class PyngrokNgrokError(PyngrokError):
    pass

class PyngrokNgrokHTTPError(PyngrokNgrokError):
    pass
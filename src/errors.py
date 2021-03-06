import web
import json

NOTFOUND     = 10
NOTALLOWED   = 20
BADPARAMS    = 30
NORESULT     = 50
FATAL        = 80
UNAUTHORIZED = 90
FORBIDDEN    = 100
BADAUTH      = 110
DEFAULT      = NOTFOUND

_level_messages = {
    NOTFOUND:     'Not Found.',
    NOTALLOWED:   'Not Allowed.',
    BADPARAMS:    'Invalid parameters provided.',
    NORESULT:     'No records have matched your search criteria.',
    FATAL:        'Something terrible has happened.',
    UNAUTHORIZED: 'Authentication is needed.',
    FORBIDDEN:    'You do not have permissions to access this resource.',
    BADAUTH:      'Wrong credentials provided.'
}

_level_statuses = {
    NOTFOUND:     '404 Not Found',
    NOTALLOWED:   '405 Method Not Allowed',
    BADPARAMS:    '400 Bad Request',
    NORESULT:     '404 Not Found',
    FATAL:        '500 Internal Server Error',
    UNAUTHORIZED: '401 Unauthorized',
    FORBIDDEN:    '403 Forbidden',
    BADAUTH:      '401 Unauthorized'
}

_level_codes = {
    NOTFOUND:     404,
    NOTALLOWED:   405,
    BADPARAMS:    400,
    NORESULT:     404,
    FATAL:        500,
    UNAUTHORIZED: 401,
    FORBIDDEN:    403,
    BADAUTH:      401
}


class Error(web.HTTPError):
    """Exception handler in the form of http errors"""

    def __init__(self, level=DEFAULT, msg='', data=[]):
        httpstatus = self.get_status(level)
        httpcode   = self.get_code(level)
        headers    = {'Content-Type': 'application/json'}
        message    = self.get_message(level)
        params     = web.input() if web.input() else web.data().decode('utf-8')
        output     = json.dumps(
            self.make_output(httpcode, message, msg, params, data))

        web.HTTPError.__init__(self, httpstatus, headers, output)

    def get_status(self, level):
        return _level_statuses.get(level)

    def get_code(self, level):
        return _level_codes.get(level)

    def get_message(self, level):
        return _level_messages.get(level)

    def make_output(self, httpcode, status_msg, description, parameters, data):
        return {
            'status': 'error',
            'code': httpcode,
            'message': status_msg,
            'description': description,
            'parameters': parameters,
            'count': len(data),
            'data': data
        }


def not_found():
    raise Error(NOTFOUND)


def internal_error():
    raise Error(FATAL)

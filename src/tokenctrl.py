import web
from aux import logger_instance, debug_mode, is_valid_email
from api import json, json_response, api_response
from errors import Error, BADPARAMS, NOTALLOWED, BADAUTH
from models import Account, Token

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class TokenController(object):
    """Handle authentication tokens"""

    @json_response
    @api_response
    def GET(self, name):
        """Check a token"""
        logger.debug("Query: %s" % (web.input()))

        intoken = web.input().get('token')
        token = Token(intoken)
        token.validate()

        try:
            user = Account.get_from_id(token.sub).first()
            logger.debug(user)
            account = Account(user['email'], user['password'],
                              user['account_id'], user['name'],
                              user['surname'], user['authority'])
        except Exception as e:
            logger.debug(e)
            raise Error(BADAUTH)

        result = account.__dict__
        result['token'] = token.token
        del result['password']
        return [result]

    @json_response
    @api_response
    def POST(self, name):
        """Login - obtain a token"""
        logger.debug(web.data())

        try:
            data = json.loads(web.data().decode('utf-8'))
        except json.decoder.JSONDecodeError:
            raise Error(BADPARAMS, msg="Could not decode JSON.")
        email  = data.get('email')
        passwd = data.get('password')

        try:
            assert email and is_valid_email(email)
        except AssertionError:
            raise Error(BADPARAMS, msg="Invalid email provided.")

        try:
            assert passwd
            account = Account(email, passwd)
            assert account.is_valid()
        except AssertionError:
            raise Error(BADAUTH)

        account.reload()
        result = account.__dict__
        result['token'] = account.issue_token()
        del result['password']
        del result['hash']
        return [result]

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)

    @json_response
    def OPTIONS(self, name):
        return

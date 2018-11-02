import web
from aux import logger_instance, debug_mode, is_valid_email
from api import json, json_response, api_response, check_token
from errors import Error, BADPARAMS, NOTALLOWED, FATAL
from models import Account

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class AccountController(object):
    """Handles authentication tokens"""

    def GET(self, name):
        raise Error(NOTALLOWED)

    @json_response
    @api_response
    @check_token
    def POST(self, name):
        """Login - obtain a token"""
        logger.debug(web.data())

        data   = json.loads(web.data())
        email  = data.get('email')
        passwd = data.get('password')
        name = data.get('name')
        surname = data.get('surname')
        authority = data.get('authority')

        try:
            assert passwd and name and surname
        except AssertionError:
            raise Error(BADPARAMS)

        account = AccountController.create_acccount(email, passwd, name,
                                                    surname, authority)

        account = account.__dict__
        del account['password']
        del account['hash']
        return [account]

    @staticmethod
    def create_account(email, password, name, surname, authority='user'):
        try:
            assert email and is_valid_email(email)
        except AssertionError:
            raise Error(BADPARAMS, msg="Invalid email provided.")
        try:
            uuid = Account.generate_uuid()
            account = Account(email, password, uuid, name, surname, authority)
            account.save()
        except Exception as e:
            logger.error(e)
            raise Error(FATAL)
        return account

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)

    @json_response
    def OPTIONS(self, name):
        return

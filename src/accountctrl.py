import web
from aux import logger_instance, debug_mode, is_valid_email, is_uri
from api import json, json_response, api_response, check_token
from errors import Error, BADPARAMS, NOTALLOWED
from models import Account

logger = logger_instance(__name__)
web.config.debug = debug_mode()


class AccountController(object):
    """Handles user accounts"""

    def GET(self, name):
        raise Error(NOTALLOWED)

    @json_response
    @api_response
    @check_token
    def POST(self, name):
        """Create an account"""
        logger.debug(web.data())

        try:
            data = json.loads(web.data().decode('utf-8'))
        except json.decoder.JSONDecodeError:
            raise Error(BADPARAMS, msg="Could not decode JSON.")
        account_id = data.get('account_id')
        email = data.get('email')
        passwd = data.get('password')
        name = data.get('name')
        surname = data.get('surname')
        authority = data.get('authority')

        if not passwd or not name or not surname:
            raise Error(BADPARAMS)

        account = AccountController.create_acccount(email, passwd, account_id,
                                                    name, surname, authority)

        account = account.__dict__
        del account['password']
        del account['hash']
        return [account]

    @staticmethod
    def create_account(email, password, account_id, name,
                       surname, authority='user'):
        if not email or not is_valid_email(email):
            raise Error(BADPARAMS, msg="Invalid email provided.")
        if not account_id or not is_uri(account_id):
            raise Error(BADPARAMS,
                        msg="Invalid account_id provided. Not a URI")

        acct = Account(email, password, account_id, name, surname, authority)
        acct.save()
        return acct

    def PUT(self, name):
        raise Error(NOTALLOWED)

    def DELETE(self, name):
        raise Error(NOTALLOWED)

    @json_response
    def OPTIONS(self, name):
        return

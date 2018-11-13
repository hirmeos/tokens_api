import jwt
import uuid
import datetime
import psycopg2
from aux import logger_instance
from api import db, TOKEN_LIFETIME, SECRET_KEY, PBKDF2_ITERATIONS
from errors import Error, FATAL, FORBIDDEN, UNAUTHORIZED
from pbkdf2 import crypt

logger = logger_instance(__name__)


class Account(object):
    """API authentication accounts"""
    def __init__(self, email, password, uuid='', name='', surname='',
                 authority='user'):
        self.email     = email
        self.password  = password
        self.id        = uuid
        self.name      = name
        self.surname   = surname
        self.authority = authority

    def save(self):
        try:
            assert self.hash
        except AttributeError:
            self.hash_password()

        try:
            db.insert('account', account_id=self.id, email=self.email,
                      password=self.hash, authority=self.authority,
                      name=self.name, surname=self.surname)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)

    def get_full_name(self):
        return " ".join([self.name, self.surname])

    def hash_password(self):
        self.hash = crypt(self.password, iterations=PBKDF2_ITERATIONS)

    def issue_token(self):
        try:
            token = Token(sub=self.id, name=self.get_full_name(),
                          email=self.email, authority=self.authority)
            self.token = token.encoded().decode()
            return self.token
        except Exception as e:
            logger.error(e)
            raise Error(FATAL)

    def is_valid(self):
        result = Account.get_from_email(self.email)
        if not result:
            return False
        res = result.first()
        self.hash = res["password"]
        self.authority = res["authority"]
        self.name = res["name"]
        self.surname = res["surname"]
        return self.is_password_correct()

    def is_password_correct(self):
        return self.hash == crypt(self.password, self.hash)

    def reload(self):
        atts = Account.get_from_email(self.email).first()
        self.id = atts['account_id']
        self.name = atts['name']
        self.surname = atts['surname']
        self.authority = atts['authority']

    @staticmethod
    def generate_uuid():
        return str(uuid.uuid4())

    @staticmethod
    def is_uuid(input_uuid):
        try:
            uuid.UUID(input_uuid)
            return True
        except ValueError:
            return False

    @staticmethod
    def get_from_email(email):
        options = dict(email=email)
        return db.select('account', options, where="email = $email")

    @staticmethod
    def get_from_id(uuid):
        params = {'uuid': uuid}
        q = '''SELECT * FROM account WHERE account_id = $uuid;'''
        try:
            return db.query(q, params)
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            raise Error(FATAL)


class Token(object):
    """API tokens"""
    def __init__(self, token=None, sub=None, exp=None, iat=None,
                 name=None, email=None, authority=None):
        self.token = token
        self.sub = sub
        self.iat = iat if exp else datetime.datetime.utcnow()
        self.exp = exp if exp else self.iat + datetime.timedelta(
            seconds=TOKEN_LIFETIME)
        self.name = name
        self.email = email
        self.authority = authority
        self.load_payload()

    def load_payload(self):
        self.payload = {'exp': self.exp, 'iat': self.iat, 'sub': self.sub,
                        'name': self.name, 'email': self.email,
                        'authority': self.authority}

    def update_from_payload(self, payload):
        self.sub = payload['sub']
        self.iat = payload['iat']
        self.exp = payload['exp']
        self.name = payload['name']
        self.email = payload['email']
        self.authority = payload['authority']
        self.load_payload()

    def encoded(self):
        return self.token if self.token else jwt.encode(self.payload,
                                                        SECRET_KEY,
                                                        algorithm='HS256')

    def validate(self):
        try:
            payload = jwt.decode(self.token, SECRET_KEY)
            self.update_from_payload(payload)
            assert Account.is_uuid(self.sub)
        except jwt.exceptions.DecodeError:
            raise Error(FORBIDDEN)
        except jwt.ExpiredSignatureError:
            raise Error(UNAUTHORIZED, msg="Signature expired.")
        except (AssertionError, jwt.InvalidTokenError):
            raise Error(UNAUTHORIZED, msg="Invalid token.")

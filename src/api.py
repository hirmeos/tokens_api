#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
JWT issuing API for authentication in multiple services.
Simple web.py based API to a PostgreSQL database that runs on port 8080.

usage: python api.py

(c) Javier Arias, Open Book Publishers, August 2018
Use of this software is governed by the terms of the MIT license

Dependencies:
  pbkdf2==1.3
  PyJWT==1.6.1
  psycopg2-binary==2.7.5
  web.py==0.39
"""

import os
import web
import json
from aux import logger_instance, debug_mode
from errors import Error, internal_error, not_found, FATAL, NORESULT

# get logging interface
logger = logger_instance(__name__)
web.config.debug = debug_mode()
# Get entication configuration
SECRET_KEY = os.environ['SECRET_KEY']
TOKEN_LIFETIME = int(os.environ['TOKEN_LIFETIME'])
PBKDF2_ITERATIONS = int(os.environ['PBKDF2_ITERATIONS'])

# Define routes
urls = (
    "/tokens(/?)", "tokenctrl.TokenController",
    "/accounts(/?)", "accountctrl.AccountController"
)

try:
    db = web.database(dbn='postgres',
                      host=os.environ['DB_HOST'],
                      user=os.environ['DB_USER'],
                      pw=os.environ['DB_PASS'],
                      db=os.environ['DB_DB'])
except Exception as error:
    logger.error(error)
    raise Error(FATAL)


def api_response(fn):
    """Decorator to provide consistency in all responses"""
    def response(self, *args, **kw):
        data  = fn(self, *args, **kw)
        count = len(data)
        if count > 0:
            return {'status': 'ok', 'code': 200, 'count': count, 'data': data}
        else:
            raise Error(NORESULT)
    return response


def json_response(fn):
    """JSON decorator"""
    def response(self, *args, **kw):
        web.header('Content-Type', 'application/json;charset=UTF-8')
        web.header('Access-Control-Allow-Origin',
                   '"'.join([os.environ['ALLOW_ORIGIN']]))
        web.header('Access-Control-Allow-Credentials', 'true')
        web.header('Access-Control-Allow-Headers',
                   'Authorization, x-test-header, Origin, '
                   'X-Requested-With, Content-Type, Accept')
        return json.dumps(fn(self, *args, **kw), ensure_ascii=False)
    return response


def check_token(fn):
    """Decorator to act as middleware, checking authentication token"""
    def response(self, *args, **kw):
        intoken = get_token_from_header()
        token = Token(intoken)
        token.validate()
        return fn(self, *args, **kw)
    return response


def get_token_from_header():
    bearer = web.ctx.env.get('HTTP_AUTHORIZATION')
    return bearer.replace("Bearer ", "") if bearer else ""


import tokenctrl  # noqa: F401
import accountctrl  # noqa: F401
from models import Token  # noqa: F401

if __name__ == "__main__":
    logger.info("Starting API...")
    app = web.application(urls, globals())
    app.internalerror = internal_error
    app.notfound = not_found
    app.run()

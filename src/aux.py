#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import os
import logging
from urllib.parse import urlparse


def debug_mode():
    trues = ('True', 'true', True, 1)
    return 'API_DEBUG' in os.environ and os.environ['API_DEBUG'] in trues


def logger_instance(name):
    level = logging.NOTSET if debug_mode() else logging.ERROR
    logging.basicConfig(level=level)
    return logging.getLogger(name)


def is_valid_email(email):
    check_email = re.compile(r"[^@]+@[^@]+\.[^@]+")
    return check_email.match(email) is not None


def is_uri(input_uri):
    return isinstance(input_uri, str) and bool(urlparse(input_uri).scheme)

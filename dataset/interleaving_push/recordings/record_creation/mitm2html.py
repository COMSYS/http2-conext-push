"""
This inline script can be used to dump url response bodies to stdout.
"""

import json
import sys
import base64
import zlib
import sys
import os
import string
import random

from datetime import datetime
import pytz

import mitmproxy

from mitmproxy import version
from mitmproxy.utils import strutils
from mitmproxy.net.http import status_codes


PARAMS={}

def start():
    """
        Called once on script startup before any other events.
    """
    if len(sys.argv) != 2:
        raise ValueError(
            'Usage: -s "mitm2html.py url" '
        )

    PARAMS.update({"URL_TO_DUMP":sys.argv[1]})


def response(flow):
    """
       Called when a server response has been received.
    """
    if flow.request.url == PARAMS['URL_TO_DUMP']:
        if flow.response.get_content() is not None:
            print(flow.response.get_content().decode())


def done():
    """
        Called once on script shutdown, after any other events.
    """
    #mitmproxy.ctx.log("Dump finished ")
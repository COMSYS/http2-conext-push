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
import pprint

import mitmproxy

from mitmproxy import version
from mitmproxy.utils import strutils
from mitmproxy.net.http import status_codes


def start():
    """
        Called once on script startup before any other events.
    """
    if len(sys.argv) != 1:
        raise ValueError(
            'Usage: -s "mitm2mergedcss.py" '
        )


def response(flow):
    """
       Called when a server response has been received.
    """
    
    content_type = flow.response.headers.get("content-type", "").lower();

    if 'css' in content_type:
        if flow.response.get_content() is not None:
            print(flow.response.get_content().decode())


def done():
    """
        Called once on script shutdown, after any other events.
    """
    #mitmproxy.ctx.log("Dump finished ")
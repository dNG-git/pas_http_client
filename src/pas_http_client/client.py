# -*- coding: utf-8 -*-

"""
direct PAS
Python Application Services
----------------------------------------------------------------------------
(C) direct Netware Group - All rights reserved
https://www.direct-netware.de/redirect?pas;http;client

This Source Code Form is subject to the terms of the Mozilla Public License,
v. 2.0. If a copy of the MPL was not distributed with this file, You can
obtain one at http://mozilla.org/MPL/2.0/.
----------------------------------------------------------------------------
https://www.direct-netware.de/redirect?licenses;mpl2
----------------------------------------------------------------------------
#echo(pasHttpClientVersion)#
#echo(__FILEPATH__)#
"""

from .raw_client import RawClient
from .response import Response

class Client(RawClient):
    """
HTTP client for requesting and parsing data.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: client
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    # pylint: disable=arguments-differ

    __slots__ = [ ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self, url, timeout = 6, event_handler = None):
        """
Constructor __init__(Client)

:param url: URL to be called
:param timeout: Connection timeout in seconds
:param return_reader: Returns a body reader instead of reading the response
                      if true.
:param event_handler: EventHandler to use

:since: v1.0.0
        """

        RawClient.__init__(self, url, timeout, True, event_handler)
    #

    def _new_response(self, raw_response):
        """
Initializes an HTTP response object based on the received raw data.

:param raw_response: Raw response dict

:return: (object) Response object
:since:  v1.0.0
        """

        # pylint: disable=protected-access

        _return = Response()
        _return._set_code(raw_response['code'])
        _return._set_headers(raw_response['headers'])

        if (isinstance(raw_response['body'], Exception)): _return._set_exception(raw_response['body'])
        if ("body_reader" in raw_response): _return._set_body_reader(raw_response['body_reader'])

        return _return
    #

    def request(self, method, separator = ";", params = None, data = None):
        """
Call a given request method on the connected HTTP server.

:param method: HTTP method
:param separator: Query parameter separator
:param params: Parsed query parameters as str
:param data: HTTP body

:return: (object) Response object
:since:  v1.0.0
        """

        raw_response = RawClient.request(self, method, separator, params, data)
        return self._new_response(raw_response)
    #
#

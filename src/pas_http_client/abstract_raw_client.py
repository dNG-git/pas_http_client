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

# pylint: disable=import-error,invalid-name,no-name-in-module

from base64 import b64encode
from weakref import proxy, ProxyTypes

try: from urllib.parse import quote_plus, urlencode, urlsplit
except ImportError:
    from urllib import quote_plus, urlencode
    from urlparse import urlsplit
#

from dpt_runtime.binary import Binary
from dpt_runtime.not_implemented_exception import NotImplementedException
from dpt_runtime.type_exception import TypeException
from pas_rfc_basics.header import Header

class AbstractRawClient(object):
    """
Abstract HTTP-like client abstraction layer returning raw responses.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: client
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    BINARY_NEWLINE = Binary.bytes("\r\n")
    """
Newline bytes used in raw HTTP data
    """

    def __init__(self, url, timeout = 30, return_reader = False, log_handler = None):
        """
Constructor __init__(AbstractRawClient)

:param url: URL to be called
:param timeout: Socket timeout in seconds
:param return_reader: Returns a body reader instead of reading the response
                      if true.
:param log_handler: Log handler to use

:since: v1.0.0
        """

        self.auth_username = None
        """
Request authorisation username
        """
        self.auth_password = None
        """
Request authorisation password
        """
        self.connection = None
        """
HTTP connection
        """
        self.headers = None
        """
Request headers
        """
        self.host = None
        """
Request host
        """
        self.ipv6_link_local_interface = None
        """
IPv6 link local interface to be used for outgoing requests
        """
        self._log_handler = None
        """
The log handler is called whenever debug messages should be logged or errors
happened.
        """
        self.path = None
        """
Request path
        """
        self.port = None
        """
Request port
        """
        self.return_reader = return_reader
        """
True if the client returns a callable reader supporting a size argument.
        """
        self.scheme = None
        """
Request scheme
        """
        self.timeout = timeout
        """
Socket timeout in seconds
        """

        if (log_handler is not None): self.log_handler = log_handler
        self.url = url
    #

    @property
    def log_handler(self):
        """
Returns the LogHandler.

:return: (object) LogHandler in use
:since:  v1.0.0
        """

        return self._log_handler
    #

    @log_handler.setter
    def log_handler(self, log_handler):
        """
Sets the LogHandler.

:param log_handler: LogHandler to use

:since: v1.0.0
        """

        self._log_handler = (log_handler if (isinstance(log_handler, ProxyTypes)) else proxy(log_handler))
    #

    @property
    def url(self):
        """
Returns the URL used for all subsequent requests.

:return: (str) URL to be called
:since:  v1.0.0
        """

        _return = "{0}://".format(self.scheme)

        if (self.auth_username is not None or self.auth_password is not None):
            if (self.auth_username is not None): _return += quote_plus(self.auth_username, "")
            _return += ":"
            if (self.auth_password is not None): _return += quote_plus(self.auth_password, "")
            _return += "@"
        #

        _return += "{0}:{0:1}{2}".format(self.host, self.port, self.path)

        return _return
    #

    @url.setter
    def url(self, url):
        """
Sets a new URL for all subsequent requests.

:param url: URL to be called

:since: v1.0.0
        """

        url = Binary.str(url)
        if (type(url) is not str): raise TypeException("URL given is invalid")

        self._configure(url)
    #

    def _build_request_parameters(self, params = None, separator = ";"):
        """
Build a HTTP query string based on the given parameters and the separator.

:param params: Query parameters as dict
:param separator: Query parameter separator

:return: (mixed) Response data; Exception on error
:since:  v1.0.0
        """

        _return = None

        if (isinstance(params, dict)):
            params_list = [ ]

            for key in params:
                if (type(params[key]) is not bool): params_list.append("{0}={1}".format(quote_plus(str(key), ""), quote_plus(str(params[key]), "")))
                elif (params[key]): params_list.append("{0}=1".format(quote_plus(str(key), "")))
                else: params_list.append("{0}=0".format(quote_plus(str(key), "")))
            #

            _return = separator.join(params_list)
        #

        return _return
    #

    def _configure(self, url):
        """
Configures the HTTP connection for later use.

:param url: URL to be called

:since: v1.0.0
        """

        raise NotImplementedException()
    #

    def request(self, method, separator = ";", params = None, data = None):
        """
Call a given request method on the connected HTTP server.

:param method: HTTP method
:param separator: Query parameter separator
:param params: Parsed query parameters as str
:param data: HTTP body

:return: (dict) Response data; 'body' may contain the catched exception
:since:  v1.0.0
        """

        # pylint: disable=broad-except,star-args

        if (self._log_handler is not None): self._log_handler.debug("#echo(__FILEPATH__)# -{0!r}.request({1})- (#echo(__LINE__)#)".format(self, method))

        try:
            path = self.path

            if (type(params) is str):
                if ("?" not in path): path += "?"
                elif (not path.endswith(separator)): path += separator

                path += params
            #

            headers = (None if (self.headers is None) else self.headers.copy())
            kwargs = { "url": path }

            if (data is not None):
                if (isinstance(data, dict)):
                    if (headers is None): headers = { }
                    if ("content-type" not in headers): headers['content-type'] = "application/x-www-form-urlencoded"

                    data = urlencode(data)
                #

                kwargs['body'] = Binary.utf8_bytes(data)
            #

            if (self.auth_username is not None):
                auth_data = "{0}:{1}".format(self.auth_username, self.auth_password)

                if (type(auth_data) is not Binary.BYTES_TYPE): auth_data = Binary.utf8_bytes(auth_data)
                base64_data = b64encode(auth_data)
                if (type(base64_data) is not str): base64_data = Binary.str(base64_data)

                kwargs['headers'] = { "Authorization": "Basic {0}".format(base64_data) }
                if (headers is not None): kwargs['headers'].update(headers)
            elif (headers is not None): kwargs['headers'] = headers

            _return = self._request(method, **kwargs)
        except Exception as handled_exception: _return = { "code": None, "headers": None, "body": handled_exception }

        return _return
    #

    def _request(self, method, **kwargs):
        """
Sends the request to the connected HTTP server and returns the result.

:param method: HTTP method

:return: (dict) Response data; 'body' may contain the catched Exception
:since:  v1.0.0
        """

        raise NotImplementedException()
    #

    def reset_headers(self):
        """
Resets previously set headers.

:since: v1.0.0
        """

        self.headers = { }
    #

    def set_basic_auth(self, username, password):
        """
Sets the basic authentication data.

:param username: Username
:param password: Password

:since: v1.0.0
        """

        self.auth_username = ("" if (username is None) else username)
        self.auth_password = ("" if (password is None) else password)
    #

    def set_header(self, name, value, value_appends = False):
        """
Sets a header.

:param name: Header name
:param value: Header value as string or array
:param value_appends: True if headers should be appended

:since: v1.0.0
        """

        if (self.headers is None): self.headers = { }
        name = name.lower()

        if (value is None):
            if (name in self.headers): del(self.headers[name])
        elif (name not in self.headers): self.headers[name] = value
        elif (value_appends):
            if (type(self.headers[name]) is list): self.headers[name].append(value)
            else: self.headers[name] = [ self.headers[name], value ]
        #
    #

    def set_ipv6_link_local_interface(self, interface):
        """
Forces the given interface to be used for outgoing IPv6 link local
addresses.

:param interface: Header name

:since: v1.0.0
        """

        self.ipv6_link_local_interface = interface
    #

    @staticmethod
    def get_headers(data):
        """
Returns a RFC 7231 compliant dict of headers from the entire HTTP response.

:param data: Input message

:return: (str) Dict with parsed headers; None on error
:since:  v1.0.0
        """

        if (type(data) is not str): data = Binary.str(data)
        header = data.split("\r\n\r\n", 1)[0]
        _return = Header.get_headers(header)

        if (_return is not None and "@nameless" in _return and "\n" not in _return['@nameless']):
            _return['@http'] = _return['@nameless']
            del(_return['@nameless'])
        #

        return _return
    #
#

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

class Response(object):
    """
HTTP response object handling chunked transfer-encoded data transparently.

:author:     direct Netware Group
:copyright:  (C) direct Netware Group - All rights reserved
:package:    pas.http
:subpackage: client
:since:      v1.0.0
:license:    https://www.direct-netware.de/redirect?licenses;mpl2
             Mozilla Public License, v. 2.0
    """

    __slots__ = [ "body_reader", "_code", "_exception", "_headers" ]
    """
python.org: __slots__ reserves space for the declared variables and prevents
the automatic creation of __dict__ and __weakref__ for each instance.
    """

    def __init__(self):
        """
Constructor __init__(Response)

:since: v1.0.0
        """

        self._body_reader = None
        """
Body reader callable
        """
        self._code = None
        """
HTTP status code
        """
        self._exception = None
        """
Exception occurred while receiving an response.
        """
        self._headers = { }
        """
Response headers
        """
    #

    @property
    def code(self):
        """
Returns the HTTP status code for the request.

:return: (int) HTTP status code; None otherwise
:since:  v1.0.0
        """

        return self._code
    #

    @property
    def error_message(self):
        """
Returns the error message based on the exception that occurred while
processing the request.

:return: (str) Error message; None otherwise
:since:  v1.0.0
        """

        exception = self.exception
        return (None if (exception is None) else str(exception))
    #

    @property
    def exception(self):
        """
Returns the exception that occurred while processing the request.

:return: (object) Exception instance; None otherwise
:since:  v1.0.0
        """

        return self._exception
    #

    @property
    def headers(self):
        """
Returns the response headers.

:return: (dict) Dictionary of headers
:since:  v1.0.0
        """

        return self._headers.copy()
    #

    @property
    def is_readable(self):
        """
Returns true if the body reader is ready to receive the response and no
exception occurred while processing the request.

:return: (bool) True if ready
:since:  v1.0.0
        """

        return (self._body_reader is not None and self.exception is None)
    #

    def get_header(self, name):
        """
Returns the response header if defined.

:param name: Header name

:return: (str) Header value if set; None otherwise
:since:  v1.0.0
        """

        name = name.lower().replace("-", "_")
        return self._headers.get(name)
    #

    def read(self, n = 0):
        """
Reads data using the given body reader. Chunked transfer-encoded data is
handled automatically.

:param n: How many bytes to read from the current position (0 means until
          EOF)

:return: (bytes) Data; None if EOF
:since:  v1.0.0
        """

        return (self._body_reader() if (n < 1) else self._body_reader(n))
    #

    def _set_body_reader(self, body_reader):
        """
Sets the body reader callable of this response object.

:param body_reader: Body reader callable

:since: v1.0.0
        """

        self._body_reader = body_reader
    #

    def _set_code(self, code):
        """
Sets the HTTP status code for the request.

:param code: HTTP status code; None otherwise

:since: v1.0.0
        """

        self._code = code
    #

    def _set_exception(self, exception):
        """
Sets the exception occurred while processing the request.

:param exception: Exception object

:since: v1.0.0
        """

        self._exception = exception
    #

    def _set_headers(self, headers):
        """
Sets the headers of the response.

:param headers: HTTP response headers

:since: v1.0.0
        """

        if (headers is not None): self._headers = headers
    #
#

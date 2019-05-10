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

# pylint: disable=invalid-name

from time import time

from dpt_runtime.binary import Binary
from dpt_runtime.io_exception import IOException

class ChunkedReaderMixin(object):
    """
HTTP reader handling chunked transfer-encoded data.

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

    def __init__(self):
        """
Constructor __init__(ChunkedReaderMixin)

:since: v1.0.0
        """

        self._chunked_reader_buffer = None
        """
Bytes buffer
        """
    #

    def _read_chunked_data(self, reader, callback, size = -1, timeout = None):
        """
Reads chunked data from the given reader to the given callback.

:param reader: Read callback
:param callback: Callback for data read
:param size: Byte size to read
:param timeout: Timeout in seconds

:since: v1.0.0
        """

        is_last_chunk = False
        size_read = 0
        size_unread = 5
        timeout_time = (-1 if (timeout is None) else time() + timeout)

        chunk_buffer = self._chunked_reader_buffer
        chunk_size = len(chunk_buffer)

        self._chunked_reader_buffer = None

        while (size_unread > 0
               and (size_read < size or chunk_size > 0)
               and (timeout_time < 0 or time() < timeout_time)
              ):
            """
Read remaining data from last chunk
            """

            part_size = (16384 if (size_unread > 16384) else size_unread)
            part_data = reader(part_size)
            part_size = len(part_data)

            if (part_size < 1): raise IOException("Reader pointer could not be read before timeout occurred")
            size_unread -= part_size

            """
Get size for next chunk
            """

            if (chunk_size < 1):
                newline_position = (part_data
                                    if (chunk_buffer is None) else
                                    chunk_buffer + part_data
                                   ).find(ChunkedReaderMixin.BINARY_NEWLINE)

                chunk_octets = None

                if (newline_position < 0):
                    if (chunk_buffer is None): chunk_buffer = part_data
                    else: chunk_buffer += part_data

                    part_size = 0
                    size_unread += 3
                elif (chunk_buffer is not None):
                    chunk_octets = (chunk_buffer + part_data)[:newline_position]
                    part_data = (chunk_buffer + part_data)[2 + newline_position:]
                    part_size = len(part_data)

                    chunk_buffer = None
                elif (not is_last_chunk):
                    chunk_octets = part_data[:newline_position]
                    part_data = part_data[2 + newline_position:]

                    part_size = len(part_data)
                else: part_size = 0

                if (chunk_octets is not None):
                    chunk_size = int(chunk_octets, 16)

                    if (chunk_size == 0): is_last_chunk = True
                    else: size_unread += chunk_size
                #
            #

            if (part_size > 0):
                chunk_size -= part_size

                if (size_read > size):
                    if (self._chunked_reader_buffer is None): self._chunked_reader_buffer = part_data
                    else: self._chunked_reader_buffer += part_data
                elif ((size_read + part_size) > size):
                    size_expected = size - (size_read + part_size)

                    self._chunked_reader_buffer = part_data[size_expected:]
                    callback(part_data[:size_expected])
                else: callback(part_data)

                size_read += part_size
            #
        #

        if (size_unread > 0): raise IOException("Timeout occurred before EOF")
    #

    def _reset_chunked_buffer(self):
        """
Resets the buffer of chunked data remaining after the last read call.

:since: v1.0.0
        """

        self._chunked_reader_buffer = None
    #
#

# coding=utf-8
# Copyright 2016 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import datetime
import sys

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

if PY3:
    integer_types = int,
    long_type = int
    basestring_types = (str, bytes)
    text_types = str,
    unicode_type = str
    bytes_type = bytes
else:
    integer_types = (int, long)
    long_type = long
    basestring_types = basestring,
    text_types = basestring,
    unicode_type = unicode
    bytes_type = str

MAX_SAFE_INTEGER = 9007199254740991

safeint_type = type(MAX_SAFE_INTEGER)

if PY2:
    from compat2 import throw_exc_info

    throw_exc_info = throw_exc_info
else:
    def throw_exc_info(exc_info):
        e = exc_info[0](exc_info[1])
        e.__traceback__ = exc_info[2]
        raise e


def make_key(key):
    if isinstance(key, str):
        return key
    try:
        if PY2:
            return key.encode('utf-8')
        else:
            return key.decode('utf-8')
    except:
        raise TypeError()


try:
    from email.utils import parsedate_to_datetime
except ImportError:
    import email.utils


    def parsedate_to_datetime(date):
        t = email.utils.parsedate_tz(date)
        if t is None:
            raise ValueError()
        dt = datetime.datetime(*t[:7])
        if t[-1] is not None:
            dt = dt.replace(tzinfo=timezone(datetime.timedelta(seconds=t[-1])))
        return dt

try:
    from datetime import timezone
except ImportError:

    class timezone(datetime.tzinfo):

        def __init__(self, offset):
            super(timezone, self).__init__()
            self.offset = offset

        def utcoffset(self, date_time):
            return self.offset

        def dst(self, date_time):
            return None

        def tzname(self, dt):
            offset = int(self.offset.total_seconds() // datetime.timedelta(minutes=1).total_seconds())
            if offset == 0:
                return 'UTC'
            elif offset % 60 == 0:
                return 'GMT%+d' % (offset // 60)
            elif offset > 0:
                return 'UTC+%02d:%02d' % divmod(offset, 60)
            else:
                return 'UTC-%02d:%02d' % divmod(-offset, 60)


    timezone.utc = timezone(datetime.timedelta(0))

try:
    import ipaddress
except ImportError:

    class _ipaddress(object):
        def __getattr__(self, item):
            raise ImportError('No module named ipaddress')


    ipaddress = _ipaddress()

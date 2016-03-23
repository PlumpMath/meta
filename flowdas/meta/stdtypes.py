# coding=utf-8
# Copyright 2016 Flowdas Inc. <prospero@flowdas.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
import calendar
import cmath
import datetime
import decimal
import math
import time
import uuid

import re
from .compat import *
from .property import Property, Marker, Null


class Primitive(Property):
    """
    JSON serializable 을 표현하는 :py:class:`Property`.

    모든 JSON serializable 값들을 받아들인다.

    이 값들은 다음 :py:class:`Property` 이 다루는 값들의 합집합이다.

    - :py:class:`String`
        - :py:class:`Unicode`
        - :py:class:`Bytes`
    - :py:class:`Boolean`
    - :py:class:`Number`
        - :py:class:`Integer`
        - :py:class:`Float`
    - :py:class:`JsonObject`
    - :py:class:`JsonArray`

    :py:class:`Property` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/primitive.py

    Since version 1.0.
    """

    def _dump_(self, value, context):
        return value

    def _load_(self, value, context):
        self._check_json(value, context)
        return value

    def _check_json(self, value, context):
        if value is None or isinstance(value, (basestring_types, integer_types, float)):
            return
        elif isinstance(value, dict):
            self._check_object(value, context)
        elif isinstance(value, (tuple, list)):
            self._check_array(value, context)
        else:
            raise ValueError()

    def _check_object(self, value, context):
        with Marker(context, value) as marker:
            for key, val in value.items():
                skip = False
                with marker.cursor(key, Null):
                    if not isinstance(key, basestring_types):
                        skip = True
                        raise ValueError()
                if skip:
                    continue
                with marker.cursor(key, val):
                    if not marker.isvisited(val):
                        self._check_json(val, marker.context)

    def _check_array(self, value, context):
        with Marker(context, value) as marker:
            for i, val in enumerate(value):
                with marker.cursor(i, val):
                    if not marker.isvisited(val):
                        self._check_json(val, marker.context)


class String(Primitive):
    """
    문자열을 표현하는 :py:class:`Property`.

    모든 문자열을 변환 없이 받아들인다.

    :py:class:`Primitive` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    allow_empty
        False 면 길이가 0 인 문자열이 올 때 :py:exc:`ValueError` 예외를 발생시킨다.

        기본값은 True.

    Example

        .. literalinclude:: /../tests/ex/string.py

    Since version 1.0.
    """

    class Options(Primitive.Options):
        allow_empty = True

    def _load_(self, value, context):
        if not isinstance(value, basestring_types):
            raise ValueError()
        if not value and not self.get_options().allow_empty:
            raise ValueError()
        return value


class Unicode(String):
    """
    텍스트 문자열을 표현하는 :py:class:`Property`.

    텍스트 문자열은 ``type(u'')`` 형을 뜻한다.

    모든 문자열을 받아들이고, 바이너리 문자열은 텍스트 문자열로 변환한다.

    :py:class:`String` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    default_encoding
        바이너리 문자열을 텍스트 문자열로 변환할 때 사용할 인코딩.

        기본값은 'utf-8'.

    Example

        .. literalinclude:: /../tests/ex/unicode.py

    Since version 1.0.
    """

    class Options(String.Options):
        default_encoding = 'utf-8'

    def _load_(self, value, context):
        if isinstance(value, bytes_type):
            value = value.decode(self.get_options().get('default_encoding', 'utf-8'))
        elif not isinstance(value, unicode_type):
            raise ValueError()
        if not value and not self.get_options().allow_empty:
            raise ValueError()
        return value


class Bytes(String):
    """
    바이너리 문자열을 표현하는 :py:class:`Property`.

    바이너리 문자열은 ``type(b'')`` 형을 뜻한다.

    모든 문자열을 받아들이고, 텍스트 문자열은 바이너리 문자열로 변환한다.

    :py:class:`String` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    default_encoding
        텍스트 문자열을 바이너리 문자열로 변환할 때 사용할 인코딩.

        기본값은 'utf-8'.

    Example

        .. literalinclude:: /../tests/ex/bytes.py

    Since version 1.0.
    """

    class Options(String.Options):
        default_encoding = 'utf-8'

    def _load_(self, value, context):
        if isinstance(value, unicode_type):
            value = value.encode(self.get_options().get('default_encoding', 'utf-8'))
        elif not isinstance(value, bytes_type):
            raise ValueError()
        if not value and not self.get_options().allow_empty:
            raise ValueError()
        return value


class Boolean(Primitive):
    """
    :py:class:`bool` 값을 표현하는 :py:class:`Property`.

    True 와 False 값 만을 받아들인다.

    :py:class:`Primitive` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/boolean.py

    Since version 1.0.
    """

    def _load_(self, value, context):
        if not isinstance(value, bool):
            raise ValueError()
        return value


class Number(Primitive):
    """
    숫자 값을 표현하는 :py:class:`Property`.

    모든 정수형과 :py:class:`float` 를 변환 없이 받아들인다.

    :py:class:`Primitive` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    allow_bool
        True 면 :py:class:`bool` 형도 받아들여 0 또는 1로 변환한다. False 면 :py:exc:`ValueError` 예외를 발생시킨다.

        파이썬에서 :py:class:`bool` 은 :py:class:`int` 형으로 취급되지만, 다른 많은 곳에서 boolean 은 정수형과 다른 형으로 취급된다.
        파이썬의 관행을 따르면 JSON 의 ``true`` 를 1로 받아들이는 결과를 얻게 된다. 응용에 따라 원하는 바가 다를 수 있다.

        기본값은 False.
    allow_nan
        False 면 `NaN`, `Infinity`, `-Infinity` 가 올 때 :py:exc:`ValueError` 예외를 발생시킨다.

        기본값은 False.
    jssafe
        True 면 9007199254740991 보다 크거나 -9007199254740991 보다 작은 정수가 올 때 :py:exc:`ValueError` 예외를 발생시킨다.

        JSON 을 사용할 경우 Javascript 엔진과의 호환성을 고려할 필요가 있다. Javascript 는 정수형과 :py:class:`float` 를 구분하지 않는다.
        많은 Javascript 엔진에서 IEEE-754 binary64 라는 단일 형식을 사용하고 있고, 이 형식은 64-bit 정수를 온전히 표현할 수 없다.

        기본값은 False.

    Example

        .. literalinclude:: /../tests/ex/number.py

    Since version 1.0.
    """

    class Options(Primitive.Options):
        allow_bool = False  # 기본 설정은 Python 보다는 JSON 의 convention 을 따른다.
        allow_nan = False  # False 면 Nan, Infinity, -Infinity 를 받아들이지 않는다.
        jssafe = False  # True 면 [-MAX_SAFE_INTEGER, MAX_SAFE_INTEGER] 범위의 정수만 허용한다.

    def _load_(self, value, context):
        if isinstance(value, bool):
            if self.get_options().allow_bool:
                return int(value)
            else:
                raise ValueError()
        elif isinstance(value, integer_types):
            if self.get_options().jssafe and not (-MAX_SAFE_INTEGER <= value <= MAX_SAFE_INTEGER):
                raise ValueError()
            return value
        elif isinstance(value, float):
            if not self.get_options().allow_nan and (math.isnan(value) or math.isinf(value)):
                raise ValueError()
            return value
        else:
            raise ValueError()


class Integer(Number):
    """
    정수값을 표현하는 :py:class:`Property`.

    모든 정수형과 :py:class:`float` 을 받아들이고, 정수형으로 변환한다.

    :py:class:`float` 가 올 경우 손실 없이 정수형으로 변환할 수 없으면 :py:exc:`ValueError` 예외를 발생시킨다.

    :py:class:`Number` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/integer.py

    Since version 1.0.
    """

    def _load_(self, value, context):
        value = super(Integer, self)._load_(value, context)
        if isinstance(value, float):
            iv = safeint_type(value)
            if iv != value:
                raise ValueError()
            return iv
        return value


class Float(Number):
    """
    :py:class:`float` 값을 표현하는 :py:class:`Property`.

    모든 정수형과 :py:class:`float` 을 받아들이고, :py:class:`float` 로 변환한다.

    :py:class:`Number` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/float.py

    Since version 1.0.
    """

    def _dump_(self, value, context):
        return value

    def _load_(self, value, context):
        return float(super(Float, self)._load_(value, context))


class JsonObject(Primitive):
    """
    JSON Object 값을 표현하는 :py:class:`Property`.

    문자열 키와 JSON Serializable 값으로만 구성된 :py:class:`dict` 를 변환 없이 받아들인다.

    값에 순환 참조가 있어서 JSON 으로 변환할 수 없으면 :py:exc:`OverflowError` 예외를 발생시킨다.

    :py:class:`Primitive` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/jsonobject.py

    Since version 1.0.
    """

    def _load_(self, value, context):
        if not isinstance(value, dict):
            raise ValueError()
        self._check_object(value, context)
        return value


class JsonArray(Primitive):
    """
    JSON Array 값을 표현하는 :py:class:`Property`.

    JSON Serializable 로만 구성된 :py:class:`list` 나 :py:class:`tuple` 을 변환 없이 받아들인다.

    값에 순환 참조가 있어서 JSON 으로 변환할 수 없으면 :py:exc:`OverflowError` 예외를 발생시킨다.

    :py:class:`Primitive` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/jsonarray.py

    Since version 1.0.
    """

    def _load_(self, value, context):
        if not isinstance(value, (list, tuple)):
            raise ValueError()
        self._check_array(value, context)
        return value


class Decimal(Property):
    """
    :py:class:`decimal.Decimal` 을 표현하는 :py:class:`Property`.

    다음과 같은 값들을 받아들여 :py:class:`decimal.Decimal` 형으로 변환한다.

    - :py:class:`decimal.Decimal`
    - 모든 정수형
    - :py:class:`float`
    - 정수나 :py:class:`float` 로 해석될 수 있는 문자열

    :py:meth:`Entity.dump` 할 때 문자열을 출력한다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    allow_nan
        False 면 `NaN`, `Infinity`, `-Infinity` 가 올 때 :py:exc:`ValueError` 예외를 발생시킨다.

        기본값은 False.

    Example

        .. literalinclude:: /../tests/ex/decimal.rst

    Since version 1.0.
    """

    class Options(Property.Options):
        allow_nan = False

    def _dump_(self, value, context):
        return str(value)

    def _load_(self, value, context):
        if isinstance(value, decimal.Decimal):
            if not self.get_options().allow_nan and not value.is_finite():
                raise ValueError()
            return value
        elif isinstance(value, text_types):
            try:
                with decimal.localcontext() as ctx:
                    ctx.traps[decimal.InvalidOperation] = 1
                    value = decimal.Decimal(value)
                    if not self.get_options().allow_nan and not value.is_finite():
                        raise ValueError()
                    return value
            except decimal.InvalidOperation:
                raise ValueError()
        elif isinstance(value, integer_types):
            return decimal.Decimal(value)
        elif isinstance(value, float):
            if not self.get_options().allow_nan:
                if math.isnan(value) or math.isinf(value):
                    raise ValueError()
            return decimal.Decimal(value)
        else:
            raise ValueError()


class Complex(Property):
    """
    복소수를 표현하는 :py:class:`Property`.

    다음과 같은 값들을 받아들여 :py:class:`complex` 형으로 변환한다.

    - :py:class:`complex`
    - 실수 - 모든 정수형과 :py:class:`float`
    - 두개의 실수로 구성된 :py:class:`tuple` 이나 :py:class:`list`

    :py:meth:`Entity.dump` 할 때 (:py:class:`float`, :py:class:`float`) 를 출력한다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    allow_nan
        False 면 `NaN`, `Infinity`, `-Infinity` 가 올 때 :py:exc:`ValueError` 예외를 발생시킨다.

        기본값은 False.

    Example

        .. literalinclude:: /../tests/ex/complex.py

    Since version 1.0.
    """

    class Options(Property.Options):
        allow_nan = False

    def _dump_(self, value, context):
        return value.real, value.imag

    def _load_(self, value, context):
        if isinstance(value, complex):
            pass
        elif isinstance(value, (integer_types, float)):
            value = complex(value)
        elif isinstance(value, (tuple, list)):
            if len(value) != 2:
                raise ValueError()
            if not isinstance(value[0], (integer_types, float)) or not isinstance(value[1], (integer_types, float)):
                raise ValueError()
            value = complex(value[0], value[1])
        else:
            raise ValueError()
        if not self.get_options().allow_nan and (cmath.isnan(value) or cmath.isinf(value)):
            raise ValueError()
        return value


class Uuid(Property):
    """
    UUID 를 표현하는 :py:class:`Property`.

    문자열을 받아들여 :py:class:`uuid.UUID` 형으로 변환한다.

    :py:meth:`Entity.dump` 할 때 문자열을 출력한다.

    :py:class:`Property` 의 모든 옵션을 지원한다.

    Example

        .. literalinclude:: /../tests/ex/uuid.py

    Since version 1.0.
    """

    def _dump_(self, value, context):
        return str(value)

    def _load_(self, value, context):
        if isinstance(value, uuid.UUID):
            return value
        if not isinstance(value, basestring_types):
            raise ValueError()
        if PY3 and isinstance(value, bytes):
            value = value.decode('utf-8')
        return uuid.UUID(value)


class DateTimeFormat(object):
    """
    커스텀 시간 형식을 만드는데 사용된다.

    :py:meth:`DateTimeFormat.register` 데코레이터로 등록하면,
    :py:class:`DateTime`, :py:class:`Date`, :py:class:`Time` 의 ``format`` 옵션에서 사용할 수 있게 된다.

    Example:

        .. literalinclude:: /../tests/ex/datetimeformat.rst

    Since version 1.0.
    """
    _formatters_ = {}

    def __init__(self, name):
        self._name_ = name

    @classmethod
    def register(cls, name, *args, **kwargs):
        def deco(klass):
            if not issubclass(klass, DateTimeFormat):
                raise TypeError()
            cls._formatters_[name] = klass(name, *args, **kwargs)

        return deco

    @classmethod
    def get_formatter(cls, name):
        return cls._formatters_.get(name)

    @property
    def name(self):
        """
        형식의 이름.

        Since version 1.0.
        """
        return self._name_

    def format(self, value, property, context):
        """
        :py:meth:`Entity.dump` 에서 실행되는 메쏘드.

        ``value`` 로 :py:class:`datetime.datetime`, :py:class:`datetime.date`, :py:class:`datetime.time` 이 올 수 있다.

        ``property`` 는 :py:class:`DateTime`, :py:class:`Date`, :py:class:`Time` 중 하나가 오게 된다.

        ``context`` 로는 :py:class:`Context` 인스턴스나 None 이 전달된다.

        커스텀 형식은 이 메쏘드를 구현해야 한다. 기본 구현은 :py:exc:`NotImplementedError` 예외를 일으킨다.

        Since version 1.0.
        """
        raise NotImplementedError()

    def parse(self, value, property, context):
        """
        :py:meth:`Entity.load` 에서 실행되는 메쏘드.

        ``property`` 는 :py:class:`DateTime`, :py:class:`Date`, :py:class:`Time` 중 하나가 오게 된다.
        이 값을 참조해서 :py:class:`datetime.datetime`, :py:class:`datetime.date`, :py:class:`datetime.time` 중 어떤 종류를
        만들어야 하는지 결정한다.

        ``context`` 로는 :py:class:`Context` 인스턴스나 None 이 전달된다.

        커스텀 코덱은 이 메쏘드를 구현해야 한다. 기본 구현은 :py:exc:`NotImplementedError` 예외를 일으킨다.

        Since version 1.0.
        """
        raise NotImplementedError()


@DateTimeFormat.register('unix')
class UnixTimeFormat(DateTimeFormat):
    def format(self, value, property, context):
        if isinstance(value, datetime.datetime):
            if value.tzinfo:
                # DST 를 고려하지 않는다.
                value = value.replace(tzinfo=timezone.utc) - value.utcoffset()
            return int(calendar.timegm(value.timetuple())) + (value.microsecond / 1000000.0)
        elif isinstance(value, datetime.time):
            seconds = value.hour * 3600 + value.minute * 60 + value.second
            if value.tzinfo:
                # DST 를 고려하지 않는다.
                seconds -= value.utcoffset().total_seconds()
            return seconds % 86400 + (value.microsecond / 1000000.0)
        elif isinstance(value, datetime.date):
            return calendar.timegm(value.timetuple())
        else:
            raise ValueError()

    def parse(self, value, property, context):
        if not isinstance(value, (integer_types, float)):
            raise ValueError()
        decoded = datetime.datetime.utcfromtimestamp(value)
        if issubclass(property, Time):
            return decoded.time().replace(tzinfo=timezone.utc)
        elif issubclass(property, Date):
            return decoded.date()
        return decoded.replace(tzinfo=timezone.utc)


@DateTimeFormat.register('iso')
class Iso8601Format(DateTimeFormat):
    TIME = r'(?P<H>\d{2}):(?P<M>\d{2})(:(?P<S>\d{2}(.\d*)?))?(?P<tzd>[+-](?P<tzh>\d{2}):(?P<tzm>\d{2})|Z)?'
    PATTERN1 = re.compile(r'(?P<Y>\d{4})(-(?P<m>\d{2})(-(?P<d>\d{2})([T ]' + TIME + r')?)?)?')
    PATTERN2 = re.compile(TIME)

    def format(self, value, property, context):
        if isinstance(value, (datetime.datetime, datetime.time)):
            if value.tzinfo and value.utcoffset() == datetime.timedelta():
                return value.replace(tzinfo=None).isoformat() + 'Z'
            return value.isoformat()
        elif isinstance(value, datetime.date):
            return value.isoformat()
        else:
            raise ValueError()

    def parse(self, value, property, context):
        value = value.strip()
        m = self.PATTERN1.match(value)
        if m is None:
            if issubclass(property, Time):
                m = self.PATTERN2.match(value)
                if m is None:
                    raise ValueError()
            else:
                raise ValueError()

        if m.groupdict().get('Y'):
            date = datetime.date(*map(lambda x: 1 if x is None else int(x), m.group('Y', 'm', 'd')))
        else:
            date = datetime.date.fromtimestamp(0)

        if issubclass(property, Date):
            return date

        if m.group('H'):
            hour, min, sec = m.group('H', 'M', 'S')
            hour = int(hour)
            min = int(min) if min else 0
            sec = float(sec) if sec else 0.0
            time = datetime.time(hour, min, int(sec), int((sec % 1.0) * 1000000))
        else:
            time = datetime.time()

        if m.group('tzd'):
            if m.group('tzd') in ('Z', '+00:00', '-00:00'):
                tzinfo = timezone.utc
            else:
                offset = int(m.group('tzh')) * 60 + int(m.group('tzm'))
                if m.group('tzd').startswith('-'):
                    offset = -offset
                tzinfo = timezone(datetime.timedelta(minutes=offset))
            time = time.replace(tzinfo=tzinfo)

        if issubclass(property, Time):
            return time

        return datetime.datetime.combine(date, time)


class Rfc2822Format(DateTimeFormat):
    WDAY = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
    MON = ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec')

    def _format(self, value, property, context, gmt):
        if isinstance(value, datetime.time):
            value = datetime.datetime.combine(datetime.date.fromtimestamp(0), value)
        elif not isinstance(value, datetime.datetime):
            value = datetime.datetime.combine(value, datetime.time())
        if gmt:
            if value.tzinfo and value.utcoffset() != datetime.timedelta():
                value = value.replace(tzinfo=timezone.utc) - value.utcoffset()
            format = '%s, %%d %s %%Y %%H:%%M:%%S GMT'
        else:
            TZ = (' %%z' if value.utcoffset() != datetime.timedelta() else ' GMT') if value.tzinfo else ''
            format = '%s, %%d %s %%Y %%H:%%M:%%S' + TZ
        format = format % (self.WDAY[value.weekday()], self.MON[value.month - 1])
        return value.strftime(format)

    def parse(self, value, property, context):
        dt = parsedate_to_datetime(value.strip())
        if issubclass(property, Date):
            return dt.date()
        elif issubclass(property, Time):
            return dt.timetz()
        return dt


@DateTimeFormat.register('email')
class HttpDateFormat(Rfc2822Format):
    def format(self, value, property, context):
        return self._format(value, property, context, False)


@DateTimeFormat.register('http')
class HttpDateFormat(Rfc2822Format):
    def format(self, value, property, context):
        return self._format(value, property, context, True)


class DateTimeBase(Property):
    class Options(Property.Options):
        format = 'iso'

    def _dump_(self, value, context):
        format = self.get_options().get('format', self.__class__.Options.format)
        formatter = DateTimeFormat.get_formatter(format)
        if formatter:
            return formatter.format(value, self.__class__, context)
        else:
            return value.strftime(format)

    def _load_(self, value, context):
        format = self.get_options().get('format', self.__class__.Options.format)
        formatter = DateTimeFormat.get_formatter(format)
        if formatter:
            return formatter.parse(value, self.__class__, context)
        else:
            dt = datetime.datetime.strptime(value, format)
            if isinstance(self, Time):
                return dt.time()
            elif isinstance(self, Date):
                return dt.date()
            return dt


class DateTime(DateTimeBase):
    """
    :py:class:`datetime.datetime` 값을 표현하는 :py:class:`Property`.

    :py:class:`datetime.datetime` 과 ``format`` 옵션이 지정하는 값들을 받아들이고,
    :py:class:`datetime.datetime` 으로 변환한다.

    시간대가 있는 값이 오는 경우 시간대를 변환 없이 보존한다. 시간대가 없는 값이 오는 경우 시간대를 부여하지는 않는다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    format
        날짜 형식을 지정한다. :py:meth:`datetime.datetime.strftime`, :py:meth:`datetime.datetime.strptime` 에서 사용되는 형식을 쓸 수 있다.

        이 외에 미리 준비되어 있는 형식의 이름을 줄 수도 있다. :py:class:`DateTimeFormat` 을 사용해서 커스텀 형식을 등록할 수 있는데,
        미리 준비되어 있는 형식은 다음과 같다.

        email
            `RFC 2822 <https://tools.ietf.org/html/rfc2822>`_ 형식.

            출력은 다음과 같은 형식을 취한다.

            - `Mon, 14 Mar 2016 07:19:36 GMT`
            - `Mon, 14 Mar 2016 16:19:36 +0900`

            시간대가 없는 값이 오면 시간대를 출력하지 않는다.

            입력에서 시간대는 생략될 수있다. 시간대가 없는 경우는 시간대가 없는 값을 만들고,
            있는 경우는 :py:class:`datetime.timezone` 으로 시간대를 설정한다.

            Since version 1.0.
        http
            `HTTP-date <https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html>`_ 형식.

            출력의 시간대를 다루는 방식을 제외하고는 ``email`` 형식과 동일하다.

            시간대가 없는 값이 오면 UTC 시간대가 있는 것으로 취급한다. 시간대가 있는 값이 오면 UTC 시간대로 변환한 후 출력한다.

            시간대 변환에는 DST 가 고려되지 않는다. DST 가 중요한 경우 미리 UTC 로 변환해서 값을 주는 것이 좋다.

            Since version 1.0.
        iso
            `ISO 8601 <https://www.w3.org/TR/NOTE-datetime>`_ 형식.

            `YYYY-MM-DDThh:mm:ss.sTZD` 형식의 문자열로 출력한다. TZD 는 시간대를 표시하는데 시간대가 없으면 표시하지 않고,
            UTC 의 경우는 `Z` 를 그외의 경우는 `+hh:mm` 이나 `-hh:mm` 형식으로 표현한다.

            입력은 다음과 같은 형식의 문자열을 받아들인다.

            - `YYYY`
            - `YYYY-MM`
            - `YYYY-MM-DD`
            - `YYYY-MM-DDThh:mmTZD`
            - `YYYY-MM-DDThh:mm:ssTZD`
            - `YYYY-MM-DDThh:mm:ss.sTZD`

            TZD 는 생략될 수 있다. TZD 가 없는 경우는 시간대가 없는 값을 만들고, 있는 경우는 :py:class:`datetime.timezone` 으로 시간대를
            설정한다.

            Since version 1.0.
        unix
            UTC 시간의 Unix Timestamp 를 :py:class:`float` 형식으로 표현한다.
            :py:func:`time.time` 과 같은 형식이다.

            시간대가 있는 값을 출력할 때는 UTC 로 변환한다.

            시간대 변환에는 DST 가 고려되지 않는다. DST 가 중요한 경우 미리 UTC 로 변환해서 값을 주는 것이 좋다.

            시간대가 없는 값을 출력할 때는 UTC 로 간주한다.

            Unix Timestamp 로 부터 :py:class:`datetime.datetime` 을 만들 때는, 시간대를 :py:attr:`datetime.timezone.utc` 로 설정한다.

            Since version 1.0.

        기본 값은 ``'iso'`` 다.

    Example

        .. literalinclude:: /../tests/ex/datetime.py

    Since version 1.0.
    """

    @classmethod
    def now(cls):
        """
        현재 시간을 나타내는 UTC 시간대의 :py:class:`datetime.datetime` 인스턴스를 만든다.

        Example

            .. literalinclude:: /../tests/ex/datetime_now.rst

        Since version 1.0.
        """
        return datetime.datetime.utcfromtimestamp(time.time()).replace(tzinfo=timezone.utc)

    def _load_(self, value, context):
        if isinstance(value, datetime.datetime):
            return value
        return super(DateTime, self)._load_(value, context)


class Time(DateTimeBase):
    """
    :py:class:`datetime.time` 값을 표현하는 :py:class:`Property`.

    :py:class:`datetime.time`, :py:class:`datetime.datetime` 과 ``format`` 옵션이 지정하는 값들을 받아들이고,
    :py:class:`datetime.time` 으로 변환한다.

    시간대가 있는 값이 오는 경우 시간대를 변환 없이 보존한다. 시간대가 없는 값이 오는 경우 시간대를 부여하지는 않는다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    format
        날짜 형식을 지정한다. :py:meth:`datetime.datetime.strftime`, :py:meth:`datetime.datetime.strptime` 에서 사용되는 형식을 쓸 수 있다.

        이 외에 미리 준비되어 있는 형식의 이름을 줄 수도 있다. :py:class:`DateTimeFormat` 을 사용해서 커스텀 형식을 등록할 수 있는데,
        미리 준비되어 있는 형식은 다음과 같다.

        email
            `RFC 2822 <https://tools.ietf.org/html/rfc2822>`_ 형식.

            출력할 때는 날짜 `1970년 1월 1일` 과 결합하여 :py:class:`DateTime` 의 ``email`` 형식 대로 출력한다.

            입력에서는 :py:class:`DateTime` 의 ``email`` 형식 대로 처리한 후 시간만 취한다.

            Since version 1.0.
        http
            `HTTP-date <https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html>`_ 형식.

            출력할 때는 날짜 `1970년 1월 1일` 과 결합하여 :py:class:`DateTime` 의 ``http`` 형식 대로 출력한다.

            입력에서는 :py:class:`DateTime` 의 ``http`` 형식 대로 처리한 후 시간만 취한다.

            Since version 1.0.
        iso
            `ISO 8601 <https://www.w3.org/TR/NOTE-datetime>`_ 형식.

            `hh:mm:ss.sTZD` 형식의 문자열로 출력한다. TZD 는 시간대를 표시하는데 시간대가 없으면 표시하지 않고,
            UTC 의 경우는 `Z` 를 그외의 경우는 `+hh:mm` 이나 `-hh:mm` 형식으로 표현한다.

            입력은 :py:class:`DateTime` 이 허락하는 모든 문자열을 받아들이고, 다음과 같은 형식을 추가로 받아들인다.

            - `hh:mmTZD`
            - `hh:mm:ssTZD`
            - `hh:mm:ss.sTZD`

            TZD 는 생략될 수 있다. TZD 가 없는 경우는 시간대가 없는 값을 만들고, 있는 경우는 :py:class:`datetime.timezone` 으로 시간대를
            설정한다.

            입력으로 오는 시간에 날짜가 포함되어 있더라도 에러로 취급되지 않고 시간만을 취한다.

            Since version 1.0.
        unix
            1970년 1월 1일 날짜의 해당 시간에 해당하는 Unix Timestamp 를 :py:class:`float` 형식으로 표현한다.
            :py:func:`time.time` 과 같은 형식이다.

            시간대가 있는 값을 출력할 때는 UTC 로 변환한다.

                .. warning::
                    시간대 변환에는 DST 가 고려되지 않는다. DST 가 중요한 경우 미리 UTC 로 변환해서 값을 주는 것이 좋다.

            시간대가 없는 값을 출력할 때는 UTC 로 간주한다.

            Unix Timestamp 로 부터 :py:class:`datetime.time` 을 만들 때는, 시간대를 :py:attr:`datetime.timezone.utc` 로 설정한다.

            시간대가 있는 :py:class:`datetime.time` 의 쓰임새는 극히 제한적이다.
            대부분의 경우 시간대가 없는 값을 사용하는데, 이 때 ``unix`` 형식은 본질적으로 시간대가 있는 형식이기 때문에 피하는 것이 좋다.

            입력으로 오는 값에서 시간만을 취한다.

            Since version 1.0.

        기본 값은 ``'iso'`` 다.

    Example

        .. literalinclude:: /../tests/ex/time.py

    Since version 1.0.
    """

    def _load_(self, value, context):
        if isinstance(value, datetime.time):
            return value
        elif isinstance(value, datetime.datetime):
            return value.timetz()
        return super(Time, self)._load_(value, context)


class Date(DateTimeBase):
    """
    :py:class:`datetime.date` 값을 표현하는 :py:class:`Property`.

    :py:class:`datetime.date`, :py:class:`datetime.datetime` 과 ``format`` 옵션이 지정하는 값들을 받아들이고,
    :py:class:`datetime.date` 로 변환한다.

    시간대가 있는 :py:class:`datetime.datetime` 이 올 경우 시간대는 무시된다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    format
        날짜 형식을 지정한다. :py:meth:`datetime.datetime.strftime`, :py:meth:`datetime.datetime.strptime` 에서 사용되는 형식을 쓸 수 있다.

        이 외에 미리 준비되어 있는 형식의 이름을 줄 수도 있다. :py:class:`DateTimeFormat` 을 사용해서 커스텀 형식을 등록할 수 있는데,
        미리 준비되어 있는 형식은 다음과 같다.

        email
            `RFC 2822 <https://tools.ietf.org/html/rfc2822>`_ 형식.

            출력할 때는 시간대 없는 시간 ``00:00:00` 과 결합하여 :py:class:`DateTime` 의 ``email`` 형식 대로 출력한다.

            입력에서는 :py:class:`DateTime` 의 ``email`` 형식 대로 처리한 후 날짜만 취한다.

            Since version 1.0.
        http
            `HTTP-date <https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html>`_ 형식.

            출력할 때는 시간대 없는 시간 ``00:00:00` 과 결합하여 :py:class:`DateTime` 의 ``http`` 형식 대로 출력한다.

            입력에서는 :py:class:`DateTime` 의 ``http`` 형식 대로 처리한 후 날짜만 취한다.

            Since version 1.0.
        iso
            `ISO 8601 <https://www.w3.org/TR/NOTE-datetime>`_ 형식.

            `YYYY-MM-DD` 형식의 문자열로 출력한다.
            입력은 :py:class:`DateTime` 이 허락하는 모든 문자열이 가능한데 날짜만을 취한다. 입력에 시간대가 지정되어 있더라도 무시된다.

            Since version 1.0.
        unix
            UTC 시간으로 해당 날짜의 0시 0분 0초 에 해당하는 Unix Timestamp 를 :py:class:`float` 형식으로 표현한다.
            :py:func:`time.time` 과 같은 형식이다.

            입력으로 오는 시간이 0시 0분 0초가 아니더라도 에러로 취급되지 않고 날짜만을 취한다.

            Since version 1.0.

        기본 값은 ``'iso'`` 다.

    Example

        .. literalinclude:: /../tests/ex/date.rst

    Since version 1.0.
    """

    def _load_(self, value, context):
        if isinstance(value, datetime.datetime):
            return value.date()
        elif isinstance(value, datetime.date):
            return value
        return super(Date, self)._load_(value, context)


class Duration(Property):
    """
    :py:class:`datetime.timedelta` 를 표현하는 :py:class:`Property`.

    다음과 같은 값들을 받아들여 :py:class:`decimal.Decimal` 형으로 변환한다.

    - :py:class:`datetime.timedelta`
    - 모든 정수형
    - :py:class:`float`

    :py:meth:`Entity.dump` 할 때 :py:class:`float` 를 출력한다.

    정수형이나 :py:class:`float` 로 표현될 때 값의 단위는 ``unit`` 옵션으로 지정된다.

    :py:class:`Property` 의 모든 옵션을 지원하고, 다음과 같은 추가 옵션을 제공한다.

    unit
        정수형이나 :py:class:`float` 로 표현될 때 값의 단위를 지정한다. 다음과 같은 값들을 사용할 수 있다.

        - ``'weeks'``
        - ``'days'``
        - ``'hours'``
        - ``'minutes'``
        - ``'seconds'``
        - ``'milliseconds'``
        - ``'microseconds'``

        기본값은 ``'seconds'``.

    Example

        .. literalinclude:: /../tests/ex/duration.py

    Since version 1.0.
    """

    class Options(Property.Options):
        unit = 'seconds'
        _unit = 1

        def __init__(self, **kwargs):
            super(Duration.Options, self).__init__(**kwargs)
            if self.unit != 'seconds':
                self._unit = datetime.timedelta(**{self.unit: 1}).total_seconds()

    def _dump_(self, value, context):
        unit = self.get_options().get('_unit', 1)
        return value.total_seconds() / unit

    def _load_(self, value, context):
        if isinstance(value, datetime.timedelta):
            return value
        if not isinstance(value, (integer_types, float)):
            raise ValueError()
        unit = self.get_options().get('unit', 'seconds')
        return datetime.timedelta(**{unit: value})


class IpAddress(Property):
    """
    IP 주소를 표현하는 :py:class:`Property`.

    문자열을 받아들여 :py:class:`ipaddress.IPv4Address` 또는 :py:class:`ipaddress.IPv6Address` 형으로 변환한다.

    :py:meth:`Entity.dump` 할 때 문자열을 출력한다.

    :py:class:`Property` 의 모든 옵션을 지원한다.

    Python 2 의 경우 `py2-ipaddress <https://pypi.python.org/pypi/py2-ipaddress>`_ 패키지를 설치하지 않으면,
    실제 값을 줄 때 :py:exc:`ImportError` 예외가 발생한다.

    Example

        .. literalinclude:: /../tests/ex/ipaddress.py

    Since version 1.0.
    """

    def _dump_(self, value, context):
        return str(value)

    def _load_(self, value, context):
        if not isinstance(value, text_types):
            raise ValueError()
        return ipaddress.ip_address(value)


class Ipv4Address(IpAddress):
    """
    IPv4 주소를 표현하는 :py:class:`Property`.

    문자열을 받아들여 :py:class:`ipaddress.IPv4Address` 형으로 변환한다.

    :py:meth:`Entity.dump` 할 때 문자열을 출력한다.

    :py:class:`IpAddress` 의 모든 옵션을 지원한다.

    Python 2 의 경우 `py2-ipaddress <https://pypi.python.org/pypi/py2-ipaddress>`_ 패키지를 설치하지 않으면,
    실제 값을 줄 때 :py:exc:`ImportError` 예외가 발생한다.

    Example

        .. literalinclude:: /../tests/ex/ipv4address.py

    Since version 1.0.
    """

    def _load_(self, value, context):
        if not isinstance(value, text_types):
            raise ValueError()
        return ipaddress.IPv4Address(value)


class Ipv6Address(IpAddress):
    """
    IPv6 주소를 표현하는 :py:class:`Property`.

    문자열을 받아들여 :py:class:`ipaddress.IPv6Address` 형으로 변환한다.

    :py:meth:`Entity.dump` 할 때 문자열을 출력한다.

    :py:class:`IpAddress` 의 모든 옵션을 지원한다.

    Python 2 의 경우 `py2-ipaddress <https://pypi.python.org/pypi/py2-ipaddress>`_ 패키지를 설치하지 않으면,
    실제 값을 줄 때 :py:exc:`ImportError` 예외가 발생한다.

    Example

        .. literalinclude:: /../tests/ex/ipv6address.py

    Since version 1.0.
    """

    def _load_(self, value, context):
        if not isinstance(value, text_types):
            raise ValueError()
        return ipaddress.IPv6Address(value)


__all__ = [
    'Primitive',
    'String',
    'Unicode',
    'Bytes',
    'Boolean',
    'Number',
    'Integer',
    'Float',
    'JsonObject',
    'JsonArray',
    'Decimal',
    'Complex',
    'Uuid',
    'DateTimeFormat',
    'DateTime',
    'Date',
    'Time',
    'Duration',
    'IpAddress',
    'Ipv4Address',
    'Ipv6Address',
]
